from pathlib import Path
import copy
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guard', ROOT/'scripts/audit_guard.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.source = 'The estimator may reduce error by 12 ms.\r\n\r\nThe sample contains 14 records.\r\n'
        self.write('doc.txt', self.source)
        self.write('facts.txt', 'The estimator reduced error by 14 ms in one simulation.\nThe field effect is unknown.\n')
        self.manifest = g.snapshot(self.root, ['doc.txt', 'facts.txt'])
        self.record = {'coverage':dict(inventory_scope='doc.txt and facts.txt',rendered='not_checked: text only',evidence='read facts.txt',derived='not_applicable'),
                       'rows':[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='Human attestation; not comprehension proof') for u in self.manifest['units']],
                       'edits':[], 'required_checks':[]}

    def write(self, name, value):
        p = self.root/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(value.encode('utf-8'))

    def edit(self, old='reduce error', new='lower error', **updates):
        start = self.source.index(old)
        e = dict(id='E1',source='doc.txt',source_sha256=self.manifest['sources']['doc.txt']['sha256'],start=start,end=start+len(old),current=old,proposed=new,reason='Clarify wording',declarations=[],meaning=dict(status='preserved',assessment='Same actor, outcome, scope and units'),evidence=[])
        e.update(updates)
        self.record['edits'].append(e)
        return e

    def evidence(self):
        return dict(source='facts.txt',sha256=self.manifest['sources']['facts.txt']['sha256'],line_start=1,line_end=1,quote='The estimator reduced error by 14 ms in one simulation.',relation='supports',assessment='Same estimator, unit and trial; supports corrected simulation value only')

    def check(self):
        return g.validate(self.root,self.manifest,self.record)

    def reject(self, fragment):
        with self.assertRaisesRegex(g.Invalid, fragment):
            self.check()

    def test_sound_text_empty_edits_valid(self):
        self.assertEqual(self.check()['doc.txt'],self.source)

    def test_legitimate_clarity_preserves_source_and_crlf(self):
        self.edit()
        proposed = self.check()
        out=self.root/'stage'
        g.stage(self.root,self.manifest,proposed,out)
        self.assertEqual((self.root/'doc.txt').read_bytes(),self.source.encode())
        self.assertEqual((out/'doc.txt').read_bytes(),self.source.replace('reduce error','lower error').encode())

    def test_supported_number_change_valid(self):
        self.edit('12','14',declarations=['number'],meaning=dict(status='changed',assessment='Correct simulation value with exact evidence'),evidence=[self.evidence()])
        self.assertIn('14 ms',self.check()['doc.txt'])

    def test_stale_input_rejected(self):
        self.write('doc.txt',self.source+'New statement.')
        self.reject('stale source')

    def test_stale_edit_hash_rejected(self):
        self.edit(source_sha256='wrong')
        self.reject('hash mismatch')

    def test_duplicate_conflicting_rows_rejected(self):
        self.record['rows'].append(dict(self.record['rows'][0],verdict='finding'))
        self.reject('duplicate unit')

    def test_unknown_id_rejected(self):
        self.record['rows'][0]['id']='U90000'
        self.reject('unknown unit')

    def test_missing_row_rejected(self):
        self.record['rows'].pop()
        self.reject('missing or unknown')

    def test_quote_altered_rejected(self):
        self.record['rows'][0]['quote']='made up'
        self.reject('quote mismatch')

    def test_missing_assessment_rejected(self):
        self.record['rows'][0]['assessment']=''
        self.reject('assessment')

    def test_tampered_inventory_rejected(self):
        self.manifest['units'].pop()
        self.reject('inventory mismatch')

    def test_partial_rendering_is_explicit_not_false_failure(self):
        self.record['coverage']['rendered']='not_checked: no image provided'
        self.assertTrue(self.check())

    def test_missing_coverage_dimension_rejected(self):
        del self.record['coverage']['rendered']
        self.reject('coverage dimensions')

    def test_not_verified_required_compile_rejected(self):
        self.record['required_checks']=[dict(name='compile',status='not_verified',receipt='engine unavailable')]
        self.reject('not verified')

    def test_legitimate_not_applicable_check_valid(self):
        self.record['required_checks']=[dict(name='compile',status='not_applicable',receipt='plain text artifact, no build requested')]
        self.assertTrue(self.check())

    def test_generated_primary_target_rejected(self):
        self.write('doc.txt','# Generated by build.py; do not edit\n'+self.source)
        self.manifest=g.snapshot(self.root,['doc.txt','facts.txt'])
        self.source=g.text(self.root/'doc.txt')
        self.record['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read') for u in self.manifest['units']]
        self.edit()
        self.reject('generated source')

    def test_explicit_generated_without_header_rejected(self):
        self.manifest=g.snapshot(self.root,['doc.txt','facts.txt'],generated=['doc.txt'])
        self.edit()
        self.reject('generated source')

    def test_undeclared_quantifier_rejected(self):
        self.edit('may','always does')
        self.reject('undeclared strength')

    def test_undeclared_negation_rejected(self):
        self.edit('may reduce','may not reduce')
        self.reject('undeclared strength')

    def test_number_swap_rejected(self):
        self.edit('12 ms.\r\n\r\nThe sample contains 14','14 ms.\r\n\r\nThe sample contains 12')
        self.reject('undeclared number')

    def test_numbers_elsewhere_do_not_bypass_declaration(self):
        self.edit('12','14')
        self.reject('undeclared number')

    def test_declared_number_without_mapped_support_rejected(self):
        self.edit('12','14',declarations=['number'])
        self.reject('lacks mapped support')

    def test_semantic_review_required(self):
        self.edit(meaning={})
        self.reject('semantic review')

    def test_unverified_word_not_escape(self):
        # Full context also sees that UNVERIFIED separates the value from ms.
        # Declare both token changes so this test still isolates missing support.
        self.edit('12','99 UNVERIFIED',declarations=['number', 'unit'])
        self.reject('lacks mapped support')

    def test_wrong_evidence_hash_rejected(self):
        ev=self.evidence();ev['sha256']='no'
        self.edit('12','14',declarations=['number'],evidence=[ev])
        self.reject('evidence hash')

    def test_wrong_exact_evidence_range_rejected(self):
        ev=self.evidence();ev['line_start']=ev['line_end']=2
        self.edit('12','14',declarations=['number'],evidence=[ev])
        self.reject('specified range')

    def test_fabricated_evidence_quote_rejected(self):
        ev=self.evidence();ev['quote']='The estimator always eliminates error.'
        self.edit('12','14',declarations=['number'],evidence=[ev])
        self.reject('specified range')

    def test_context_not_support_for_changed_meaning(self):
        ev=self.evidence();ev['relation']='context'
        self.edit('12','14',declarations=['number'],evidence=[ev])
        self.reject('lacks mapped support')

    def test_semantic_lie_is_not_proven_by_guard(self):
        # Deliberate limitation: structural checks cannot detect false entailment.
        self.edit('may reduce','always eliminates',declarations=['strength'],meaning=dict(status='changed',assessment='MISLEADING support attestation'),evidence=[self.evidence()])
        self.assertIn('always eliminates',self.check()['doc.txt'])

    def test_overlap_rejected(self):
        self.edit()
        self.edit('may reduce','can lower',id='E2',declarations=['strength'],evidence=[self.evidence()])
        self.reject('overlapping')

    def test_repeated_text_exact_location_supported(self):
        self.write('doc.txt','Repeated phrase.\n\nRepeated phrase.')
        m=g.snapshot(self.root,['doc.txt'])
        r=copy.deepcopy(self.record)
        r['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read') for u in m['units']]
        r['edits']=[dict(id='E1',source='doc.txt',source_sha256=m['sources']['doc.txt']['sha256'],start=18,end=34,current='Repeated phrase.',proposed='Specific phrase.',reason='Context-specific term',declarations=[],meaning=dict(status='preserved',assessment='Preserved local referent'),evidence=[])]
        self.assertEqual(g.validate(self.root,m,r)['doc.txt'],'Repeated phrase.\n\nSpecific phrase.')

    def test_same_basename_preserves_both_paths(self):
        self.write('a/same.txt','Alpha result.');self.write('b/same.txt','Beta result.')
        m=g.snapshot(self.root,['a/same.txt','b/same.txt'])
        r=copy.deepcopy(self.record)
        r['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read') for u in m['units']]
        r['edits']=[]
        for i, u in enumerate(m['units']):
            r['edits'].append(dict(id=f'E{i}',source=u['source'],source_sha256=m['sources'][u['source']]['sha256'],start=0,end=len(u['quote']),current=u['quote'],proposed=u['quote'].replace('result','finding'),reason='Clarity',declarations=[],meaning=dict(status='preserved',assessment='Same finding'),evidence=[]))
        g.stage(self.root,m,g.validate(self.root,m,r),self.root/'out')
        self.assertEqual(g.text(self.root/'out/a/same.txt'),'Alpha finding.')
        self.assertEqual(g.text(self.root/'out/b/same.txt'),'Beta finding.')

    def test_existing_output_never_overwritten(self):
        self.write('stage/precious.txt','Keep this')
        with self.assertRaisesRegex(g.Invalid,'already exists'):
            g.stage(self.root,self.manifest,self.check(),self.root/'stage')
        self.assertEqual(g.text(self.root/'stage/precious.txt'),'Keep this')

    def test_escape_path_rejected(self):
        with self.assertRaisesRegex(g.Invalid,'unsafe path'):
            g.snapshot(self.root,['../outside.txt'])

    def test_case_collision_rejected(self):
        with self.assertRaisesRegex(g.Invalid,'case-colliding'):
            g.snapshot(self.root,['doc.txt','DOC.TXT'])

    def test_snapshot_binding_rejected(self):
        snap=self.root/'snapshot.json';rec=self.root/'record.json'
        g.save_new(snap,self.manifest)
        self.record['snapshot_sha256']='wrong'
        g.save_new(rec,self.record)
        with self.assertRaisesRegex(g.Invalid,'bound'):
            g.read_record(self.root,snap,rec)

    def test_citation_order_swap_requires_declaration(self):
        self.write('doc.txt',r'Claim A \cite{one}; claim B \cite{two}.')
        self.source=g.text(self.root/'doc.txt')
        self.manifest=g.snapshot(self.root,['doc.txt','facts.txt'])
        self.record['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read') for u in self.manifest['units']]
        self.edit(self.source,r'Claim A \cite{two}; claim B \cite{one}.')
        self.reject('undeclared citation')

    def test_unit_change_requires_declaration(self):
        self.edit('12 ms','12 seconds')
        self.reject('undeclared unit')

    def test_binary_artifact_change_rejected(self):
        (self.root/'image.bin').write_bytes(b'\x00\xff\x01')
        self.manifest=g.snapshot(self.root,['doc.txt','facts.txt'],artifacts=['image.bin'])
        (self.root/'image.bin').write_bytes(b'\x00\xff\x02')
        self.reject('stale source')

    def test_all_nonwhitespace_text_is_inventoried(self):
        s='\ufeff# Title\r\n\r\n a\r\nb\n \n $x < y$\n\n| row | 2 |\r\n'
        self.write('mixed.txt',s)
        m=g.snapshot(self.root,['mixed.txt'])
        seen=set(i for u in m['units'] for i in range(u['start'],u['end']))
        self.assertTrue(all(i in seen for i,c in enumerate(s) if not c.isspace() and c!='\ufeff'))

    def test_failed_validation_creates_no_scratch(self):
        self.edit('may','always')
        out=self.root/'out'
        try:
            proposed=self.check()
            g.stage(self.root,self.manifest,proposed,out)
        except g.Invalid:
            pass
        self.assertFalse(out.exists())
        self.assertEqual((self.root/'doc.txt').read_bytes(),self.source.encode())

    def test_linked_input_rejected_when_supported(self):
        try:
            (self.root/'link.txt').symlink_to(self.root/'doc.txt')
        except OSError as exc:
            self.skipTest('OS symlink privilege unavailable: '+str(exc))
        with self.assertRaisesRegex(g.Invalid,'linked path'):
            g.snapshot(self.root,['link.txt'])

    def test_multiline_crlf_evidence_preserves_exact_quote(self):
        quote='The estimator reduced error\r\nby 14 ms in one simulation.'
        self.write('facts.txt',quote+'\r\nThe field effect is unknown.\r\n')
        self.manifest=g.snapshot(self.root,['doc.txt','facts.txt'])
        self.record['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read') for u in self.manifest['units']]
        ev=self.evidence();ev.update(line_end=2,quote=quote)
        self.edit('12','14',declarations=['number'],evidence=[ev])
        self.assertIn('14 ms',self.check()['doc.txt'])

    def reset_source(self, content):
        self.source=content
        self.write('doc.txt',content)
        self.manifest=g.snapshot(self.root,['doc.txt','facts.txt'])
        self.record['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read') for u in self.manifest['units']]

    def test_generated_data_prose_is_editable(self):
        self.reset_source('We evaluate latency on traffic generated by a simulator.\nThe output matches the bound.')
        self.edit('matches','agrees with')
        self.assertIn('agrees with',self.check()['doc.txt'])

    def test_generated_markdown_heading_is_not_a_warning(self):
        self.reset_source('# Benchmarks generated from production traces\n\nThe output matches the bound.')
        self.edit('matches','agrees with')
        self.assertIn('agrees with',self.check()['doc.txt'])

    def test_attached_value_requires_number_declaration(self):
        self.reset_source('The reduction is 12ms in one simulation.')
        self.edit('12ms','14ms')
        self.reject('undeclared number')

    def test_attached_rate_requires_number_declaration(self):
        self.reset_source('The link rate is 100Mbps.')
        self.edit('100Mbps','10Mbps')
        self.reject('undeclared number')

    def test_whole_sentence_final_number_requires_declaration(self):
        self.reset_source('The sample count is 12.')
        self.edit('The sample count is 12.','The sample count is 14.')
        self.reject('undeclared number')

    def test_sentence_final_exponent_requires_declaration(self):
        self.reset_source('The sample count is 12e3.')
        self.edit('The sample count is 12e3.','The sample count is 12e4.')
        self.reject('undeclared number')

    def test_sentence_final_p_value_requires_declaration(self):
        self.reset_source('The p value is 0.05.')
        self.edit(self.source,'The p value is 0.01.')
        self.reject('undeclared number')

    def test_sentence_final_grouped_number_requires_declaration(self):
        self.reset_source('The sample count is 1,234.')
        self.edit(self.source,'The sample count is 1,567.')
        self.reject('undeclared number')

    def test_possessive_rewrite_has_no_unit_change(self):
        self.reset_source("The estimator's error is bounded.")
        self.edit("estimator's error",'error of the estimator')
        self.assertIn('error of the estimator',self.check()['doc.txt'])

    def test_curly_possessive_rewrite_has_no_unit_change(self):
        self.reset_source('The estimator\u2019s error is bounded.')
        self.edit('estimator\u2019s error','error of the estimator')
        self.assertIn('error of the estimator',self.check()['doc.txt'])

    def test_pronoun_us_is_not_a_unit(self):
        self.reset_source('They contacted us before the analysis.')
        self.edit(self.source,'We were contacted before the analysis.')
        self.assertIn('We were contacted',self.check()['doc.txt'])

    def test_parenthetical_plural_is_not_a_unit(self):
        self.reset_source('The author(s) approved the result.')
        self.edit('author(s)','author or authors')
        self.assertIn('author or authors',self.check()['doc.txt'])

    def test_bom_does_not_hide_generated_warning(self):
        self.reset_source('\ufeff# Generated by build.py; do not edit\nThe result agrees with the bound.')
        self.edit('agrees with','matches')
        self.reject('generated source')

    def test_invalid_utf8_evidence_rejected_at_snapshot_with_filename(self):
        (self.root/'utf16.log').write_bytes('Result 14'.encode('utf-16'))
        with self.assertRaisesRegex(g.Invalid,'utf16.log.*UTF-8'):
            g.snapshot(self.root,['doc.txt'],evidence=['utf16.log'])

    def test_unicode_separator_does_not_shift_editor_line_range(self):
        self.write('facts.txt','Trace descriptor\u2028continuation.\nThe estimator reduced error by 14 ms in one simulation.\n')
        self.manifest=g.snapshot(self.root,['doc.txt'],evidence=['facts.txt'])
        self.record['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read') for u in self.manifest['units']]
        ev=self.evidence();ev.update(line_start=2,line_end=2)
        self.edit('12','14',declarations=['number'],evidence=[ev])
        self.assertIn('14 ms',self.check()['doc.txt'])

    def test_attached_unit_requires_unit_declaration(self):
        self.reset_source('The reduction is 12ms in one simulation.')
        self.edit('12ms','12s')
        self.reject('undeclared unit')

    def test_cannot_requires_strength_declaration(self):
        self.edit('reduce error','cannot reduce error')
        self.reject('undeclared strength')

    def test_contraction_requires_strength_declaration(self):
        self.edit('reduce error',"doesn't reduce error")
        self.reject('undeclared strength')

    def test_can_to_cannot_contraction_requires_strength_declaration(self):
        self.edit('may',"can't")
        self.reject('undeclared strength')
        self.record['edits']=[]
        self.reset_source('The estimator can reduce error.')
        self.edit('can',"can't")
        self.reject('undeclared strength')

    def test_microseconds_are_unit_tokens(self):
        self.reset_source('The reduction is 12\u00b5s in one simulation.')
        self.edit('12\u00b5s','12s')
        self.reject('undeclared unit')

    def test_evidence_only_has_no_reader_rows_and_supports_correction(self):
        self.manifest=g.snapshot(self.root,['doc.txt'],evidence=['facts.txt'])
        self.record['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read prose') for u in self.manifest['units']]
        self.assertTrue(all(u['source']=='doc.txt' for u in self.manifest['units']))
        self.edit('12','14',declarations=['number'],evidence=[self.evidence()])
        self.assertIn('14 ms',self.check()['doc.txt'])

    def test_evidence_only_cannot_be_edited_as_audited_prose(self):
        self.manifest=g.snapshot(self.root,['doc.txt'],evidence=['facts.txt'])
        self.record['rows']=[dict(id=u['id'],quote=u['quote'],verdict='ok',assessment='read prose') for u in self.manifest['units']]
        self.edit('The','A',source='facts.txt',source_sha256=self.manifest['sources']['facts.txt']['sha256'])
        self.reject('audited text')

    def test_mid_staging_failure_removes_only_temporary_output(self):
        self.edit()
        proposed=self.check()
        original_write=Path.write_bytes
        def fail_second_file(path,data):
            if path.name=='facts.txt' and any(p.startswith('.audit-stage-') for p in path.parts):
                raise OSError('injected write failure')
            return original_write(path,data)
        with patch.object(Path,'write_bytes',fail_second_file):
            with self.assertRaisesRegex(OSError,'injected write failure'):
                g.stage(self.root,self.manifest,proposed,self.root/'out')
        self.assertFalse((self.root/'out').exists())
        self.assertEqual(list(self.root.glob('.audit-stage-*')),[])
        self.assertEqual((self.root/'doc.txt').read_bytes(),self.source.encode())


if __name__=='__main__':
    unittest.main(verbosity=2)
