import unittest
from shader_fields import ShaderFields, Field
import test_native_reader


def const(value):return {"kind":"constant","value":value,"type":{"name":"float"}}
def var(name):return {"kind":"variable","name":name,"type":{"name":"float"}}
def binary(op,left,right):return {"kind":"binary","operator":op,"left":left,"right":right,"type":{"name":"float"}}


class ShaderFieldsTest(unittest.TestCase):
    def test_declare_then_assign_does_not_report_an_uninitialized_read(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'
            'comp_1=`shader_body {float x;float unused;x=bass;ret=float3(x);}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertTrue(model.complete,model.unknown)
        from field_math import evaluate
        self.assertEqual(evaluate(result,inputs={'_c3':[2,0,0,0]}).tolist(),[2,2,2])

    def test_a_possible_uninitialized_branch_read_remains_unknown(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'
            'comp_1=`shader_body {float x;if(bass>0){x=1;}ret=float3(x);}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertFalse(model.complete)
        self.assertEqual(result.op,'unknown')

    def test_texture_helper_sampler_retains_main_history(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'
            'comp_1=`float3 sampleit(sampler2D s,float2 p){return tex2D(s,p).xyz;}\n'
            'comp_2=`shader_body {ret=sampleit(sampler_main,uv);}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertTrue(model.complete,model.unknown)
        sample=result.args[0]
        self.assertEqual(sample.detail['sampler'],'sampler_main')
        self.assertEqual(sample.detail['frame'],3)

    def test_lod_and_projected_texture_calls_are_not_misread_as_plain_uv_samples(self):
        for call in ['tex2Dproj']:
            tree=test_native_reader.NativeReaderTest().read(f'PSVERSION_COMP=2\ncomp_1=`shader_body {{ret={call}(sampler_main,float4(uv,0,2)).xyz;}}\n')['sections']['comp_']['tree']
            model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
            result=model.lower(tree)
            self.assertFalse(model.complete)
            self.assertEqual(result.op,'unknown')

    def test_pre_and_post_increment_preserve_returned_and_stored_values(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`shader_body {float x=0;x++;ret=float3(x);}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertTrue(model.complete,model.unknown)
        from field_math import evaluate
        self.assertEqual(evaluate(result).tolist(),[1,1,1])
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`shader_body {float x=1;float old=x++;float now=++x;ret=float3(old,now,x);}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        self.assertEqual(evaluate(model.lower(tree)).tolist(),[1,3,3])

    def test_ternary_side_effects_cannot_be_eagerly_executed_as_complete(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`shader_body {float x=0;float y=bass>0 ? (x=1) : (x=2);ret=float3(x);}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertFalse(model.complete)
        self.assertEqual(result.op,'unknown')

    def test_native_helper_is_inlined_with_default_argument_and_local_scope(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_WARP=2\n'
            'warp_1=`float3 pulse(float b, float gain=.5){float local=b*gain;return float3(local);}\n'
            'warp_2=`shader_body {float local=.25; ret=pulse(bass)+local;}\n')['sections']['warp_']['tree']
        model=ShaderFields(stage='warp',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertTrue(model.complete,model.unknown)
        self.assertEqual(result.op,'add')
        self.assertEqual(result.args[0].op,'construct')
        self.assertEqual(result.args[0].args[0].op,'multiply')
        self.assertAlmostEqual(result.args[0].args[0].args[1].detail['value'],.5)
        from field_math import evaluate
        self.assertEqual(evaluate(result,inputs={'_c3':[1,0,0,0]}).tolist(),[.75,.75,.75])

    def test_block_local_shadow_does_not_replace_outer_value(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'
            'comp_1=`shader_body {float b=bass; {float b=treb;ret=float3(b);} ret+=b;}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertTrue(model.complete,model.unknown)
        self.assertEqual(result.op,'add')
        self.assertEqual(result.args[0].args[0].detail['field'],'z')
        from field_math import evaluate
        self.assertEqual(evaluate(result,inputs={'_c3':[1,0,3,0]}).tolist(),[4,4,4])

    def test_helper_with_output_argument_is_explicitly_unresolved(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'
            'comp_1=`float3 change(inout float b){b*=2;return float3(b);}\n'
            'comp_2=`shader_body {float b=bass;ret=change(b);}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertFalse(model.complete)
        self.assertEqual(result.op,'unknown')
        self.assertIn('output',result.detail['reason'])

    def test_texture_sample_preserves_surface_age_and_coordinates(self):
        model=ShaderFields(stage="warp",frame=3,warp_reads_blur=True)
        main=model.expression({"kind":"call","function":"tex2D","args":[var("sampler_main"),var("uv")],"type":{"name":"float4"}})
        blur=model.expression({"kind":"call","function":"tex2D","args":[var("sampler_blur1"),var("uv")],"type":{"name":"float4"}})
        self.assertEqual(main.detail["frame"],2)
        self.assertEqual(blur.detail["frame"],1)
        self.assertEqual(main.args[0].op,"input")

    def test_successive_writes_retain_operation_chain(self):
        model=ShaderFields(stage="composite",frame=3,warp_reads_blur=True)
        model.expression(binary(16,var("ret"),var("bass")))
        model.expression(binary(19,var("ret"),const(.5)))
        result=model.environment["ret"]
        self.assertEqual(result.op,"multiply")
        self.assertEqual(result.args[0].detail["name"],"bass")

    def test_conditions_preserve_both_possible_colour_writes(self):
        model=ShaderFields(stage="composite",frame=3,warp_reads_blur=True)
        model.environment["ret"]=Field("constant",detail={"value":0})
        model.statements([{"kind":"if","condition":var("bass"),
                           "yes":[{"kind":"expression","value":binary(16,var("ret"),const(1))}],
                           "no":[{"kind":"expression","value":binary(16,var("ret"),const(.2))}]}])
        self.assertEqual(model.environment["ret"].op,"select")
        self.assertEqual([a.detail["value"] for a in model.environment["ret"].args[1:]],[1,.2])

    def test_unsupported_operation_remains_in_output_graph(self):
        model=ShaderFields(stage="warp",frame=3,warp_reads_blur=True)
        result=model.expression({"kind":"call","function":"not_understood","args":[var("bass")],"type":{"name":"float"}})
        self.assertEqual(result.op,"unknown")
        self.assertFalse(model.complete)
        self.assertEqual(result.args[0].detail["name"],"bass")


if __name__=="__main__":unittest.main()
