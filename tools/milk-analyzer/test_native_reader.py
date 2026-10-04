import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READER = Path(os.environ.get("MILK_NATIVE_READER", ROOT / "build/milk-analyzer/native/milk-native-reader"))


class NativeReaderTest(unittest.TestCase):
    def test_commented_texsize_does_not_invent_a_sampler_binding(self):
        result=self.read('PSVERSION_WARP=2\nwarp_1=`// float4 texsize_fc_main;\n'
                         'warp_2=`shader_body {ret=GetPixel(uv);}\n')
        section=result['sections']['warp_'];self.assertEqual(section['status'],'parsed',result)
        names={d['name'] for node in section['tree'] if node['kind']=='declarations' for d in node['values']}
        self.assertNotIn('texsize_fc_main',names)
        self.assertNotIn('sampler_fc_main',names)
        from shader_fields import ShaderFields
        model=ShaderFields(stage='warp',frame=3,warp_reads_blur=False,frame_wrap=0)
        field=model.lower(section['tree'])
        self.assertTrue(model.complete,model.unknown)
        self.assertFalse(field.args[0].detail['sampling_policy']['wrap'])
    def test_authored_texsize_declaration_is_rebuilt_as_native_uniform(self):
        result=self.read('PSVERSION_COMP=2\ncomp_1=`float4 texsize_image;\n'
                         'comp_2=`shader_body {ret=texsize_image.xyz;}\n')
        tree=result['sections']['comp_']['tree']
        declaration=next(d for node in tree if node['kind']=='declarations'
                         for d in node['values'] if d['name']=='texsize_image')
        self.assertEqual(declaration['type']['flags']&4,4)

    def test_texsize_rebuilding_preserves_deleted_line_refs_and_qualifiers(self):
        result=self.read('PSVERSION_COMP=2\ncomp_1=`uniform float4 texsize_a; float4 texsize_b;\n'
                         'comp_2=`float g=.4;\ncomp_3=`shader_body {ret=float3(g);}\n')
        tree=result['sections']['comp_']['tree']
        declarations={d['name']:d for node in tree if node['kind']=='declarations' for d in node['values']}
        self.assertEqual(declarations['texsize_a']['type']['flags']&4,4)
        self.assertEqual(declarations['texsize_b']['type']['flags']&4,4)
        self.assertEqual(declarations['g']['type']['flags']&4,4)
    def test_unused_sampler_declaration_keeps_native_binding_order(self):
        for declaration in ['sampler2D sampler_fc_main;',
                            'sampler2D sampler_noise_hq; sampler2D sampler_fc_main;']:
            with self.subTest(declaration=declaration):
                result=self.read('PSVERSION_WARP=2\nwarp_1=`'+declaration+'\n'
                                 'warp_2=`shader_body {ret=tex2D(sampler_main,uv).xyz;}\n')
                section=result['sections']['warp_']
                self.assertEqual(section['status'],'parsed',result)
                from shader_fields import ShaderFields
                model=ShaderFields(stage='warp',frame=3,warp_reads_blur=False,frame_wrap=0)
                field=model.lower(section['tree'])
                self.assertTrue(model.complete,model.unknown)
                self.assertTrue(field.args[0].detail['sampling_policy']['wrap'])

    def test_sampler_removal_preserves_native_qualifier_spillover(self):
        code=['#define sampler_pic sampler_main','uniform sampler2D sampler_pic;',
              'float g=.4;','float helper(){return g;}',
              'shader_body {g=.8;ret=float3(helper());}']
        result=self.read('PSVERSION_COMP=2\n'+'\n'.join('comp_'+str(i+1)+'=`'+line
                         for i,line in enumerate(code))+'\n')
        section=result['sections']['comp_']
        self.assertEqual(section['status'],'parsed',result)
        g=next(d for node in section['tree'] if node['kind']=='declarations'
               for d in node['values'] if d['name']=='g')
        self.assertEqual(g['type']['flags']&4,4)

    def test_generic_sampler_alias_declaration_uses_rebuilt_texture_binding(self):
        result=self.read('PSVERSION_COMP=2\ncomp_1=`#define sampler_pic sampler_cells\n'
                         'comp_2=`sampler sampler_pic;\n'
                         'comp_3=`shader_body {ret=tex2D(sampler_pic,uv).xyz;}\n')
        self.assertEqual(result['sections']['comp_']['status'],'parsed',result)

    def test_sampler_alias_declaration_uses_native_rebuilt_binding(self):
        result=self.read('PSVERSION_COMP=2\ncomp_1=`#define sampler_pic sampler_cells\n'
                         'comp_2=`sampler2D sampler_pic;\n'
                         'comp_3=`shader_body {ret=tex2D(sampler_pic,uv).xyz;}\n')
        self.assertEqual(result['sections']['comp_']['status'],'parsed',result)
        from shader_fields import ShaderFields
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        field=model.lower(result['sections']['comp_']['tree'])
        self.assertTrue(model.complete,model.unknown)
        self.assertEqual(field.args[0].detail['sampler'],'sampler_cells')

    def test_sampler_alias_does_not_preserve_native_deleted_same_line_code(self):
        result=self.read('PSVERSION_COMP=2\ncomp_1=`#define sampler_pic sampler_main\n'
                         'comp_2=`shader_body {\n'
                         'comp_3=`sampler2D sampler_pic; ret=float3(.9,.1,.2);\n'
                         'comp_4=`}\n')
        self.assertEqual(result['sections']['comp_']['status'],'parsed',result)
        from shader_fields import ShaderFields
        from field_math import evaluate
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        field=model.lower(result['sections']['comp_']['tree'])
        self.assertTrue(model.complete,model.unknown)
        self.assertEqual(evaluate(field).tolist(),[0,0,0])

    def test_custom_wave_forward_backward_audio_smoothing_matches_known_kernel(self):
        left=[0]*480;left[239]=1
        settings={'frame_program':'frame','spectrum':False,'separation':0,'scaling':1,'smoothing':.5,
                  'preset_wave_scale':1,'left':left,'right':[0]*480}
        result=self.execute({'frame':'samples=3;','point':'0;'},
                            [{'program':'frame'},{'program':'point','wave_points':settings,'capture':['value1']}])
        for point,expected in zip(result['steps'][1]['points'],[.1659*.004,.237*.004,.21*.004]):
            self.assertAlmostEqual(point['value1'],expected,places=9)

    def test_custom_spectrum_stride_uses_native_truncated_indices(self):
        settings={'frame_program':'frame','spectrum':True,'separation':0,'scaling':1,'smoothing':0,
                  'preset_wave_scale':1,'left':list(range(512)),'right':[0]*512}
        result=self.execute({'frame':'samples=3;','point':'0;'},
                            [{'program':'frame'},{'program':'point','wave_points':settings,'capture':['value1']}])
        for point,expected in zip(result['steps'][1]['points'],[0,170*.15,341*.15]):
            self.assertAlmostEqual(point['value1'],expected,places=4)

    def test_dynamic_custom_wave_samples_qt_and_point_locals_use_native_execution(self):
        settings={'frame_program':'frame','spectrum':False,'separation':0,'scaling':1,'smoothing':0,
                  'preset_wave_scale':1,'left':list(range(480)),'right':[0]*480}
        result=self.execute({'frame':'samples=3;q1=5;t1=2;r=.4;g=.5;b=.6;a=1;',
                             'point':'q1+=1;t1+=1;counter+=1;x=q1;y=t1;'},
                            [{'program':'frame'},
                             {'program':'point','variables':{**{name:{'program':'frame','variable':name} for name in ['q1','t1']}},
                              'wave_points':settings,'capture':['x','y','counter','sample','value1','r']}])
        group=result['steps'][1]
        self.assertEqual(group['sample_count'],3)
        self.assertEqual([p['x'] for p in group['points']],[6,7,8])
        self.assertEqual([p['y'] for p in group['points']],[3,4,5])
        self.assertEqual([p['counter'] for p in group['points']],[1,2,3])
        self.assertEqual([p['sample'] for p in group['points']],[0,.5,1])
        self.assertAlmostEqual(group['points'][0]['value1'],238*.004,places=6)
        self.assertEqual([p['r'] for p in group['points']],[.4]*3)

    def test_native_custom_wave_skips_one_sample_even_for_dots(self):
        settings={'frame_program':'frame','spectrum':False,'separation':0,'scaling':1,'smoothing':.5,
                  'preset_wave_scale':1,'left':[0]*480,'right':[0]*480}
        result=self.execute({'frame':'samples=1;','point':'reg00+=1;'},
                            [{'program':'frame'},{'program':'point','wave_points':settings,'capture':['reg00']}])
        self.assertEqual(result['steps'][1]['points'],[])
        self.assertEqual(result['steps'][1]['sample_count'],1)

    def test_generated_texture_size_bindings_retain_native_uniform_qualifier(self):
        result=self.read('PSVERSION_COMP=2\ncomp_1=`shader_body {ret=texsize_noise_hq.xyz;}\n')
        declarations=[d for node in result['sections']['comp_']['tree'] if node['kind']=='declarations' for d in node['values']]
        size=next(d for d in declarations if d['name']=='texsize_noise_hq')
        self.assertEqual(size['type']['flags']&4,4)

    def test_dynamic_context_transfers_reuse_actual_frame_outputs_and_init_defaults(self):
        result=self.execute({'init':{'scope':'main','code':'q1=3;counter=0;'},
                             'frame':{'scope':'main','code':'counter+=1;q1+=bass;'},
                             'defaults':'0;',
                             'point':'q1+=1;x=q1;'},
                            [{'program':'init'},
                             {'program':'defaults','variables':{'q1':{'program':'init','variable':'q1'}}},
                             {'program':'frame','variables':{'bass':2},
                              'reset_variables':{'q1':{'program':'defaults','variable':'q1'}},'capture':['q1','counter']},
                             {'program':'point','repeat':2,
                              'reset_variables':{'q1':{'program':'frame','variable':'q1'}},'capture':['x']},
                             {'program':'frame','variables':{'bass':4},
                              'reset_variables':{'q1':{'program':'defaults','variable':'q1'}},'capture':['q1','counter']}])
        self.assertEqual(result['steps'][2],{'q1':5,'counter':1})
        self.assertEqual(result['steps'][3:5],[{'x':6},{'x':6}])
        self.assertEqual(result['steps'][5],{'q1':7,'counter':2})

    def test_init_and_frame_programs_share_explicit_component_scope_and_local_memory(self):
        result=self.execute({'init':{'scope':'main','code':'counter=5;megabuf(3)=.4;'},
                             'frame':{'scope':'main','code':'counter+=1;q1=megabuf(3)+counter;'},
                             'other':{'scope':'wave0','code':'q1=counter+megabuf(3);'}},
                            [{'program':'init'},
                             {'program':'frame','capture':['counter','q1']},
                             {'program':'other','capture':['counter','q1']},
                             {'program':'frame','capture':['counter','q1']}])
        self.assertEqual(result['steps'][1]['counter'],6)
        self.assertAlmostEqual(result['steps'][1]['q1'],6.4)
        self.assertEqual(result['steps'][2],{'counter':0,'q1':0})
        self.assertAlmostEqual(result['steps'][3]['q1'],7.4)

    def test_float_literal_preserves_native_and_renderer_values_separately(self):
        result=self.read('PSVERSION_COMP=2\ncomp_1=`shader_body {ret=16777216.;}\n')
        nodes=[]
        def visit(node):
            if isinstance(node,dict):
                if node.get('kind')=='constant' and node.get('value')==16777216:nodes.append(node)
                for value in node.values():visit(value)
            elif isinstance(node,list):
                for value in node:visit(value)
        visit(result['sections']['comp_']['tree'])
        self.assertEqual(len(nodes),1)
        self.assertEqual(nodes[0]['renderer_literal'],'float(1.67772e+07)')

    def execute(self, programs, steps):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"execution.json"
            path.write_text(json.dumps({"programs":programs,"steps":steps}))
            result=subprocess.run([str(READER),"--equations",str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            return json.loads(result.stdout)

    def read(self, body, version=201):
        self.assertTrue(READER.is_file(), "native code-only Milk reader has not been built")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.milk"
            path.write_text(f"MILKDROP_PRESET_VERSION={version}\n[preset00]\n" + body)
            result = subprocess.run([str(READER), str(path)], check=True, capture_output=True, text=True)
            return json.loads(result.stdout)

    def test_native_equation_tree_retains_loops_and_memory(self):
        result = self.read("per_frame_1=q1=bass;loop(3,q1+=0.1);megabuf(2)=q1;reg00=megabuf(2);\n")
        section = result["sections"]["per_frame_"]
        self.assertEqual(section["status"], "parsed")
        tree = json.dumps(section["tree"])
        self.assertIn('"loop"', tree)
        self.assertIn('"bass"', tree)
        self.assertIn('"reg00"', tree)
        self.assertIn('"mem"', tree)

    def test_shader_native_types_helpers_loops_and_packed_bass_alias(self):
        result = self.read("PSVERSION_WARP=2\n"
            "warp_1=`float2 bend(float b){return float2(b,0);}\n"
            "warp_2=`shader_body { float2 p=uv; for(int i=0;i<3;i++){p+=bend(bass*.1);} ret=tex2D(sampler_main,p).xyz; }\n")
        section = result["sections"]["warp_"]
        self.assertEqual(section["status"], "parsed")
        tree = json.dumps(section["tree"])
        for name in ['"bend"', '"for"', '"float2"', '"_c3"', '"tex2D"']:
            self.assertIn(name, tree)

    def test_equation_constants_use_the_native_language(self):
        result = self.read("per_frame_1=zoom=$PI;rot=$XFF;q1=$'A';\n")
        self.assertEqual(result["sections"]["per_frame_"]["status"], "parsed")

    def test_malformed_shader_is_unknown_and_not_silently_empty(self):
        result = self.read("PSVERSION_WARP=2\nwarp_1=`shader_body { ret=missing_function(bass); }\n")
        self.assertEqual(result["sections"]["warp_"]["status"], "unknown")
        self.assertFalse(result["syntax_complete"])

    def test_disabled_shape_is_recorded_without_treating_it_as_active(self):
        result = self.read("shapecode_0_enabled=0\nshape_0_per_frame1=rad=bass;\n")
        self.assertFalse(result["sections"]["shape_0_per_frame"]["active"])
        self.assertEqual(result["sections"]["shape_0_per_frame"]["status"], "parsed")

    def test_legacy_comment_encoding_does_not_break_native_parsing_or_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"legacy.milk"
            path.write_bytes(b"[preset00]\nper_frame_1=zoom=1; // \xf6\n")
            result=subprocess.run([str(READER),str(path)],check=True,capture_output=True,text=True)
            self.assertEqual(json.loads(result.stdout)["sections"]["per_frame_"]["status"],"parsed")

    def test_sampler_state_language_is_preserved_in_the_tree(self):
        result=self.read("PSVERSION_COMP=2\n"
            "comp_1=`sampler sampler_grad = sampler_state { AddressU=WRAP; AddressV=CLAMP; };\n"
            "comp_2=`shader_body { ret=tex2D(sampler_grad,uv).xyz; }\n")
        section=result["sections"]["comp_"]
        self.assertEqual(section["status"],"parsed")
        tree=json.dumps(section["tree"])
        self.assertIn('"sampler_state"',tree)
        self.assertIn('"state_id": 1',tree)

    def test_shader_footer_after_body_is_not_executed(self):
        result=self.read("PSVERSION_WARP=2\n"
            "warp_1=`shader_body { ret=float3(bass); }\n"
            "warp_2=`written by author\nwarp_3=`END\n")
        self.assertEqual(result["sections"]["warp_"]["status"],"parsed")

    def test_standard_hlsl_all_is_understood_with_a_compatibility_annotation(self):
        result=self.read("PSVERSION_WARP=2\n"
            "warp_1=`shader_body { ret=all(float2(bass,mid)) ? float3(1) : float3(0); }\n")
        section=result["sections"]["warp_"]
        self.assertEqual(section["status"],"parsed")
        self.assertIn("all",section["language_extensions"])

    def test_version_one_shaders_are_not_active(self):
        result=self.read("PSVERSION_WARP=2\nwarp_1=`shader_body { ret=float3(bass); }\n",version=100)
        self.assertFalse(result["sections"]["warp_"]["active"])

    def test_numbered_equation_line_boundaries_follow_original_milkdrop(self):
        result=self.read("per_frame_1=is_beat=bass;\nper_frame_2=q1=is_\nper_frame_3=beat*.2;\n")
        section=result["sections"]["per_frame_"]
        self.assertEqual(section["status"],"parsed")
        self.assertEqual(section["projectm_native_status"],"unknown")
        self.assertIn('"is_beat"',json.dumps(section["tree"]))

    def test_original_double_backslash_equation_comments(self):
        result=self.read("per_frame_1=zoom=1;\\\\ note\nper_frame_2=rot=bass;\n")
        self.assertEqual(result["sections"]["per_frame_"]["status"],"parsed")

    def test_matrix_brace_initializers_preserve_typed_elements(self):
        result=self.read("PSVERSION_WARP=2\n"
            "warp_1=`shader_body { float2x2 r={bass,0,0,1}; ret=float3(mul(r,uv),0); }\n")
        section=result["sections"]["warp_"]
        self.assertEqual(section["status"],"parsed")
        self.assertIn('"aggregate"',json.dumps(section["tree"]))

    def test_default_shader_arguments_keep_constants_and_bass(self):
        for default in [".42","bass"]:
            result=self.read("PSVERSION_WARP=2\n"
                f"warp_1=`float helper(float x={default}) {{ return x; }}\n"
                "warp_2=`shader_body {ret=float3(helper());}\n")
            section=result["sections"]["warp_"]
            self.assertEqual(section["status"],"parsed")
            helper=next(node for node in section["tree"] if node.get("name")=="helper")
            expression=helper["args"][0].get("default")
            self.assertIsNotNone(expression)
            if default=="bass":self.assertIn('"_c3"',json.dumps(expression))
            else:self.assertAlmostEqual(expression["value"],.42,places=6)

    def test_nonfinite_native_constants_have_explicit_ieee_values(self):
        result=self.read("per_frame_1=q1=exp(1000);\n")
        tree=json.dumps(result["sections"]["per_frame_"]["tree"])
        self.assertIn('"positive_infinity"',tree)
        self.assertNotIn('"value": null',tree)

    def test_equation_execution_preserves_custom_state_and_explicit_q_resets(self):
        result=self.execute({"frame":"ma+=bass;q1+=bass;"},[
            {"program":"frame","variables":{"bass":1,"q1":0},"capture":["ma","q1"]},
            {"program":"frame","variables":{"bass":1,"q1":0},"capture":["ma","q1"]}])
        self.assertEqual(result["steps"],[{"ma":1,"q1":1},{"ma":2,"q1":1}])

    def test_equation_contexts_share_global_memory_and_registers(self):
        result=self.execute({"frame":"gmegabuf(4)=bass*2;reg00=bass;",
                             "shape":"rad=gmegabuf(4)*.1;r=reg00;"},[
            {"program":"frame","variables":{"bass":1.5},"capture":["reg00"]},
            {"program":"shape","capture":["rad","r"]}])
        self.assertAlmostEqual(result["steps"][1]["rad"],.3)
        self.assertEqual(result["steps"][1]["r"],1.5)

    def test_instance_builtins_reset_while_custom_variables_persist(self):
        result=self.execute({"shape":"rad+=bass;ma+=bass;"},[
            {"program":"shape","variables":{"bass":1},"repeat":3,
             "reset_variables":{"rad":.1},"capture":["rad","ma"]}])
        self.assertEqual([row["ma"] for row in result["steps"]],[1,2,3])
        for row in result["steps"]:self.assertAlmostEqual(row["rad"],1.1)


if __name__ == "__main__":
    unittest.main()
