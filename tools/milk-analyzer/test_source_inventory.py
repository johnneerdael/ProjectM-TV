import hashlib
import importlib
import unittest


class SourceInventoryTest(unittest.TestCase):
    def inventory(self,raw):return importlib.import_module('source_inventory').inventory_source(raw)

    def test_tokens_point_to_original_bytes_with_crlf_and_shader_wrappers(self):
        raw=b'[preset00]\r\ncomp_1=`shader_body {ret=bass;} // note\r\n'
        inventory=self.inventory(raw)
        tokens=inventory['tokens']
        self.assertEqual([t['text'] for t in tokens],['shader_body','{','ret','=','bass',';','}'])
        for token in tokens:
            reconstructed=b''.join(raw[start:end] for start,end in token['spans'])
            self.assertEqual(reconstructed.decode('latin1'),token['text'])
            self.assertEqual(token['line'],2)
            self.assertEqual(token['stage'],'composite')
        self.assertEqual(inventory['preset_sha256'],hashlib.sha256(raw).hexdigest())

    def test_comments_cross_numbered_lines_without_erasing_source_offsets(self):
        raw=b'comp_1=`/* ignored\ncomp_2=`also ignored */ ret=1;\n'
        inventory=self.inventory(raw)
        self.assertEqual([t['text'] for t in inventory['tokens']],['ret','=','1',';'])
        self.assertEqual(inventory['tokens'][0]['spans'],[[raw.index(b'ret'),raw.index(b'ret')+3]])

    def test_duplicate_keys_gaps_and_unsupported_indices_keep_unique_owners(self):
        raw=b'per_frame_1=q1=1;\nper_frame_1=q1=2;\nper_frame_3=q2=3;\nwave_4_per_point1=x=4;\n'
        inventory=self.inventory(raw)
        self.assertEqual(len(inventory['tokens']),16)
        self.assertEqual(len({t['id'] for t in inventory['tokens']}),16)
        reachable=[t for t in inventory['tokens'] if t['loader_numbering_reachable']]
        self.assertEqual(len(reachable),4)
        self.assertEqual(sum(len(u['token_ids']) for u in inventory['units']),16)

    def test_numbered_source_reordering_does_not_lose_physical_locations(self):
        raw=b'per_frame_2=q2=2;\nper_frame_1=q1=1;\n'
        inventory=self.inventory(raw)
        unit=next(u for u in inventory['units'] if u['loader_numbering_reachable'])
        self.assertEqual(unit['source'],'q1=1;\nq2=2;\n')
        first=next(t for t in inventory['tokens'] if t['id']==unit['token_ids'][0])
        self.assertEqual(first['line'],2)

    def test_changed_source_invalidates_all_source_bound_ids(self):
        first=self.inventory(b'per_frame_1=q1=1;\n')
        second=self.inventory(b'per_frame_1=q1=2;\n')
        self.assertTrue(set(t['id'] for t in first['tokens']).isdisjoint(t['id'] for t in second['tokens']))

    def test_omitted_duplicate_or_changed_ownership_payload_is_rejected(self):
        import copy
        module=importlib.import_module('source_inventory');raw=b'per_frame_1=q1=1;\n'
        original=self.inventory(raw)
        for mutation in ['missing','duplicate','span']:
            changed=copy.deepcopy(original)
            if mutation=='missing':changed['units'][0]['token_ids'].pop()
            elif mutation=='duplicate':changed['tokens'].append(dict(changed['tokens'][0]))
            else:changed['tokens'][0]['spans'][0][0]+=1
            with self.assertRaises(ValueError):module.validate_inventory(raw,changed)


if __name__=='__main__':unittest.main()
