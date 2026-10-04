import unittest
import numpy as np
import test_native_reader
from shader_fields import ShaderFields
from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid


def lower(code):
    source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`'+code+'\n')
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
    result=model.lower(source['sections']['comp_']['tree'])
    return model,result


class ShaderLoopsTest(unittest.TestCase):
    def test_global_accumulator_written_by_loop_is_read_after_loop(self):
        model,result=lower('float3 accumulated;shader_body {accumulated=0;for(int n=0;n<3;n++){accumulated+=.25;}ret=accumulated*2;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_allclose(evaluate(result),[1.5]*3)
        np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,)),np.full((2,3),1.5))

    def test_global_loop_update_preserves_zero_iteration_lanes(self):
        model,result=lower('float total;shader_body {total=.2;int n=0;while(n<bass){total+=.1;n++;}ret=total;}')
        self.assertTrue(model.complete,model.unknown)
        actual=evaluate_grid(result,batch_shape=(3,),inputs={'_c3':[[0,0,0,0],[1,0,0,0],[3,0,0,0]]})
        np.testing.assert_allclose(actual,[[.2]*3,[.3]*3,[.5]*3],atol=1e-6)

    def test_for_counter_scope_and_post_increment_preserve_outer_variable(self):
        model,result=lower('shader_body {float i=9;float sum=0;for(int i=0;i<3;i++){sum+=i;}ret=float3(sum,i,0);}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[3,9,0])

    def test_dynamic_while_stops_each_lane_and_preserves_zero_iteration_values(self):
        model,result=lower('shader_body {float p=uv.x;int n=0;while(p<.8){p+=.2;n++;}ret=float3(p,n,0);}')
        self.assertTrue(model.complete,model.unknown)
        actual=evaluate_grid(result,batch_shape=(3,),inputs={'_uv':[[.1,0],[.5,0],[.9,0]]})
        np.testing.assert_allclose(actual,[[.9,4,0],[.9,2,0],[.9,0,0]],atol=1e-6)

    def test_nested_for_loops_preserve_outer_state(self):
        model,result=lower('shader_body {float sum=0;for(int i=0;i<2;i++){for(int j=0;j<3;j++){sum+=i*10+j;}}ret=sum;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[36,36,36])

    def test_helper_loop_preserves_arguments_and_return_value(self):
        model,result=lower('float sumit(float b){float sum=0;for(int i=0;i<3;i++){sum+=b;}return sum;}'
                           'shader_body {ret=sumit(bass);}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result,inputs={'_c3':[2,0,0,0]}),[6,6,6])

    def test_exhausted_loop_budget_raises_instead_of_returning_partial_value(self):
        model,result=lower('shader_body {float x=0;while(bass>0){x+=1;}ret=x;}')
        self.assertTrue(model.complete,model.unknown)
        with self.assertRaisesRegex(UnresolvedMath,'iteration'):
            evaluate(result,inputs={'_c3':[1,0,0,0]})
        np.testing.assert_array_equal(evaluate(result,inputs={'_c3':[0,0,0,0]}),[0,0,0])

    def test_loop_texture_samples_only_active_lanes_with_correct_coordinates(self):
        model,result=lower('shader_body {float sum=0;int n=0;while(n<bass){sum+=GetPixel(uv+float2(n*.1,0)).x;n++;}ret=sum;}')
        self.assertTrue(model.complete,model.unknown)
        samples=[]
        def sample(detail,uv):
            samples.append(uv.copy())
            self.assertEqual(detail['frame'],3)
            return np.stack((uv[:,0],np.zeros(len(uv)),np.zeros(len(uv)),np.ones(len(uv))),axis=-1)
        actual=evaluate_grid(result,batch_shape=(3,),
                             inputs={'_uv':[[.2,0],[.4,0],[.6,0]],'_c3':[[1,0,0,0],[2,0,0,0],[0,0,0,0]]},sample=sample)
        np.testing.assert_allclose(actual,[[.2]*3,[.9]*3,[0]*3],atol=1e-6)
        self.assertEqual([len(s) for s in samples],[2,1])

    def test_loop_condition_side_effects_and_break_stay_explicitly_unresolved(self):
        for code in ['float x=0;while(x++<3){}ret=x;',
                     'float x=0;while(x<3){if(bass>0)break;x++;}ret=x;']:
            model,result=lower('shader_body {'+code+'}')
            self.assertFalse(model.complete)
            self.assertEqual(result.op,'unknown')

    def test_empty_or_unused_loop_cannot_hide_nontermination(self):
        for code in ['while(bass>0){}ret=1;',
                     'float x=0;while(bass>0){x+=1;}ret=1;']:
            model,result=lower('shader_body {'+code+'}')
            self.assertTrue(model.complete,model.unknown)
            with self.assertRaisesRegex(UnresolvedMath,'iteration'):
                evaluate(result,inputs={'_c3':[1,0,0,0]})

    def test_loop_in_unselected_if_branch_does_not_execute(self):
        model,result=lower('shader_body {ret=1;if(bass>0){while(bass>0){}}}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result,inputs={'_c3':[0,0,0,0]}),[1,1,1])

    def test_scalar_loop_outputs_share_one_execution_with_texture_history(self):
        model,result=lower('shader_body {float sum=0;for(int i=0;i<3;i++){sum+=GetPixel(uv).x;}ret=sum;}')
        self.assertTrue(model.complete,model.unknown)
        samples=[]
        def sample(detail,uv):
            self.assertEqual(np.asarray(uv).shape,(2,))
            samples.append(uv.copy())
            return np.array([.25,0,0,1],dtype=np.float32)
        np.testing.assert_allclose(evaluate(result,inputs={'_uv':[.5,.5]},sample=sample),[.75]*3)
        self.assertEqual(len(samples),3)

    def test_unsequenced_arithmetic_updates_do_not_claim_precise_native_order(self):
        model,result=lower('shader_body {float x=1;ret=x+x++;}')
        self.assertFalse(model.complete)
        self.assertEqual(result.op,'unknown')

    def test_branch_masks_inside_loop_inherit_current_state_per_lane(self):
        model,result=lower('shader_body {int n=0;float sum=0;while(n<3){if(bass>n){sum+=.1;}else{sum+=.2;}n++;}ret=sum;}')
        self.assertTrue(model.complete,model.unknown)
        actual=evaluate_grid(result,batch_shape=(3,),inputs={'_c3':[[0,0,0,0],[2,0,0,0],[4,0,0,0]]})
        np.testing.assert_allclose(actual,[[.6]*3,[.4]*3,[.3]*3],atol=1e-6)

    def test_body_shadow_does_not_replace_header_counter(self):
        model,result=lower('shader_body {float sum=0;for(int n=0;n<3;n++){float n=.1;sum+=n;}ret=sum;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_allclose(evaluate(result),[.3]*3,atol=1e-6)

    def test_for_without_declaration_preserves_final_outer_counter(self):
        model,result=lower('shader_body {int n=99;for(n=1;n<4;n+=1){}ret=n;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[4]*3)


if __name__=='__main__':unittest.main()
