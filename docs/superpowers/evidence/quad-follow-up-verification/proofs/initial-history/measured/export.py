"""Re-digitize real CGL test reads; export diagnostic figures, never app screenshots."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import cv2
import numpy as np

HERE=Path(__file__).resolve().parent
REVIEW=HERE.parent
ROOT=REVIEW.parents[2]
fixture=(REVIEW/'TextureHistoryTest.cpp').read_text()
fixture=fixture.replace('#include <vector>','#include <vector>\n#include <fstream>\n#include <iostream>\n#include <cstdlib>')
dump=r'''
void DumpProofPixels(const std::vector<unsigned char>& pixels)
{
    const auto directory = std::getenv("PMX_PROOF_DIR");
    if (!directory) return;
    const auto test = ::testing::UnitTest::GetInstance()->current_test_info()->name();
    std::ofstream stream(std::string(directory) + "/" + test + ".rgba", std::ios::binary);
    stream.write(reinterpret_cast<const char*>(pixels.data()), pixels.size());
    std::cerr << "PROOF_PIXELS " << test << " nonzero="
              << std::count_if(pixels.begin(), pixels.end(), [](unsigned char v) { return v != 0; })
              << " bytes=" << pixels.size() << "\n";
}
'''
fixture=fixture.replace('GLuint lastClearFramebuffer{};',dump+'\nGLuint lastClearFramebuffer{};')
fixture=fixture.replace('        return pixels;','        DumpProofPixels(pixels);\n        return pixels;')
fixture=fixture.replace('    EXPECT_EQ(attachment, static_cast<GLint>(sentinel))',
    '    std::cerr << "PROOF_ATTACHMENT expected=" << sentinel << " actual=" << attachment\n'
    '              << " framebuffer_status=" << glCheckFramebufferStatus(GL_FRAMEBUFFER) << "\\n";\n'
    '    EXPECT_EQ(attachment, static_cast<GLint>(sentinel))')
fixture=fixture.replace('    EXPECT_EQ(pixels, paint)', '    DumpProofPixels(pixels);\n    EXPECT_EQ(pixels, paint)')
(HERE/'ReadbackProofTest.cpp').write_text(fixture)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
records=[]
for variant in ['red','green']:
    work=HERE/variant;work.mkdir(exist_ok=True)
    source=REVIEW/variant/'source'
    (work/'CMakeLists.txt').write_text(f'''cmake_minimum_required(VERSION 3.22)
project(ReadbackProof LANGUAGES CXX)
find_package(OpenGL REQUIRED)
find_package(GTest REQUIRED CONFIG)
add_executable(proof-test "{HERE/'ReadbackProofTest.cpp'}" "{source/'Renderer/Texture.cpp'}" "{source/'Renderer/Sampler.cpp'}")
target_compile_features(proof-test PRIVATE cxx_std_17)
target_compile_definitions(proof-test PRIVATE GL_SILENCE_DEPRECATION)
target_include_directories(proof-test PRIVATE "{source}")
target_link_libraries(proof-test PRIVATE GTest::gtest_main OpenGL::GL)
''')
    with (work/'build.log').open('w') as log:
        subprocess.run(['cmake','-S',str(work),'-B',str(work/'build'),'-DGTest_DIR=/opt/homebrew/lib/cmake/GTest'],check=True,stdout=log,stderr=subprocess.STDOUT)
        subprocess.run(['cmake','--build',str(work/'build'),'-j','4'],check=True,stdout=log,stderr=subprocess.STDOUT)
    result=subprocess.run([str(work/'build/proof-test')],capture_output=True,text=True,
                           env=dict(os.environ,PMX_PROOF_DIR=str(work)))
    (work/'test.log').write_text(result.stdout+result.stderr)
    assert result.returncode==(1 if variant=='red' else 0),result.stdout+result.stderr
    records.append({'variant':variant,'exit_code':result.returncode,
        'renderer_source':str((source/'Renderer/TextureAttachment.cpp').relative_to(ROOT)),
        'renderer_sha256':sha(source/'Renderer/TextureAttachment.cpp'),
        'fixture_sha256':sha(HERE/'ReadbackProofTest.cpp'),'log_sha256':sha(work/'test.log'),
        'raw_files':{p.name:sha(p) for p in sorted(work.glob('*.rgba'))}})

fresh_name='FreshColorHistoryIsTransparentBlackBeforeFirstRender'
collision_name='RecreatedContextDoesNotClearForeignFramebufferWithReusedName'
fresh=[np.fromfile(HERE/v/f'{fresh_name}.rgba',dtype=np.uint8).reshape(16,16,4) for v in ['red','green']]
assert np.all(fresh[0]==0x7b) and np.all(fresh[1]==0)
foreign=[np.fromfile(HERE/v/f'{collision_name}.rgba',dtype=np.uint8).reshape(16,16,4) for v in ['red','green']]
assert np.all(foreign[0]==0x45) and np.all(foreign[1]==0x45)
logs=[(HERE/v/'test.log').read_text() for v in ['red','green']]
assert 'PROOF_ATTACHMENT expected=1 actual=0' in logs[0]
assert 'PROOF_ATTACHMENT expected=1 actual=1' in logs[1]
assert 'framebuffer_status=36055' in logs[0]  # actual GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT
assert 'framebuffer_status=36053' in logs[1]  # actual GL_FRAMEBUFFER_COMPLETE

def text(image,s,x,y,size=.55,color=(35,35,35),thick=1):
    cv2.putText(image,s,(x,y),cv2.FONT_HERSHEY_SIMPLEX,size,color,thick,cv2.LINE_AA)
def figure(title,subtitle):
    im=np.full((850,1400,3),248,np.uint8)
    text(im,title,34,48,.92,thick=2)
    text(im,subtitle,34,82,.52)
    cv2.line(im,(34,98),(1366,98),(160,160,160),1)
    return im

im=figure('08 | Fresh color history starts with defined transparent black',
          'Actual macOS CGL renderer readback. Controlled allocator contents: 0x7b, RGBA8, 16 x 16. Not an app image.')
for n,(label,frame) in enumerate(zip(['Before: fresh storage was not initialized','After: fresh color attachment is cleared'],fresh)):
    x=40+n*700;text(im,label,x,137,.62,thick=2)
    grid=cv2.resize(frame[...,:3],(320,320),interpolation=cv2.INTER_NEAREST)
    im[158:478,x:x+320]=grid
    for line in range(17):
        cv2.line(im,(x+line*20,158),(x+line*20,478),(200,200,200),1)
        cv2.line(im,(x,158+line*20),(x+320,158+line*20),(200,200,200),1)
    text(im,f'Raw RGBA per pixel: {frame[0,0].tolist()}',x,511,.57)
    text(im,f'Nonzero bytes: {np.count_nonzero(frame)} / 1024',x,544,.66,thick=2)
    text(im,'Before first render; no shader or preset image substituted.',x,577,.44)
text(im,'Log evidence',40,634,.62,thick=2)
text(im,'RED: FreshColorHistoryIsTransparentBlackBeforeFirstRender FAILED; measured 1024 nonzero bytes.',40,671,.53)
text(im,'GREEN: same production initializer + minimal clear; measured 0 nonzero bytes; test PASSED.',40,706,.53)
text(im,'Caller read/draw FBO, clear colour, colour mask and scissor are preserved; pooled history remains black.',40,752,.48)
text(im,'Scope: renderer initialization proof. This does not claim the Mali startup outlier is resolved.',40,799,.50)
cv2.imwrite(str(HERE/'08-fresh-history-init.png'),im)

im=figure('09 | Color clear preserves ownership after context recreation',
          'Actual two-context CGL collision test. Foreign FBO uses the old cached name; sentinel texture is painted 0x45.')
for n,(label,attached) in enumerate(zip(['Before: cached helper drops foreign attachment','After: local scratch FBO preserves ownership'],[False,True])):
    x=40+n*700;text(im,label,x,139,.56,thick=2)
    cv2.rectangle(im,(x,168),(x+580,450),(75,75,75),2)
    text(im,'Foreign framebuffer',x+18,205,.69,thick=2)
    text(im,'Expected colour attachment: sentinel texture 1',x+18,247,.53)
    text(im,f'Actual attachment name: {1 if attached else 0}',x+18,293,.80,
         color=(35,115,35) if attached else (30,30,160),thick=2)
    text(im,'COMPLETE' if attached else 'INCOMPLETE: attachment detached',x+18,332,.58,
         color=(35,115,35) if attached else (30,30,160),thick=2)
    tile=cv2.resize(foreign[n][...,:3],(80,80),interpolation=cv2.INTER_NEAREST)
    im[350:430,x+18:x+98]=tile
    text(im,'Actual sentinel storage after clear: RGBA [69, 69, 69, 69]',x+110,379,.45)
    text(im,'Paint intact in both runs; ownership loss is the RED failure.',x+110,407,.43)
    text(im,'Read and draw bindings still point to the caller framebuffer.',x,494,.47)
text(im,'Log evidence',40,554,.65,thick=2)
text(im,'RED: PROOF_ATTACHMENT expected=1 actual=0; recreated-context test FAILED.',40,597,.56)
text(im,'GREEN: PROOF_ATTACHMENT expected=1 actual=1; recreated-context test PASSED.',40,638,.56)
text(im,'One local glGenFramebuffers/glDeleteFramebuffers pair per allocation-time clear; no per-frame pass.',40,699,.48)
text(im,'Focused GREEN: 5 passed, 0 skipped. Full isolated patches 1-28 host suite: 174 passed, 0 skipped.',40,747,.50)
text(im,'Scope: framebuffer ownership proof, not a preset screenshot or hardware-outlier attribution.',40,798,.50)
cv2.imwrite(str(HERE/'09-context-fbo-ownership.png'),im)

manifest={'schema_version':1,'kind':'real-CGL-controlled-renderer-diagnostic',
          'not_app_screenshots':True,'mali_outlier_resolution_claim':False,
          'code_patch_sha256':sha(REVIEW/'0028-initialize-fresh-color-history.patch'),
          'original_fixture_sha256':sha(REVIEW/'TextureHistoryTest.cpp'),
          'export_script_sha256':sha(Path(__file__)),
          'host_suite_log_sha256':sha(REVIEW/'host-suite/suite.log'),'runs':records,
          'images':[{ 'file':name,'sha256':sha(HERE/name)} for name in ['08-fresh-history-init.png','09-context-fbo-ownership.png']]}
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
