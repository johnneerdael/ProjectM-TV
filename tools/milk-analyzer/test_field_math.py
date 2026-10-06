"""Source arithmetic tests, with no rendered/reference images."""
import pytest
import math
import unittest
import numpy as np
import test_native_reader
import shader_fields


def lower(body,stage='warp'):
    prefix='warp' if stage=='warp' else 'comp'
    lines='\n'.join(f'{prefix}_{i}=`{line}' for i,line in enumerate(('shader_body { '+body+' }').splitlines(),1))
    section=test_native_reader.NativeReaderTest().read(f'PSVERSION_{prefix.upper()}=2\n{lines}\n')['sections'][prefix+'_']
    assert section['status']=='parsed',section
    tree=section['tree']
    model=shader_fields.ShaderFields(stage=stage,frame=3,warp_reads_blur=True)
    result=model.lower(tree)
    return model,result


class FieldMathTest(unittest.TestCase):
    def test_native_zero_multiply_masks_the_sample01_unused_horizon_division(self):
        import field_math
        from grid_math import evaluate_grid
        _, result = lower('float h=q9;float z=3/(uv_orig.y-1);ret=float3(z*h);', stage='composite')
        inputs = {'_qc': [0, 0, 0, 0], '_uv': [.5, 1]}
        np.testing.assert_array_equal(field_math.evaluate(result, inputs=inputs), [0, 0, 0])
        np.testing.assert_array_equal(evaluate_grid(result, batch_shape=(2,), inputs=inputs), np.zeros((2, 3)))

    def test_native_zero_guard_handles_mixed_lanes_in_both_operand_orders(self):
        from grid_math import evaluate_grid
        for expression in ['(1/bass)*mid', 'mid*(1/bass)']:
            _, result = lower('ret=float3('+expression+');')
            inputs = {'_c3': np.array([[0, 0, 0, 0], [2, 1, 0, 0]], dtype=np.float32)}
            np.testing.assert_array_equal(evaluate_grid(result, batch_shape=(2,), inputs=inputs), [[0, 0, 0], [.5, .5, .5]])

    def test_zero_guard_does_not_hide_missing_source_inputs_or_texture_reads(self):
        import field_math
        from grid_math import evaluate_grid
        _, result = lower('ret=float3(bass*0);')
        with self.assertRaisesRegex(field_math.UnresolvedMath, 'missing symbolic'):
            field_math.evaluate(result)
        with self.assertRaisesRegex(field_math.UnresolvedMath, 'missing symbolic'):
            evaluate_grid(result, batch_shape=(2,))
        _, texture = lower('ret=GetPixel(uv)*0;')
        with self.assertRaisesRegex(field_math.UnresolvedMath, 'texture function'):
            field_math.evaluate(texture, inputs={'_uv': [.5, .5, .5, .5]})

    def test_unmasked_horizon_division_stays_unresolved(self):
        import field_math
        _, result = lower('ret=float3(3/(uv_orig.y-1));', stage='composite')
        with self.assertRaisesRegex(field_math.UnresolvedMath, 'divide'):
            field_math.evaluate(result, inputs={'_uv': [.5, 1]})

    def test_logical_guard_preserves_scalar_short_circuit(self):
        import field_math
        _,result=lower('ret=(bass!=0 && 1/bass>0) ? float3(1) : float3(0);')
        np.testing.assert_allclose(field_math.evaluate(result,inputs={'_c3':[0,0,0,0]}),[0,0,0])

    def test_assignment_expression_returns_the_stored_declared_type(self):
        import field_math
        _,result=lower('int i=0;ret=float3(i=.9);')
        np.testing.assert_allclose(field_math.evaluate(result),[0,0,0])

    def test_compound_assignment_converts_operand_before_operation(self):
        import field_math
        _,result=lower('float x=-bass;int i=16777217;x+=i;ret=float3(x);')
        np.testing.assert_allclose(field_math.evaluate(result,inputs={'_c3':[16777216,0,0,0]}),[0,0,0])

    def test_comparison_uses_generator_common_scalar_type(self):
        import field_math
        _,result=lower('int i=16777217;ret=float3(i==bass);')
        np.testing.assert_allclose(field_math.evaluate(result,inputs={'_c3':[16777216,0,0,0]}),[1,1,1])

    def test_matrix_scalar_constructor_uses_native_zero_padding(self):
        import field_math
        model,result=lower('float2x2 m=float2x2(.5);ret=float3(m[0],0);')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(field_math.evaluate(result),[.5,0,0])

    def test_signed_integer_overflow_cannot_silently_wrap_into_a_prediction(self):
        import field_math
        _,result=lower('int i=2147483647;int b=i+1;ret=float3(b);')
        with self.assertRaises(field_math.UnresolvedMath):field_math.evaluate(result)

    def test_generator_arithmetic_converts_integer_operand_before_float_addition(self):
        import field_math
        _,result=lower('int i=16777217;ret=float3(i - bass);')
        np.testing.assert_allclose(field_math.evaluate(result,inputs={'_c3':[16777216,0,0,0]}),[0,0,0])

    @pytest.mark.historical_profile("legacy_pre30")
    def test_constant_uses_the_actual_renderer_decimal_literal(self):
        import field_math
        _,result=lower('ret=float3(16777216.);')
        np.testing.assert_allclose(field_math.evaluate(result),[16777200]*3,rtol=0,atol=0)

    def test_nonfinite_narrowing_cannot_be_returned_as_a_valid_value(self):
        import field_math
        with self.assertRaises(field_math.UnresolvedMath):
            field_math.evaluate(shader_fields.Field('constant',dtype='float',detail={'value':1e100}))

    def test_helper_reads_lexical_global_and_casts_declared_types(self):
        import field_math
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'
            'comp_1=`int g=1.9;int f(){return .9;}float h(){return g;}\n'
            'comp_2=`shader_body {float g=2;ret=float3(h(),f(),g);}\n')['sections']['comp_']['tree']
        model=shader_fields.ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_allclose(field_math.evaluate(result),[1,0,2])

    def test_rotated_ridge_and_two_age_feedback_are_recovered_from_native_source(self):
        import field_math
        body='''float2 p=(uv-.5)*aspect.xy;
            float theta=lum(tex2D(sampler_noise_hq,0.001*time))*3.14;
            float2 r=mul(p,float2x2(cos(theta),-sin(theta),sin(theta),cos(theta)));
            float stripe=.2/(sqrt(r.y)+.2);
            ret=.99*(.667*(GetPixel(uv)+.5*GetPixel(uv))
                -.03*GetBlur1(uv)+.018+.04*stripe)-.04;'''
        for source in [body,body.replace('stripe','renamed_seed').replace('theta','renamed_angle')]:
            model,result=lower(source)
            self.assertTrue(model.complete,model.unknown)
            inputs={'_uv':[.5,.5,0,0],'_c0':[1,.5625,1,1/.5625],
                    '_c2':[4,0,0,0],'_c5':[1,0,1,0]}
            def response(uv,angle=0,recent=0,older=0):
                uniforms={**inputs,'_uv':[*uv,0,0]}
                def sample(detail,coordinate):
                    # The pinned lum macro weights sum to 1.10, not 1.
                    if detail['sampler']=='sampler_noise_hq':return [angle/(3.14*1.10)]*4
                    if detail['sampler']=='sampler_main':
                        self.assertEqual(detail['frame'],2);return [recent]*4
                    self.assertEqual(detail['frame'],1);return [older]*4
                return field_math.evaluate(result,inputs=uniforms,sample=sample)
            centre=response([.5,.5])
            self.assertAlmostEqual(float(centre[0]),.01742,places=6)
            self.assertAlmostEqual(float((response([.5,.5],recent=.1)-centre)[0])/.1,.990495,places=5)
            self.assertAlmostEqual(float((response([.5,.5],older=.1)-centre)[0])/.1,-.0297,places=5)
            np.testing.assert_allclose(response([.5,.52]),response([.5,.48]),atol=1e-7)
            self.assertGreater(response([.5,.52])[0],0)
            self.assertLess(response([.5,.6])[0],0)
            # A quarter turn changes the narrow normal from y to x.
            self.assertGreater(response([.51,.8],math.pi/2)[0],0)
            self.assertLess(response([.6,.51],math.pi/2)[0],0)

    def test_row_vector_rotation(self):
        import field_math
        model,result=lower('float2x2 m=float2x2(cos(bass),-sin(bass),sin(bass),cos(bass)); ret=float3(mul(float2(1,0),m),0);')
        for angle,expected in [(0,[1,0,0]),(math.pi/2,[0,-1,0])]:
            actual=field_math.evaluate(result,inputs={'_c3':[angle,0,0,0]})
            np.testing.assert_allclose(actual,expected,atol=1e-6)

    def test_bare_matrix_multiplication_uses_generator_linear_product(self):
        import field_math
        model,result=lower('float2x2 m=float2x2(1,2,3,4)*float2x2(5,6,7,8);ret=float3(m[0],0);')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(field_math.evaluate(result),[19,22,0])

    def test_pinned_floating_remainder_and_fmod_use_glsl_mod(self):
        import field_math
        _,result=lower('float b=-3;ret=float3(b%2,fmod(b,2),0);')
        np.testing.assert_allclose(field_math.evaluate(result),[1,1,0])

    def test_scalar_splats_and_implicit_vector_truncation_are_typed(self):
        import field_math
        _,result=lower('float3 colour=.2; colour+=dot(float4(1,2,3,99),float3(1,1,1)); ret=colour;')
        np.testing.assert_allclose(field_math.evaluate(result),[6.2,6.2,6.2],atol=1e-6)

    def test_projectm_square_root_uses_absolute_value_for_negative_inputs(self):
        import field_math
        _,result=lower('ret=float3(.2/(sqrt(bass)+.2));')
        for value in [-.01,.01]:
            np.testing.assert_allclose(field_math.evaluate(result,inputs={'_c3':[value,0,0,0]}),[2/3]*3,atol=1e-6)

    def test_projectm_pow_literal_one_retains_sign_but_variable_one_uses_absolute_base(self):
        import field_math
        _,literal=lower('ret=float3(pow(bass,1));')
        _,variable=lower('ret=float3(pow(bass,mid));')
        inputs={'_c3':[-2,1,0,0]}
        np.testing.assert_allclose(field_math.evaluate(literal,inputs=inputs),[-2]*3)
        np.testing.assert_allclose(field_math.evaluate(variable,inputs=inputs),[2]*3)

    def test_zero_log_domain_is_unresolved_not_a_fabricated_colour(self):
        import field_math
        _,result=lower('ret=float3(log(bass));')
        with self.assertRaisesRegex(field_math.UnresolvedMath,'log'):
            field_math.evaluate(result,inputs={'_c3':[0,0,0,0]})

    def test_conditional_evaluates_only_selected_domain(self):
        import field_math
        _,result=lower('ret=bass>0 ? float3(sqrt(bass)) : float3(0);')
        np.testing.assert_allclose(field_math.evaluate(result,inputs={'_c3':[-1,0,0,0]}),[0,0,0])

    def test_swizzle_write_preserves_other_components(self):
        import field_math
        _,result=lower('ret=float3(1,2,3);ret.yx=float2(7,8);')
        np.testing.assert_allclose(field_math.evaluate(result),[8,7,3])

    def test_texture_callback_receives_history_and_exact_stencil_coordinates(self):
        import field_math
        _,result=lower('ret=tex2D(sampler_main,uv+float2(.004,0)).xyz-tex2D(sampler_blur1,uv-float2(.004,0)).xyz;')
        seen=[]
        def sample(detail,coordinates):
            seen.append((detail['frame'],coordinates.copy()))
            return [detail['frame']]*4
        np.testing.assert_allclose(field_math.evaluate(result,inputs={'_uv':[.5,.5,0,0]},sample=sample),[1,1,1])
        self.assertEqual([s[0] for s in seen],[2,1])
        np.testing.assert_allclose(seen[0][1],[.504,.5],atol=1e-7)
        np.testing.assert_allclose(seen[1][1],[.496,.5],atol=1e-7)


if __name__=='__main__':unittest.main()
