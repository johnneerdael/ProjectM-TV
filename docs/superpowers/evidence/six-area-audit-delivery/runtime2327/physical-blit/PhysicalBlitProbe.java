package nl.neerdael.projectm.analysis;

import android.opengl.*;
import java.io.*;
import java.nio.*;
import org.json.*;
import nl.neerdael.projectm.core.ProjectMJNI;

/** Isolated RGBA8 framebuffer operator, with unchanged full published core loaded. */
public final class PhysicalBlitProbe {
    static byte[] read(File file) throws Exception {
        if(file.length()>Integer.MAX_VALUE)throw new IllegalArgumentException("Oversized fixture");
        byte[] data=new byte[(int)file.length()];
        try(FileInputStream input=new FileInputStream(file)) {
            int offset=0;
            while(offset<data.length){int n=input.read(data,offset,data.length-offset);if(n<0)throw new IOException("Short fixture");offset+=n;}
        }
        return data;
    }
    static void require(boolean value,String message) { if(!value)throw new IllegalStateException(message); }
    public static void main(String[] args) throws Exception {
        if(args.length!=2)throw new IllegalArgumentException("CORE_LIBRARY WORKDIR");
        System.load(args[0]);
        long before=ProjectMJNI.getRenderedFrameSerial();require(before==0,"Core already rendered");
        File work=new File(args[1]);JSONObject config=new JSONObject(new String(read(new File(work,"cases.json")),"UTF-8"));
        int nw=config.getInt("native_width"),nh=config.getInt("native_height");
        int pw=config.getInt("physical_width"),ph=config.getInt("physical_height");
        require(nw==1920&&nh==1080&&pw==3840&&ph==2160,"Unexpected frozen dimensions");
        EGLDisplay display=EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);int[] version=new int[2];
        require(EGL14.eglInitialize(display,version,0,version,1),"EGL initialization");
        int[] attributes={EGL14.EGL_SURFACE_TYPE,EGL14.EGL_PBUFFER_BIT,EGL14.EGL_RENDERABLE_TYPE,0x40,
            EGL14.EGL_RED_SIZE,8,EGL14.EGL_GREEN_SIZE,8,EGL14.EGL_BLUE_SIZE,8,EGL14.EGL_ALPHA_SIZE,8,
            EGL14.EGL_DEPTH_SIZE,0,EGL14.EGL_STENCIL_SIZE,0,EGL14.EGL_SAMPLE_BUFFERS,0,EGL14.EGL_SAMPLES,0,EGL14.EGL_NONE};
        EGLConfig[] choices=new EGLConfig[1];int[] count=new int[1];
        require(EGL14.eglChooseConfig(display,attributes,0,choices,0,1,count,0)&&count[0]==1,"EGL config");
        JSONObject bits=new JSONObject();
        int[] keys={EGL14.EGL_RED_SIZE,EGL14.EGL_GREEN_SIZE,EGL14.EGL_BLUE_SIZE,EGL14.EGL_ALPHA_SIZE,EGL14.EGL_SAMPLES};
        String[] labels={"red","green","blue","alpha","samples"};
        for(int i=0;i<keys.length;i++){int[] value=new int[1];require(EGL14.eglGetConfigAttrib(display,choices[0],keys[i],value,0),"Config bit query");bits.put(labels[i],value[0]);require(value[0]==(i==4?0:8),"Unexpected framebuffer format");}
        EGLContext context=EGL14.eglCreateContext(display,choices[0],EGL14.EGL_NO_CONTEXT,
            new int[]{EGL14.EGL_CONTEXT_CLIENT_VERSION,3,EGL14.EGL_NONE},0);
        EGLSurface surface=EGL14.eglCreatePbufferSurface(display,choices[0],
            new int[]{EGL14.EGL_WIDTH,pw,EGL14.EGL_HEIGHT,ph,EGL14.EGL_NONE},0);
        require(EGL14.eglMakeCurrent(display,surface,surface,context),"EGL current");
        GLES30.glDisable(GLES30.GL_DITHER);GLES30.glDisable(GLES30.GL_BLEND);GLES30.glDisable(GLES30.GL_SCISSOR_TEST);
        GLES30.glColorMask(true,true,true,true);GLES30.glPixelStorei(GLES30.GL_PACK_ALIGNMENT,1);GLES30.glPixelStorei(GLES30.GL_UNPACK_ALIGNMENT,1);
        int[] texture=new int[1],fbo=new int[1];GLES30.glGenTextures(1,texture,0);GLES30.glGenFramebuffers(1,fbo,0);
        ByteBuffer input=ByteBuffer.allocateDirect(nw*nh*4),output=ByteBuffer.allocateDirect(pw*ph*4);
        byte[] result=new byte[pw*ph*4];JSONArray cases=config.getJSONArray("cases");
        for(int c=0;c<cases.length();c++) {
            JSONObject fixture=cases.getJSONObject(c);byte[] source=read(new File(work,fixture.getString("input_file")));
            require(source.length==input.capacity(),"Input length");input.clear();
            for(int y=nh-1;y>=0;y--)input.put(source,y*nw*4,nw*4);input.flip();
            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,texture[0]);
            GLES30.glTexImage2D(GLES30.GL_TEXTURE_2D,0,GLES30.GL_RGBA8,nw,nh,0,GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,input);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MIN_FILTER,GLES30.GL_LINEAR);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MAG_FILTER,GLES30.GL_LINEAR);
            GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,fbo[0]);
            GLES30.glFramebufferTexture2D(GLES30.GL_FRAMEBUFFER,GLES30.GL_COLOR_ATTACHMENT0,GLES30.GL_TEXTURE_2D,texture[0],0);
            require(GLES30.glCheckFramebufferStatus(GLES30.GL_FRAMEBUFFER)==GLES30.GL_FRAMEBUFFER_COMPLETE,"Source framebuffer");
            GLES30.glBindFramebuffer(GLES30.GL_READ_FRAMEBUFFER,fbo[0]);GLES30.glReadBuffer(GLES30.GL_COLOR_ATTACHMENT0);
            GLES30.glBindFramebuffer(GLES30.GL_DRAW_FRAMEBUFFER,0);GLES30.glDrawBuffers(1,new int[]{GLES30.GL_BACK},0);
            GLES30.glBlitFramebuffer(0,0,nw,nh,0,0,pw,ph,GLES30.GL_COLOR_BUFFER_BIT,GLES30.GL_LINEAR);
            GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,0);GLES30.glReadBuffer(GLES30.GL_BACK);output.clear();
            GLES30.glReadPixels(0,0,pw,ph,GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,output);
            require(GLES30.glGetError()==GLES30.GL_NO_ERROR,"GL blit/readback");
            for(int y=0;y<ph;y++){output.position((ph-1-y)*pw*4);output.get(result,y*pw*4,pw*4);}
            try(FileOutputStream file=new FileOutputStream(new File(work,fixture.getString("case")+"-actual.rgba.u8"))){file.write(result);}
        }
        require(ProjectMJNI.getRenderedFrameSerial()==0,"Operator advanced preset frames");
        JSONObject metadata=new JSONObject();metadata.put("scope","Separate physical GL_LINEAR operator; no actual JNI transition/preset draws or score credit");
        metadata.put("core_version",ProjectMJNI.getVersion());metadata.put("core_frame_serial_before",before);metadata.put("core_frame_serial_after",ProjectMJNI.getRenderedFrameSerial());
        metadata.put("renderer",GLES30.glGetString(GLES30.GL_RENDERER));metadata.put("gl_version",GLES30.glGetString(GLES30.GL_VERSION));
        metadata.put("source_size",new JSONArray(new int[]{nw,nh}));metadata.put("destination_size",new JSONArray(new int[]{pw,ph}));metadata.put("destination_config_bits",bits);
        try(FileOutputStream file=new FileOutputStream(new File(work,"metadata.json"))){file.write(metadata.toString(2).getBytes("UTF-8"));}
        GLES30.glDeleteFramebuffers(1,fbo,0);GLES30.glDeleteTextures(1,texture,0);
        EGL14.eglMakeCurrent(display,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_CONTEXT);
        EGL14.eglDestroySurface(display,surface);EGL14.eglDestroyContext(display,context);EGL14.eglTerminate(display);
        System.exit(0);
    }
}
