"""Coverage must not turn parser success or engine boilerplate into proof."""
import importlib
import hashlib
import unittest


class CoverageAuditTest(unittest.TestCase):
    def audit(self, source, cache=None):
        module = importlib.import_module('coverage_audit')
        return module.audit_source(source, cache=cache, reader_sha='reader')

    def cache(self, source, sections):
        return {'preset_sha256': hashlib.sha256(source).hexdigest(),
                'reader_sha256': 'reader', 'sections': sections}

    def test_unparsed_and_unvisited_numbered_source_stays_in_denominator(self):
        source = b'[preset00]\nper_frame_1=q1=bass;\nper_frame_3=q2=treb;\n'
        report = self.audit(source)
        self.assertEqual(report['source_tokens'], 8)
        self.assertEqual(report['stages']['eel']['source_tokens'], 8)
        self.assertEqual(report['unvisited_code_tokens'], 4)
        self.assertEqual(report['parsed_code_tokens'], 0)

    def test_native_confirmed_ignored_source_is_retained_without_execution_gap(self):
        from test_native_reader import NativeReaderTest
        from gap_priority import rank_gaps
        source=(b'per_frame_1=q1=.2;\nper_frame_1=q1=100;\n'
                b'shape_4_per_frame1=zoom=100;\n=1\n')
        cache=NativeReaderTest().read(source.decode())
        cache.update(preset_sha256=hashlib.sha256(source).hexdigest(),reader_sha256='reader')
        report=self.audit(source,cache)
        ignored=[u for u in report['units'] if not u['loader_numbering_reachable']]
        self.assertEqual(len(ignored),3)
        self.assertTrue(all(u['loader_ignored_confirmed'] for u in ignored))
        self.assertEqual(report['unvisited_code_tokens'],10)
        self.assertEqual(report['parsed_code_tokens'],4)
        report.update(preset='fixture.milk',preset_sha256=hashlib.sha256(source).hexdigest())
        self.assertEqual(rank_gaps([report])['presets_with_known_gaps'],0)
        self.assertFalse(report['visual_gate']['eligible'])

    def test_unvisited_source_without_matching_native_evidence_remains_a_gap(self):
        from gap_priority import rank_gaps
        source=b'per_frame_1=q1=.2;\nper_frame_3=q1=100;\n'
        report=self.audit(source)
        self.assertFalse(report['units'][1].get('loader_ignored_confirmed',False))
        report.update(preset='fixture.milk',preset_sha256=hashlib.sha256(source).hexdigest())
        self.assertEqual(rank_gaps([report])['presets_with_known_gaps'],1)

    def test_native_loader_confirmation_requires_actual_prefixes_and_first_values(self):
        from test_native_reader import NativeReaderTest
        source=b'per_frame_1=q1=.2;\nper_frame_1=q1=100;\n'
        cache=NativeReaderTest().read(source.decode())
        cache.update(preset_sha256=hashlib.sha256(source).hexdigest(),reader_sha256='reader')
        cache['values']['per_frame_1']='q1=.7;'
        self.assertFalse(self.audit(source,cache)['units'][1]['loader_ignored_confirmed'])
        cache['values']['per_frame_1']='q1=.2;'
        cache['requested_code_prefixes']=[]
        self.assertFalse(self.audit(source,cache)['units'][1]['loader_ignored_confirmed'])

    def test_scalar_configuration_is_not_ignored_code(self):
        from test_native_reader import NativeReaderTest
        source=b'fDecay=.98;\nper_frame_1=q1=.2;\n'
        cache=NativeReaderTest().read(source.decode())
        cache.update(preset_sha256=hashlib.sha256(source).hexdigest(),reader_sha256='reader')
        unit=next(u for u in self.audit(source,cache)['units'] if u['stage']=='configuration')
        self.assertFalse(unit['loader_ignored_confirmed'])

    def test_parser_success_does_not_open_behavior_gate(self):
        source = b'per_frame_1=q1=bass;\n'
        cache = self.cache(source, {'per_frame_': {'status': 'parsed',
                           'projectm_native_status': 'parsed', 'source': 'q1=bass;\n', 'tree': {}}})
        report = self.audit(source, cache)
        self.assertEqual(report['parsed_code_tokens'], 4)
        self.assertIsNone(report['verified_behavior_percent'])
        self.assertFalse(report['visual_gate']['eligible'])

    def test_stale_source_or_reader_cache_cannot_count_as_parsed(self):
        source = b'per_frame_1=q1=bass;\n'
        cache = self.cache(source, {'per_frame_': {'status': 'parsed'}})
        cache['reader_sha256'] = 'old-reader'
        self.assertEqual(self.audit(source, cache)['parsed_code_tokens'], 0)
        cache['reader_sha256'] = 'reader'
        cache['preset_sha256'] = 'stale-source'
        self.assertEqual(self.audit(source, cache)['parsed_code_tokens'], 0)

    def test_engine_header_and_optimized_tree_never_change_denominator(self):
        source = b'per_frame_1=q1=bass;q1=0;\n'
        cache = self.cache(source, {'per_frame_': {'status': 'parsed',
                           'projectm_native_status': 'parsed', 'source': 'q1=bass;q1=0;\n',
                           'tree': {'injected_header': 'noise '*10000}}})
        self.assertEqual(self.audit(source, cache)['source_tokens'], 8)

    def test_duplicate_and_unknown_rows_are_retained(self):
        source = b'per_frame_1=q1=1;\nper_frame_1=q1=2;\nfuture_code=ret\n'
        report = self.audit(source)
        self.assertEqual(report['source_tokens'], 11)
        self.assertEqual(report['unvisited_code_tokens'], 4)
        self.assertEqual(report['stages']['configuration']['source_tokens'], 3)

    def test_shader_comments_are_removed_across_numbered_lines_but_literals_remain(self):
        source = (b'comp_1=`/* not code\ncomp_2=`also not code */ ret=1; // ignored\n'
                  b'comp_3=`"// literal";\n')
        report = self.audit(source)
        self.assertEqual(report['source_tokens'], 6)
        self.assertEqual(report['stages']['composite']['source_tokens'], 6)

    def test_source_mismatch_cannot_accept_even_matching_file_digest(self):
        source = b'per_frame_1=q1=bass;\n'
        cache = self.cache(source, {'per_frame_': {'status': 'parsed',
                          'projectm_native_status': 'parsed', 'source': 'q1=treb;\n'}})
        self.assertEqual(self.audit(source, cache)['parsed_code_tokens'], 0)

    def test_original_only_eel_acceptance_is_not_target_parsing(self):
        source = b'per_frame_1=q1=bass;\n'
        cache = self.cache(source, {'per_frame_': {'status': 'parsed',
                          'projectm_native_status': 'unknown', 'source': 'q1=bass;\n'}})
        self.assertEqual(self.audit(source, cache)['parsed_code_tokens'], 0)

    def test_unsupported_component_index_is_not_claimed_as_visited(self):
        report = self.audit(b'wave_4_per_point1=x=bass;\n')
        self.assertEqual(report['unvisited_code_tokens'], 4)

    def test_complete_native_shader_lowering_still_has_no_behavior_percentage(self):
        from test_native_reader import NativeReaderTest
        source = b'PSVERSION_COMP=2\ncomp_1=`shader_body {ret=float3(bass);}\n'
        cache = NativeReaderTest().read(source.decode())
        cache.update(preset_sha256=hashlib.sha256(source).hexdigest(), reader_sha256='reader')
        report = self.audit(source, cache)
        self.assertEqual(report['stages']['composite']['lowering_complete_tokens'], 10)
        self.assertIsNone(report['verified_behavior_percent'])
        self.assertFalse(report['visual_gate']['eligible'])


if __name__ == '__main__':
    unittest.main()
