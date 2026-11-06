"""Regression cases for contextual token checks, including sound controls."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('context_guard', ROOT/'scripts/audit_guard.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def fixture(self, source):
        self.source = source
        (self.root/'paper.md').write_bytes(source.encode('utf-8'))
        (self.root/'facts.txt').write_bytes(b'Correct measured latency: 12 s.\n')
        self.manifest = g.snapshot(self.root, ['paper.md'], evidence=['facts.txt'])
        self.record = {
            'coverage': dict(inventory_scope='Synthetic paper.md', rendered='not_applicable: plain text',
                             evidence='Synthetic facts.txt', derived='not_applicable'),
            'rows': [dict(id=u['id'], quote=u['quote'], verdict='ok',
                          assessment='Structural test fixture, not an editorial-quality claim.')
                     for u in self.manifest['units']],
            'edits': [], 'required_checks': []}

    def edit(self, old, new, **updates):
        start = self.source.index(old)
        value = dict(id=f'E{len(self.record["edits"])+1}', source='paper.md',
                     source_sha256=self.manifest['sources']['paper.md']['sha256'],
                     start=start, end=start+len(old), current=old, proposed=new,
                     reason='Focused test case', declarations=[],
                     meaning=dict(status='preserved', assessment='Explicit reader assessment required.'), evidence=[])
        value.update(updates)
        self.record['edits'].append(value)
        return value

    def check(self):
        return g.validate(self.root, self.manifest, self.record)

    def reject(self, message):
        with self.assertRaisesRegex(g.Invalid, message):
            self.check()

    def test_minimal_unit_change_requires_declaration(self):
        for source, old, new in [('Latency is 12 ms.', 'ms', 's'),
                                 ('Latency is 12ms.', 'ms', 'us'),
                                 ('Latency is 12 µs.', 'µs', 'ms'),
                                 ('Latency is 12 μs.', 'μs', 's'),
                                 ('Latency is 12 ms.', 'm', 'µ')]:
            with self.subTest(source=source, old=old, new=new):
                self.fixture(source)
                self.edit(old, new)
                self.reject('undeclared unit')

    def test_declared_unit_change_still_requires_support(self):
        self.fixture('Latency is 12 ms.')
        self.edit('ms', 's', declarations=['unit'])
        self.reject('lacks mapped support')

    def test_supported_minimal_unit_change_stages_exact_bytes(self):
        self.fixture('\ufeffLatency is 12 ms.\r\n\r\nThe estimator\u2019s bound holds.\r\n')
        self.edit('ms', 's', declarations=['unit'], meaning=dict(status='changed', assessment='Correct the unit from measured evidence.'),
                  evidence=[dict(source='facts.txt', sha256=self.manifest['sources']['facts.txt']['sha256'],
                                 line_start=1, line_end=1, quote='Correct measured latency: 12 s.',
                                 relation='supports', assessment='Same measurement and value; corrected time unit.')])
        g.stage(self.root, self.manifest, self.check(), self.root/'out')
        self.assertEqual((self.root/'out/paper.md').read_bytes(), self.source.replace('12 ms', '12 s').encode('utf-8'))
        self.assertEqual((self.root/'paper.md').read_bytes(), self.source.encode('utf-8'))

    def test_contraction_fragment_removal_requires_strength(self):
        for word, fragment in [("doesn't", "n't"), ("doesn’t", 'n’t'),
                                ("can't", "'t"), ("cannot", 'not')]:
            with self.subTest(word=word):
                self.fixture(f'The server {word} reject packets.')
                self.edit(fragment, '')
                self.reject('undeclared strength')

    def test_negation_removal_needs_support_after_declaration(self):
        self.fixture("The server doesn't reject packets.")
        self.edit("n't", '', declarations=['strength'])
        self.reject('lacks mapped support')

    def test_split_number_and_citation_changes_are_detected(self):
        for source, old, new, field in [('There are 123 records.', '2', '9', 'number'),
                                         (r'The bound follows \cite{one}.', 'one', 'two', 'citation')]:
            with self.subTest(field=field):
                self.fixture(source)
                self.edit(old, new)
                self.reject('undeclared '+field)

    def test_strength_capitalization_is_not_a_strength_change(self):
        self.fixture('Some packets may arrive.')
        self.edit('Some', 'some')
        self.assertEqual(self.check()['paper.md'], 'some packets may arrive.')

    def test_contraction_apostrophe_typography_is_not_strength_change(self):
        self.fixture("The server doesn't reject packets.")
        self.edit("'", '’')
        self.assertEqual(self.check()['paper.md'], 'The server doesn’t reject packets.')

    def test_order_only_requires_explicit_reader_review(self):
        self.fixture('We can, without retraining, adapt.')
        self.edit(self.source, 'Without retraining, we can adapt.')
        self.reject('undeclared strength')

    def test_reviewed_meaning_preserving_order_needs_no_scientific_support(self):
        self.fixture('We can, without retraining, adapt.')
        self.edit(self.source, 'Without retraining, we can adapt.', declarations=['strength'],
                  meaning=dict(status='preserved', assessment='Same ability, actor, action and no-retraining condition; only the adjunct moved.'))
        self.assertEqual(self.check()['paper.md'], 'Without retraining, we can adapt.')

    def test_changed_meaning_order_still_needs_support(self):
        self.fixture('Not all packets arrive.')
        self.edit(self.source, 'All packets do not arrive.', declarations=['strength'],
                  meaning=dict(status='changed', assessment='Negation scope is changed and needs factual evidence.'))
        self.reject('lacks mapped support')

    def test_negation_quantifier_order_is_not_silently_ignored(self):
        self.fixture('Not all packets arrive.')
        self.edit(self.source, 'All packets do not arrive.')
        self.reject('undeclared strength')

    def test_new_modality_cannot_use_order_only_exemption(self):
        self.fixture('The server may reject packets.')
        self.edit('may', 'must', declarations=['strength'])
        self.reject('lacks mapped support')

    def test_declared_unmonitored_strength_change_still_needs_support(self):
        for source, old, new in [('This outcome is likely.', 'likely', 'certain'),
                                 ('The result indicates improvement.', 'indicates', 'demonstrates')]:
            with self.subTest(source=source):
                self.fixture(source)
                self.edit(old, new, declarations=['strength'])
                self.reject('lacks mapped support')

    def test_unrelated_case_change_does_not_hide_number_change(self):
        self.fixture('Some packets number 12.')
        self.edit(self.source, 'some packets number 13.')
        self.reject('undeclared number')

    def test_two_edits_creating_unit_are_checked_in_combined_context(self):
        self.fixture('Latency is 12 ab.')
        start = self.source.rindex('a')
        self.edit('a', 'm', start=start, end=start+1)
        self.edit('b', 's')
        self.reject('undeclared unit')

    def test_two_edit_slices_do_not_silently_form_negation(self):
        self.fixture('We caXY proceed.')
        self.edit('X', 'n')
        self.edit('Y', 'not')
        self.reject('undeclared strength')

    def test_whole_span_and_minimal_span_require_same_unit_declaration(self):
        self.fixture('Latency is 12 ms.')
        self.edit('12 ms', '12 s')
        self.reject('undeclared unit')
        self.record['edits'] = []
        self.edit('ms', 's')
        self.reject('undeclared unit')

    def test_failed_context_check_leaves_no_staged_output(self):
        self.fixture('Latency is 12 ms.')
        self.edit('ms', 's')
        with self.assertRaises(g.Invalid):
            g.stage(self.root, self.manifest, self.check(), self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_documented_false_preserved_assessment_remains_a_limit(self):
        self.fixture('Not all packets arrive.')
        self.edit(self.source, 'All packets do not arrive.', declarations=['strength'],
                  meaning=dict(status='preserved', assessment='Deliberately false scope attestation for a documented limitation test.'))
        self.assertTrue(self.check())

    def test_real_cli_check_and_stage_with_reordered_qualifier(self):
        self.fixture('We can, without retraining, adapt.\r\n')
        self.edit(self.source.strip(), 'Without retraining, we can adapt.', declarations=['strength'],
                  meaning=dict(status='preserved', assessment='The same actor can adapt under the same no-retraining condition.'))
        snap, record = self.root/'snapshot.json', self.root/'review.json'
        g.save_new(snap, self.manifest)
        self.record['snapshot_sha256'] = g.digest(snap.read_bytes())
        g.save_new(record, self.record)
        for command in ['check', 'stage']:
            args = [sys.executable, '-B', str(ROOT/'scripts/audit_guard.py'), command, '--root', str(self.root),
                    '--snapshot', str(snap), '--record', str(record)]
            if command == 'stage':
                args.extend(['--out', str(self.root/'cli-out')])
            run = subprocess.run(args, text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
        self.assertEqual((self.root/'cli-out/paper.md').read_bytes(), b'Without retraining, we can adapt.\r\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
