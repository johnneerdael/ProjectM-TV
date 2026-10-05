import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import numpy as np


class NativeCompositeTest(unittest.TestCase):
    def test_python_mesh_matches_unchanged_native_cpu_bodies(self):
        from composite_mesh import make_mesh,vertex_colours
        from legacy_composite import corner_shades
        binary=Path(__file__).resolve().parents[2]/'build/milk-analyzer/native/milk-composite-inputs'
        self.assertTrue(binary.is_file(),'native composite CPU bridge not built')
        for width,height,time,offsets in [(512,288,0,[0]*4),(128,256,7.25,[1,2,3,4]),(255,143,10001.25,[.25,11,23,37])]:
            with self.subTest(viewport=(width,height)):
                with tempfile.TemporaryDirectory() as directory:
                    request=Path(directory)/'request.json'
                    request.write_text(json.dumps({'width':width,'height':height,'time':time,'hue_offsets':offsets}))
                    result=subprocess.run([str(binary),str(request)],check=True,capture_output=True,text=True)
                    native=json.loads(result.stdout)
                self.assertEqual(native['render_context_time_bits'],32)
                self.assertEqual(len(native['render_context_source_sha256']),64)
                mesh=make_mesh(width,height)
                np.testing.assert_allclose(mesh['positions'].reshape(-1,2),native['positions'],atol=2e-7,rtol=0)
                np.testing.assert_allclose(mesh['uv'].reshape(-1,2),native['uv'],atol=2e-7,rtol=0)
                np.testing.assert_allclose(mesh['polar'].reshape(-1,2),native['polar'],atol=5e-7,rtol=0)
                np.testing.assert_array_equal(mesh['triangles'].reshape(-1),native['indices'])
                colors=vertex_colours(mesh,corner_shades(time,offsets))
                np.testing.assert_allclose(colors.reshape(-1,4),native['colours'],atol=3e-7,rtol=0)


if __name__=='__main__':unittest.main()
