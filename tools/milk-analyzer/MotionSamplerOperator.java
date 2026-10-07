package nl.neerdael.projectm.analysis;
import android.opengl.*;
import java.nio.*;
import java.nio.file.*;
import org.json.*;
import nl.neerdael.projectm.core.ProjectMJNI;
public final class MotionSamplerOperator {
 static int shader(int kind,String source){int id=GLES30.glCreateShader(kind);GLES30.glShaderSource(id,source);GLES30.glCompileShader(id);int[] ok=new int[1];GLES30.glGetShaderiv(id,GLES30.GL_COMPILE_STATUS,ok,0);if(ok[0]!=1)throw new IllegalStateException(GLES30.glGetShaderInfoLog(id));return id;}
 static ByteBuffer input(String path){try {byte[] b=Files.readAllBytes(Paths.get(path));ByteBuffer out=ByteBuffer.allocateDirect(b.length).order(ByteOrder.LITTLE_ENDIAN);out.put(b).position(0);return out;}catch(Exception e){throw new IllegalArgumentException(e);}}
 static String sha(ByteBuffer buffer)throws Exception{java.security.MessageDigest digest=java.security.MessageDigest.getInstance("SHA-256");digest.update(buffer.duplicate());StringBuilder result=new StringBuilder();for(byte b:digest.digest())result.append(String.format("%02x",b&255));return result.toString();}
 public static void main(String[] args)throws Exception {
  if(args.length!=7)throw new IllegalArgumentException("LIB WIDTH HEIGHT MAP QUERY OUTPUT META");
  System.load(args[0]);long before=ProjectMJNI.getRenderedFrameSerial();if(before!=0)throw new IllegalStateException("Nonzero core frame serial");
  int w=Integer.parseInt(args[1]),h=Integer.parseInt(args[2]);ByteBuffer map=input(args[3]),queries=input(args[4]);
  if(w<1||h<1||w>1024||h>768||map.remaining()!=w*h*8||queries.remaining()<8||queries.remaining()%8!=0||queries.remaining()>3072*8)throw new IllegalArgumentException("Operator input shape");
  String mapHash=sha(map),queryHash=sha(queries);
  int count=queries.remaining()/8;
  EGLDisplay display=EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);int[] version=new int[2];if(!EGL14.eglInitialize(display,version,0,version,1))throw new IllegalStateException("EGL init");
  EGLConfig[] configs=new EGLConfig[1];int[] n=new int[1];int[] attrs={EGL14.EGL_SURFACE_TYPE,EGL14.EGL_PBUFFER_BIT,EGL14.EGL_RENDERABLE_TYPE,0x40,EGL14.EGL_RED_SIZE,8,EGL14.EGL_GREEN_SIZE,8,EGL14.EGL_BLUE_SIZE,8,EGL14.EGL_ALPHA_SIZE,8,EGL14.EGL_NONE};
  if(!EGL14.eglChooseConfig(display,attrs,0,configs,0,1,n,0)||n[0]!=1)throw new IllegalStateException("GLES3 config");
  EGLContext context=EGL14.eglCreateContext(display,configs[0],EGL14.EGL_NO_CONTEXT,new int[]{EGL14.EGL_CONTEXT_CLIENT_VERSION,3,EGL14.EGL_NONE},0);
  EGLSurface surface=EGL14.eglCreatePbufferSurface(display,configs[0],new int[]{EGL14.EGL_WIDTH,1,EGL14.EGL_HEIGHT,1,EGL14.EGL_NONE},0);
  if(!EGL14.eglMakeCurrent(display,surface,surface,context))throw new IllegalStateException("EGL current");
  int[] ids=new int[1];GLES30.glGenVertexArrays(1,ids,0);GLES30.glBindVertexArray(ids[0]);
  int[] tex=new int[1];GLES30.glGenTextures(1,tex,0);GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,tex[0]);GLES30.glTexImage2D(GLES30.GL_TEXTURE_2D,0,GLES30.GL_RG16F,w,h,0,GLES30.GL_RG,GLES30.GL_FLOAT,map.asFloatBuffer());
  GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MIN_FILTER,GLES30.GL_LINEAR);GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MAG_FILTER,GLES30.GL_LINEAR);GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_WRAP_S,GLES30.GL_CLAMP_TO_EDGE);GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_WRAP_T,GLES30.GL_CLAMP_TO_EDGE);
  String vs="#version 300 es\nprecision mediump float;layout(location=0) in vec2 q;uniform sampler2D warp_coordinates;out vec2 sampled;void main(){sampled=texture(warp_coordinates,q).xy;gl_Position=vec4(0,0,0,1);}";
  String fs="#version 300 es\nprecision mediump float;out vec4 color;void main(){color=vec4(0);}";
  int a=shader(GLES30.GL_VERTEX_SHADER,vs),b=shader(GLES30.GL_FRAGMENT_SHADER,fs),program=GLES30.glCreateProgram();GLES30.glAttachShader(program,a);GLES30.glAttachShader(program,b);GLES30.glTransformFeedbackVaryings(program,new String[]{"sampled"},GLES30.GL_INTERLEAVED_ATTRIBS);GLES30.glLinkProgram(program);int[] ok=new int[1];GLES30.glGetProgramiv(program,GLES30.GL_LINK_STATUS,ok,0);if(ok[0]!=1)throw new IllegalStateException(GLES30.glGetProgramInfoLog(program));GLES30.glUseProgram(program);GLES30.glUniform1i(GLES30.glGetUniformLocation(program,"warp_coordinates"),0);
  int[] buffers=new int[2];GLES30.glGenBuffers(2,buffers,0);GLES30.glBindBuffer(GLES30.GL_ARRAY_BUFFER,buffers[0]);GLES30.glBufferData(GLES30.GL_ARRAY_BUFFER,queries.remaining(),queries,GLES30.GL_STATIC_DRAW);GLES30.glEnableVertexAttribArray(0);GLES30.glVertexAttribPointer(0,2,GLES30.GL_FLOAT,false,8,0);
  GLES30.glBindBuffer(GLES30.GL_TRANSFORM_FEEDBACK_BUFFER,buffers[1]);GLES30.glBufferData(GLES30.GL_TRANSFORM_FEEDBACK_BUFFER,count*8,null,GLES30.GL_STATIC_READ);GLES30.glBindBufferBase(GLES30.GL_TRANSFORM_FEEDBACK_BUFFER,0,buffers[1]);GLES30.glEnable(GLES30.GL_RASTERIZER_DISCARD);GLES30.glBeginTransformFeedback(GLES30.GL_POINTS);GLES30.glDrawArrays(GLES30.GL_POINTS,0,count);GLES30.glEndTransformFeedback();GLES30.glDisable(GLES30.GL_RASTERIZER_DISCARD);
  ByteBuffer mapped=(ByteBuffer)GLES30.glMapBufferRange(GLES30.GL_TRANSFORM_FEEDBACK_BUFFER,0,count*8,GLES30.GL_MAP_READ_BIT);if(mapped==null)throw new IllegalStateException("TF map failed");byte[] output=new byte[count*8];mapped.get(output);if(!GLES30.glUnmapBuffer(GLES30.GL_TRANSFORM_FEEDBACK_BUFFER))throw new IllegalStateException("TF unmap failed");
  int err=GLES30.glGetError();if(err!=0)throw new IllegalStateException("GL error "+err);long after=ProjectMJNI.getRenderedFrameSerial();if(after!=0)throw new IllegalStateException("Core frame advanced");
  Files.write(Paths.get(args[5]),output);JSONObject meta=new JSONObject();meta.put("physical_map_sha256",mapHash);meta.put("input_queries_sha256",queryHash);meta.put("output_sha256",sha(ByteBuffer.wrap(output)));meta.put("basis","source-with-measured-operator");meta.put("operator","auxiliary-GLES300-vertex-RG16F-linear-clamp-transform-feedback-v1");meta.put("core_version",ProjectMJNI.getVersion());meta.put("core_frame_serial_before",before);meta.put("core_frame_serial_after",after);meta.put("preset_draws",0);meta.put("renderer",GLES30.glGetString(GLES30.GL_RENDERER));meta.put("vendor",GLES30.glGetString(GLES30.GL_VENDOR));meta.put("gl_version",GLES30.glGetString(GLES30.GL_VERSION));meta.put("vertex_shader",vs);meta.put("fragment_shader",fs);meta.put("width",w);meta.put("height",h);meta.put("queries",count);Files.write(Paths.get(args[6]),meta.toString().getBytes("UTF-8"));System.out.println(meta.toString());System.exit(0);
 }
}
