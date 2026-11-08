"""Paragraph and staging contracts; byte fidelity, not semantic certification."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_guard.py'
spec = importlib.util.spec_from_file_location('paragraph_guard', SCRIPT)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class ParagraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def source(self, content, name='draft.txt'):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode('utf-8'))
        return g.snapshot(self.root, [name])

    def record(self, manifest):
        # Synthetic plain-text mechanics only, never attests a real manuscript.
        return {'coverage': {
            'inventory_scope': 'Synthetic mechanics fixture only',
            'rendered': 'not_applicable: plain text fixture',
            'evidence': 'not_applicable: no factual correction',
            'derived': 'not_applicable: no publication copies'},
            'rows': [{'id': u['id'], 'quote': u['quote'], 'verdict': 'ok',
                      'assessment': 'Synthetic fixture checks exact inventory and staging only.'}
                     for u in manifest['units']],
            'edits': [], 'required_checks': []}

    def test_equivalent_line_endings_keep_two_paragraphs(self):
        for end in ['\n', '\r\n', '\r']:
            with self.subTest(end=repr(end)):
                source = end.join(['First line.', 'Wrapped line.', '', 'Second paragraph.', ''])
                manifest = self.source(source)
                self.assertEqual([u['quote'] for u in manifest['units']],
                                 ['First line.' + end + 'Wrapped line.', 'Second paragraph.'])
                for u in manifest['units']:
                    self.assertEqual(source[u['start']:u['end']], u['quote'])

    def test_mixed_endings_and_whitespace_separators(self):
        source = '\r\n\t\rAlpha.\rBeta.\r\n \t\nGamma.\nDelta.\r\n\r\n'
        manifest = self.source(source)
        self.assertEqual([u['quote'] for u in manifest['units']],
                         ['Alpha.\rBeta.', 'Gamma.\nDelta.'])

    def test_crlf_blank_line_is_not_split_into_two_breaks(self):
        manifest = self.source('A.\r\nB.\r\n\r\nC.\r\nD.')
        self.assertEqual([u['quote'] for u in manifest['units']], ['A.\r\nB.', 'C.\r\nD.'])

    def test_blank_input_rejected_for_all_endings(self):
        for source in ['', '\ufeff', ' \t\r', '\r\n \t\n\r']:
            with self.subTest(source=repr(source)), self.assertRaisesRegex(g.Invalid, 'no nonempty'):
                self.source(source)

    def test_bom_and_mixed_endings_stage_byte_for_byte(self):
        source = '\ufeffHeading.\rWrapped.\r\n\t\nSecond paragraph.\r'
        manifest = self.source(source)
        original = (self.root / 'draft.txt').read_bytes()
        staged = self.root / 'staged'
        g.stage(self.root, manifest, g.validate(self.root, manifest, self.record(manifest)), staged)
        self.assertEqual((staged / 'draft.txt').read_bytes(), original)
        self.assertEqual((self.root / 'draft.txt').read_bytes(), original)

    def test_minimal_edit_after_cr_uses_original_offset(self):
        source = 'First.\rWrapped.\r\rThe report is clear.\r'
        manifest = self.source(source)
        record = self.record(manifest)
        start = source.index('clear')
        record['edits'] = [{'id': 'E1', 'source': 'draft.txt',
            'source_sha256': manifest['sources']['draft.txt']['sha256'],
            'start': start, 'end': start + len('clear'), 'current': 'clear', 'proposed': 'readable',
            'reason': 'Synthetic offset preservation check.', 'declarations': [],
            'meaning': {'status': 'preserved', 'assessment': 'Synthetic lexical change; same report.'},
            'evidence': []}]
        g.stage(self.root, manifest, g.validate(self.root, manifest, record), self.root / 'out')
        self.assertEqual((self.root / 'out/draft.txt').read_bytes(), source.replace('clear', 'readable').encode())

    def test_old_cr_inventory_requires_new_attestations(self):
        manifest = self.source('First.\rWrapped.\r\rSecond.')
        record = self.record(manifest)
        # Legacy CR-only inventory split the wrapped paragraph into line units.
        manifest['units'] = [
            {'id': 'U00001', 'source': 'draft.txt', 'start': 0, 'end': 6, 'quote': 'First.'},
            {'id': 'U00002', 'source': 'draft.txt', 'start': 7, 'end': 15, 'quote': 'Wrapped.'},
            {'id': 'U00003', 'source': 'draft.txt', 'start': 17, 'end': 24, 'quote': 'Second.'}]
        with self.assertRaisesRegex(g.Invalid, 'inventory mismatch'):
            g.validate(self.root, manifest, record)

    def test_cr_only_evidence_keeps_editor_line_numbers(self):
        source = 'The recorded label is blue.\r'
        self.source(source)
        (self.root / 'facts.txt').write_bytes(b'First fact.\rThe recorded label is green.\r')
        manifest = g.snapshot(self.root, ['draft.txt'], evidence=['facts.txt'])
        self.assertEqual(len(manifest['units']), 1)
        record = self.record(manifest)
        start = source.index('blue')
        support = {'source': 'facts.txt', 'sha256': manifest['sources']['facts.txt']['sha256'],
                   'line_start': 2, 'line_end': 2, 'quote': 'The recorded label is green.',
                   'relation': 'supports', 'assessment': 'Same synthetic recorded label.'}
        record['edits'] = [{'id': 'E1', 'source': 'draft.txt',
            'source_sha256': manifest['sources']['draft.txt']['sha256'],
            'start': start, 'end': start + 4, 'current': 'blue', 'proposed': 'green',
            'reason': 'Match the synthetic observation.', 'declarations': ['term'],
            'meaning': {'status': 'changed', 'assessment': 'Changes the reported label to the cited observation.'},
            'evidence': [support]}]
        self.assertEqual(g.validate(self.root, manifest, record)['draft.txt'], source.replace('blue', 'green'))
        support.update(line_start=1, line_end=1)
        with self.assertRaisesRegex(g.Invalid, 'specified range'):
            g.validate(self.root, manifest, record)

    def test_reserved_root_manifest_refused_before_stage_creation(self):
        for i, name in enumerate(['staged_manifest.json', 'Staged_Manifest.JSON',
                                  'staged_manifest.json/note.txt']):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                self.root = Path(folder).resolve()
                manifest = self.source('A sound result.', name)
                record = self.record(manifest)
                target = self.root / f'new{i}' / 'out'
                with self.assertRaisesRegex(g.Invalid, 'reserved root path'):
                    g.stage(self.root, manifest, g.validate(self.root, manifest, record), target)
                self.assertFalse(target.parent.exists())
                self.assertEqual(list(self.root.rglob('.audit-stage-*')), [])

    def test_nested_manifest_basename_stages_normally(self):
        manifest = self.source('A sound result.', 'notes/staged_manifest.json')
        out = self.root / 'out'
        g.stage(self.root, manifest, g.validate(self.root, manifest, self.record(manifest)), out)
        self.assertEqual((out / 'notes/staged_manifest.json').read_text(), 'A sound result.')
        self.assertTrue((out / 'staged_manifest.json').is_file())

    def test_nonwhitespace_coverage_with_mixed_breaks(self):
        source = '\ufeffTitle.\r\n\rFirst\rwrapped.\n \t\rLast.\r\n'
        manifest = self.source(source)
        covered = {i for u in manifest['units'] for i in range(u['start'], u['end'])}
        self.assertTrue(all(i in covered for i, c in enumerate(source)
                            if not c.isspace() and c != '\ufeff'))

    def test_cli_cr_snapshot_check_and_stage(self):
        original = b'First.\rWrapped.\r\rSecond.\r'
        (self.root / 'draft.txt').write_bytes(original)
        def command(*args):
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), *args],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)
        command('snapshot', '--root', str(self.root), '--files', 'draft.txt',
                '--out', str(self.root / 'snapshot.json'))
        manifest = json.loads((self.root / 'snapshot.json').read_bytes())
        self.assertEqual(len(manifest['units']), 2)
        record = self.record(manifest)
        record['snapshot_sha256'] = g.digest((self.root / 'snapshot.json').read_bytes())
        (self.root / 'review.json').write_text(json.dumps(record), encoding='utf-8')
        common = ('--root', str(self.root), '--snapshot', str(self.root / 'snapshot.json'),
                  '--record', str(self.root / 'review.json'))
        self.assertFalse(command('check', *common)['semantic_truth_verified_by_script'])
        command('stage', *common, '--out', str(self.root / 'stage'))
        self.assertEqual((self.root / 'stage/draft.txt').read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
