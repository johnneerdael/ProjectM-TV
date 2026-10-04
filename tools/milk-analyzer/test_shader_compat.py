import importlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ShaderCompatibilityTest(unittest.TestCase):
    def check(self, code, stage='composite', profile='glsl330'):
        module = importlib.import_module('shader_compat')
        return module.check_shader(code, stage=stage, profile=profile,
            translator=ROOT/'build/milk-analyzer/native/milk-shader-translate',
            validator=Path('/opt/homebrew/bin/glslangValidator'),
            samplers={'sampler_main': 'sampler2D'}, texture_sizes=['texsize_main'])

    def test_reading_uniforms_compiles_in_both_target_profiles(self):
        for profile in ('glsl330', 'gles300'):
            with self.subTest(profile=profile):
                result = self.check('shader_body {ret=tex2D(sampler_main,uv).xyz*bass+q1;}', profile=profile)
                self.assertTrue(result['offline_accepted'], result)
                self.assertEqual(result['predicted_stage'], 'custom_composite')
                self.assertFalse(result['native_driver_verified'])

    def test_composite_unrewritten_uniform_increment_selects_passthrough_fallback(self):
        for profile in ('glsl330', 'gles300'):
            with self.subTest(profile=profile):
                result = self.check('shader_body {q18++;ret=q18;}', profile=profile)
                self.assertFalse(result['offline_accepted'])
                self.assertEqual(result['predicted_stage'], 'default_composite')
                self.assertIn('uniform', result['compiler_diagnostics'].lower())

    def test_warp_unrewritten_uniform_increment_selects_fixed_warp(self):
        result = self.check('shader_body {bass++;ret=float3(bass);}', stage='warp')
        self.assertFalse(result['offline_accepted'])
        self.assertEqual(result['predicted_stage'], 'fixed_warp')

    def test_native_uniform_assignment_is_rewritten_to_uninitialized_local(self):
        result = self.check('shader_body {q18=1;ret=q18;}')
        self.assertTrue(result['offline_accepted'], result)
        self.assertIn('vec4 new_qe;', result['translation']['glsl'])
        self.assertNotIn('new_qe = _qe', result['translation']['glsl'])

    def test_local_shadow_does_not_become_uniform_write(self):
        result = self.check('shader_body {float local=1;local=2;ret=float3(local);}')
        self.assertTrue(result['offline_accepted'], result)

    def test_target_parser_does_not_get_reader_language_extensions(self):
        result = self.check('shader_body {ret=all(float2(1,1));}')
        self.assertFalse(result['offline_accepted'])
        self.assertEqual(result['translation']['status'], 'rejected')

    def test_native_sampler_declaration_removal_is_preserved(self):
        result = self.check('sampler2D sampler_main;\nshader_body {ret=tex2D(sampler_main,uv).xyz;}')
        self.assertTrue(result['offline_accepted'], result)

    def test_profile_and_stage_are_explicit(self):
        with self.assertRaisesRegex(ValueError, 'profile'):
            self.check('shader_body {ret=0;}', profile='auto')
        with self.assertRaisesRegex(ValueError, 'stage'):
            self.check('shader_body {ret=0;}', stage='auto')

    def test_native_matrix_operator_and_scalar_initializer_rules_compile(self):
        code='shader_body {float2x2 a=float2x2(1,2,3,4);float2x2 b=a*2.;ret=float3(b[0],0);}'
        for profile in ('glsl330','gles300'):
            with self.subTest(profile=profile):
                result=self.check(code,profile=profile)
                self.assertTrue(result['offline_accepted'],result)
                glsl=result['translation']['glsl']
                self.assertIn('return x * y;',glsl)
                self.assertIn('mat2 (float(2))',glsl)
                zero=self.check('shader_body {float2x2 a=.5;ret=float3(a[0],0);}',profile=profile)
                self.assertTrue(zero['offline_accepted'],zero)
                self.assertIn('return mat2(a,0,0,0);',zero['translation']['glsl'])

    def test_native_array_constructor_rejects_flat_grouping_and_partial_initializers(self):
        fixtures=[('float a[3]={1.,2.,3.};ret=a[0];',True),
                  ('float2 a[2]={float2(1,2),float2(3,4)};ret=a[0].x;',True),
                  ('float2 a[2]={1,2,3,4};ret=a[0].x;',False),
                  ('float a[3]={1};ret=a[0];',False)]
        for profile in ('glsl330','gles300'):
            for code,accepted in fixtures:
                with self.subTest(profile=profile,code=code):
                    result=self.check('shader_body {'+code+'}',profile=profile)
                    self.assertEqual(result['offline_accepted'],accepted,result)

    def test_float_array_integer_initializer_depends_on_target_profile(self):
        code='shader_body {float a[3]={1,2,3};ret=a[0];}'
        self.assertTrue(self.check(code,profile='glsl330')['offline_accepted'])
        self.assertFalse(self.check(code,profile='gles300')['offline_accepted'])

    def test_native_translator_process_failure_is_unknown_not_fallback(self):
        result=self.check('float f(float a[]){return a[0];}'
                          'shader_body {float b[3]={1.,2.,3.};ret=f(b);}')
        self.assertEqual(result['translation']['status'],'unknown')
        self.assertIsNone(result['offline_accepted'])
        self.assertIsNone(result['predicted_stage'])


if __name__ == '__main__':
    unittest.main()
