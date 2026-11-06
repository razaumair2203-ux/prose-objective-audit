"""Frozen UTF-8 audit records and all-or-nothing scratch staging; no semantic proof."""
from pathlib import Path, PurePosixPath
from collections import Counter
import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile


class Invalid(ValueError):
    pass


def require(test, message):
    if not test:
        raise Invalid(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def decode_utf8(raw, name):
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError as error:
        raise Invalid(f'{name}: input must be UTF-8 (a UTF-8 BOM is allowed)') from error


def text(path):
    return decode_utf8(path.read_bytes(), str(path))


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def scoped(root, name):
    require(isinstance(name, str) and bool(name), 'missing relative path')
    p = PurePosixPath(name.replace('\\', '/'))
    require(not p.is_absolute() and ':' not in name and '..' not in p.parts, 'unsafe path: ' + name)
    require(p.parts and not any(part.lower() == '.git' for part in p.parts), 'invalid path: ' + name)
    result = root.joinpath(*p.parts)
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        require(not cursor.is_symlink() and not cursor.is_junction(), 'linked path: ' + name)
    require(result.resolve().is_relative_to(root), 'path escapes root: ' + name)
    return result


def canonical(root, path):
    resolved = scoped(root, path)
    return resolved.relative_to(root).as_posix()


def save_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def snapshot(root, files, artifacts=(), generated=(), evidence=()):
    records, units = {}, []
    generated = {canonical(root, x) for x in generated}
    names = [canonical(root, x) for x in [*files, *evidence, *artifacts]]
    require(len(set(x.casefold() for x in names)) == len(names), 'duplicate/case-colliding input paths')
    require(generated <= set(names[:len(files)]), 'generated path is not a text input')
    for i, name in enumerate(names):
        p = scoped(root, name)
        require(p.is_file(), 'missing input: ' + name)
        raw = p.read_bytes()
        kind = 'text' if i < len(files) else 'evidence' if i < len(files)+len(evidence) else 'artifact'
        item = {'sha256': digest(raw), 'kind': kind, 'generated': name in generated}
        records[name] = item
        if item['kind'] == 'artifact':
            continue
        content = decode_utf8(raw, name)
        if item['kind'] == 'evidence':
            continue
        for match in re.finditer(r'[^\r\n]+(?:\r?\n(?![ \t]*\r?\n)[^\r\n]+)*', content):
            if not match.group().strip('\ufeff \t'):
                continue
            units.append({'id': f'U{len(units)+1:05d}', 'source': name, 'start': match.start(), 'end': match.end(), 'quote': match.group()})
    require(bool(units), 'no nonempty text units')
    return {'version': 1, 'sources': records, 'units': units}


VALUE = r'[-+\u2212]?(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?'
NUMBER = re.compile(rf'(?<![\w.]){VALUE}(?:%|(?!\d|\.\d))')
CITE = re.compile(r'\\(?:[A-Za-z]*cite[A-Za-z]*|ref|label)\*?(?:\[[^\]]*\])*\{[^}]*\}|\[@[^\]]+\]')
STRENGTH = re.compile(r"\b\w+n['\u2019]t\b|\b(?:may|might|can|cannot|could|always|never|not|no|none|neither|without|all|some|only|every|must|shall|proves?|suggests?|causes?|associated|at most|at least)\b", re.I)
LONG_UNIT = r'seconds?|minutes?|hours?|Hz|kHz|MHz|bytes?|kB|MB|Gbps|Mbps|percent(?:age points?)?'
UNIT = re.compile(rf'(?:(?<![\w.]){VALUE}[ \t]*|\b(?=(?:{LONG_UNIT})\b))(?P<unit>ns|us|[\u00b5\u03bc]s|ms|s|{LONG_UNIT})\b')
GENERATED = re.compile(r'(?im)^[ \t]*(?:%|#|//|;|<!--)[ \t]*(?:(?:this file (?:is|was)[ \t]+)?(?:auto(?:matically)?[- ]?)?generated[ \t]+(?:by|from)\b|do not edit\b|built by[ \t]+\S+\.(?:py|sh|r)\b)')


def changed_tokens(a, b, pattern):
    return pattern.findall(a) != pattern.findall(b)


def strength_tokens(content):
    return [token.casefold().replace('\u2019', "'") for token in STRENGTH.findall(content)]


def check_edit_tokens(before, after, edit):
    # Inspect complete context: a span may contain only a unit, citation key,
    # digit, or contraction suffix. Token order remains significant.
    declarations = edit['declarations']
    for field, pattern in [('number', NUMBER), ('citation', CITE), ('unit', UNIT)]:
        if changed_tokens(before, after, pattern):
            require(field in declarations, 'undeclared ' + field + ' change: ' + edit['id'])
    old_strength, new_strength = strength_tokens(before), strength_tokens(after)
    if old_strength != new_strength:
        require('strength' in declarations, 'undeclared strength change: ' + edit['id'])
    # An order-only alert still requires an explicit reader assessment. It
    # does not, by itself, establish a changed scientific claim. Never ignore
    # order: "not all" and "all ... not" can have different scope.
    reviewed_reordering = (old_strength != new_strength
                          and edit['meaning']['status'] == 'preserved'
                          and Counter(old_strength) == Counter(new_strength))
    needs_support = (edit['meaning']['status'] == 'changed'
                     or any(d in declarations for d in ['number', 'unit', 'scope', 'citation'])
                     or ('strength' in declarations and not reviewed_reordering))
    if needs_support:
        require(any(ev.get('relation') == 'supports' for ev in edit.get('evidence', [])),
                'meaning change lacks mapped support evidence')


def validate(root, manifest, record):
    require(manifest.get('version') == 1, 'unknown snapshot version')
    sources = manifest.get('sources')
    require(isinstance(sources, dict) and bool(sources), 'missing sources')
    content = {}
    for name, item in sources.items():
        p = scoped(root, name)
        require(p.is_file(), 'missing source: ' + name)
        raw = p.read_bytes()
        require(digest(raw) == item.get('sha256'), 'stale source: ' + name)
        require(item.get('kind') in ('text', 'evidence', 'artifact'), 'unknown source kind')
        if item['kind'] in ('text', 'evidence'):
            content[name] = decode_utf8(raw, name)
    # Regenerate text inventory to detect incomplete/tampered snapshot units.
    audited = [x for x in sources if sources[x]['kind'] == 'text']
    rebuilt = snapshot(root, audited, [x for x in sources if sources[x]['kind'] == 'artifact'], [x for x in audited if sources[x].get('generated')], evidence=[x for x in sources if sources[x]['kind'] == 'evidence'])
    require(manifest.get('units') == rebuilt['units'], 'snapshot unit inventory mismatch')
    coverage = record.get('coverage', {})
    require(isinstance(coverage, dict) and all(nonempty(coverage.get(x)) for x in ['inventory_scope', 'rendered', 'evidence', 'derived']), 'missing explicit coverage dimensions')
    rows = record.get('rows')
    require(isinstance(rows, list), 'missing rows')
    expected = {u['id']: u for u in manifest['units']}
    ids = [r.get('id') for r in rows]
    require(len(set(ids)) == len(ids), 'duplicate unit row')
    require(set(ids) == set(expected), 'missing or unknown unit row')
    for r in rows:
        require(r.get('quote') == expected[r['id']]['quote'], 'unit quote mismatch: ' + r['id'])
        require(r.get('verdict') in ('ok', 'finding', 'question'), 'invalid row verdict')
        require(nonempty(r.get('assessment')), 'missing unit assessment')
    checks = record.get('required_checks', [])
    require(isinstance(checks, list), 'invalid required checks')
    check_names = []
    for c in checks:
        require(nonempty(c.get('name')), 'unnamed required check')
        check_names.append(c['name'])
        require(c.get('status') in ('passed', 'not_applicable') and nonempty(c.get('receipt')), 'required check not verified: ' + c['name'])
    require(len(set(check_names)) == len(check_names), 'duplicate required check')
    edits = record.get('edits', [])
    require(isinstance(edits, list), 'invalid edits')
    edit_ids, spans = set(), {}
    for e in edits:
        require(nonempty(e.get('id')) and e['id'] not in edit_ids, 'missing or duplicate edit id')
        edit_ids.add(e['id'])
        name = e.get('source')
        require(name in audited, 'edit source must be frozen audited text')
        require(e.get('source_sha256') == sources[name]['sha256'], 'edit source hash mismatch')
        require(not sources[name].get('generated') and not GENERATED.search(content[name].lstrip('\ufeff')[:1000]), 'generated source: ' + name)
        start, end = e.get('start'), e.get('end')
        require(type(start) is int and type(end) is int and 0 <= start < end <= len(content[name]), 'invalid edit span')
        require(nonempty(e.get('current')) and content[name][start:end] == e['current'], 'edit quote/span mismatch')
        require(isinstance(e.get('proposed'), str) and e['proposed'] != e['current'], 'missing or unchanged replacement')
        require(nonempty(e.get('reason')), 'missing edit rationale')
        meaning = e.get('meaning', {})
        require(meaning.get('status') in ('preserved', 'changed') and nonempty(meaning.get('assessment')), 'missing semantic review attestation')
        declarations = e.get('declarations')
        require(isinstance(declarations, list) and all(x in ['number', 'unit', 'citation', 'scope', 'strength', 'term'] for x in declarations), 'invalid declarations')
        evidence = e.get('evidence', [])
        require(isinstance(evidence, list), 'invalid evidence list')
        for ev in evidence:
            src = ev.get('source')
            require(src in content, 'evidence source must be frozen text')
            require(ev.get('sha256') == sources[src]['sha256'], 'evidence hash mismatch')
            a, b = ev.get('line_start'), ev.get('line_end')
            lines = re.findall(r'[^\r\n]*(?:\r\n|\r|\n|$)', content[src])
            if lines and lines[-1] == '':
                lines.pop()
            require(type(a) is int and type(b) is int and 1 <= a <= b <= len(lines), 'evidence line range invalid')
            require(nonempty(ev.get('quote')) and ev['quote'] in ''.join(lines[a-1:b]), 'evidence quote not in specified range')
            require(ev.get('relation') in ('supports', 'contradicts', 'context') and nonempty(ev.get('assessment')), 'missing evidence support assessment')
        spans.setdefault(name, []).append((start, end, e))
    for name, entries in spans.items():
        entries.sort(key=lambda s: s[0])
        require(all(a[1] <= b[0] for a, b in zip(entries, entries[1:])), 'overlapping edits: ' + name)
    proposed = dict(content)
    for name, entries in spans.items():
        for start, end, e in reversed(entries):
            before = proposed[name]
            after = before[:start] + e['proposed'] + before[end:]
            # Right-to-left application preserves original offsets and checks
            # neighboring edits together, including newly formed tokens.
            check_edit_tokens(before, after, e)
            proposed[name] = after
    return proposed


def read_record(root, snap_path, record_path):
    raw = snap_path.read_bytes()
    manifest = json.loads(raw)
    record = json.loads(record_path.read_bytes())
    require(record.get('snapshot_sha256') == digest(raw), 'review is not bound to this snapshot')
    proposed = validate(root, manifest, record)
    return manifest, record, proposed


def stage(root, manifest, proposed, out):
    out = out.absolute()
    require(out.resolve().is_relative_to(root), 'scratch output must be inside project root')
    relative = out.relative_to(root).as_posix()
    out = scoped(root, relative)
    require(out != root and not out.exists(), 'scratch output already exists or is root')
    require(all(not scoped(root, name).is_relative_to(out) for name in manifest['sources']), 'scratch output contains input')
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.audit-stage-', dir=out.parent))
    try:
        hashes = {}
        for name, item in manifest['sources'].items():
            raw = proposed[name].encode('utf-8') if name in proposed else scoped(root, name).read_bytes()
            # Source edits during validation/staging must not be silently accepted.
            require(digest(scoped(root, name).read_bytes()) == item['sha256'], 'source changed during staging: ' + name)
            dst = temporary / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(raw)
            hashes[name] = digest(raw)
        save_new(temporary/'staged_manifest.json', {'source_manifest': manifest, 'staged_sha256': hashes, 'semantic_truth_verified_by_script': False})
        require(all(digest((temporary/name).read_bytes()) == sha for name, sha in hashes.items()), 'staged byte verification failed')
        require(not out.exists(), 'scratch output appeared during staging')
        os.rename(temporary, out)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    snap = sub.add_parser('snapshot')
    snap.add_argument('--root', required=True, type=Path)
    snap.add_argument('--files', required=True, nargs='+')
    snap.add_argument('--artifacts', nargs='*', default=[])
    snap.add_argument('--evidence', nargs='*', default=[])
    snap.add_argument('--generated', nargs='*', default=[])
    snap.add_argument('--out', required=True, type=Path)
    for name in ['check', 'stage']:
        p = sub.add_parser(name)
        p.add_argument('--root', required=True, type=Path)
        p.add_argument('--snapshot', required=True, type=Path)
        p.add_argument('--record', required=True, type=Path)
        if name == 'stage':
            p.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        if args.cmd == 'snapshot':
            data = snapshot(root, args.files, args.artifacts, args.generated, args.evidence)
            save_new(args.out, data)
            print(json.dumps({'structural_snapshot': 'created', 'units': len(data['units']), 'semantic_truth_verified_by_script': False}))
        else:
            manifest, record, proposed = read_record(root, args.snapshot, args.record)
            if args.cmd == 'stage':
                stage(root, manifest, proposed, args.out)
            print(json.dumps({'structure': 'valid', 'units_attested': len(record['rows']), 'edits': len(record.get('edits', [])), 'semantic_truth_verified_by_script': False, 'rendered_status_reported_by_reader': record['coverage']['rendered']}))
    except (Invalid, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(json.dumps({'structure': 'invalid', 'error': str(error), 'semantic_truth_verified_by_script': False}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
