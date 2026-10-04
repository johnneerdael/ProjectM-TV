package nl.neerdael.projectm.corecorpus;

import android.app.Instrumentation;
import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.opengl.EGL14;
import android.opengl.EGLConfig;
import android.opengl.EGLContext;
import android.opengl.EGLDisplay;
import android.opengl.EGLSurface;
import android.os.Build;
import android.os.Bundle;
import android.os.SystemClock;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import org.json.*;
import nl.neerdael.projectm.core.ProjectMJNI;

/** One job per fresh process. Calls the production core JNI; owns only EGL, input and readback. */
public final class CorpusInstrumentation extends Instrumentation {
    private String requestPath;
    @Override public void onCreate(Bundle args) { super.onCreate(args); requestPath = args.getString("job"); start(); }
    private static void check(boolean ok, String reason) { if (!ok) throw new IllegalStateException(reason); }
    private static byte[] read(InputStream stream) throws Exception {
        try (InputStream input=stream; ByteArrayOutputStream out=new ByteArrayOutputStream()) {
            byte[] buffer=new byte[65536]; int count;
            while ((count=input.read(buffer)) != -1) out.write(buffer,0,count);
            return out.toByteArray();
        }
    }
    private static String hex(byte[] bytes) {
        char[] chars=new char[bytes.length*2]; char[] digits="0123456789abcdef".toCharArray();
        for (int i=0;i<bytes.length;i++) { chars[i*2]=digits[(bytes[i]&255)>>>4]; chars[i*2+1]=digits[bytes[i]&15]; }
        return new String(chars);
    }
    private static String sha(byte[] bytes) throws Exception { return hex(MessageDigest.getInstance("SHA-256").digest(bytes)); }
    private static String shaFile(File path) throws Exception {
        MessageDigest digest=MessageDigest.getInstance("SHA-256");
        try (InputStream input=new FileInputStream(path)) { byte[] buffer=new byte[65536]; int n; while ((n=input.read(buffer))!=-1) digest.update(buffer,0,n); }
        return hex(digest.digest());
    }
    private static void write(File path, byte[] bytes) throws Exception { try (FileOutputStream out=new FileOutputStream(path)) { out.write(bytes); out.getFD().sync(); } }
    private static void atomic(File path, JSONObject object) throws Exception {
        File temp=new File(path.getParentFile(),path.getName()+".tmp");
        write(temp,(object.toString()+"\n").getBytes(StandardCharsets.UTF_8));
        check(temp.renameTo(path),"atomic result rename failed");
    }
    private static JSONObject thumbnail(File output,int frame,byte[] rgb,int width,int height) throws Exception {
        int[] argb=new int[width*height];long red=0,green=0,blue=0,black=0,bright=0,clipped=0;
        for(int y=0;y<height;y++)for(int x=0;x<width;x++){
            int offset=(y*width+x)*3,r=rgb[offset]&255,g=rgb[offset+1]&255,b=rgb[offset+2]&255;
            red+=r;green+=g;blue+=b;int max=Math.max(r,Math.max(g,b));if(max<=2)black++;if(max>=230)bright++;if(max==255)clipped++;
            argb[(height-1-y)*width+x]=0xff000000|(r<<16)|(g<<8)|b;
        }
        Bitmap full=Bitmap.createBitmap(argb,width,height,Bitmap.Config.ARGB_8888);
        Bitmap small=Bitmap.createScaledBitmap(full,256,144,true);ByteArrayOutputStream png=new ByteArrayOutputStream();
        check(small.compress(Bitmap.CompressFormat.PNG,100,png),"thumbnail encoding failed");
        byte[] bytes=png.toByteArray();String name=String.format(Locale.ROOT,"frame-%04d.png",frame);write(new File(output,name),bytes);
        small.recycle();if(full!=small)full.recycle();double pixels=(double)width*height;
        JSONObject metrics=new JSONObject().put("native_rgb_mean",new JSONArray(new double[]{red/(255*pixels),green/(255*pixels),blue/(255*pixels)}))
            .put("native_luma_mean",(red*.2126+green*.7152+blue*.0722)/(255*pixels))
            .put("native_black_fraction",black/pixels).put("native_bright_fraction",bright/pixels).put("native_clipped_fraction",clipped/pixels);
        return new JSONObject().put("thumbnail_path",name).put("thumbnail_sha256",sha(bytes)).put("thumbnail_bytes",bytes.length).put("metrics",metrics);
    }
    @Override public void onStart() {
        Bundle returned=new Bundle(); JSONObject result=new JSONObject(); File output=null;
        EGLDisplay display=EGL14.EGL_NO_DISPLAY; EGLContext eglContext=EGL14.EGL_NO_CONTEXT; EGLSurface surface=EGL14.EGL_NO_SURFACE;
        boolean coreCreated=false; long wallStart=SystemClock.elapsedRealtime();
        try {
            check(requestPath!=null,"missing job path"); Context context=getTargetContext();
            JSONObject job=new JSONObject(new String(read(new FileInputStream(requestPath)),StandardCharsets.UTF_8));
            check(job.getInt("schema_version")==2,"unsupported request schema");
            String id=job.getString("job_id"), name=job.getString("preset_filename");
            check(id.matches("[a-f0-9]{64}"),"job_id must be SHA256");
            check(!name.contains("/")&&!name.contains("\\")&&!name.contains("\n")&&!name.contains("\r"),"invalid preset filename");
            output=new File(job.getString("output_directory"));
            String sandbox=context.getExternalFilesDir(null).getCanonicalPath()+File.separator;
            check(output.getCanonicalPath().startsWith(sandbox),"output is outside isolated app external-files directory");
            check(output.mkdirs()||output.isDirectory(),"cannot create output directory");
            check(!new File(output,"result.json").exists(),"job output already terminal; use a fresh job directory");
            result.put("job_id",id).put("schema_version",2).put("status","failed").put("protocol_sha256",job.getString("protocol_sha256"))
                .put("pid",android.os.Process.myPid()).put("started_unix_ms",System.currentTimeMillis());
            int width=job.getInt("width"), height=job.getInt("height"), fps=job.getInt("fps");
            int warmup=job.getInt("warmup_frames"), measurement=job.getInt("measurement_frames"), total=warmup+measurement;
            check(width>0&&height>0&&width<=4096&&height<=4096&&(fps==30||fps==60)&&warmup>=0&&measurement>0&&total<=3600,"invalid render configuration");
            result.put("width",width).put("height",height).put("fps",fps).put("preset_filename",name).put("pixel_format","RGB8").put("row_order","bottom_to_top")
                .put("seed",job.getInt("seed")).put("capture_mode",job.getString("capture_mode")).put("capture_frames",job.getJSONArray("capture_frames"))
                .put("rendered_frames",0).put("captured_frames",0).put("selected_files",new JSONArray());
            byte[] preset=read(context.getAssets().open("presets/"+name));
            check(sha(preset).equals(job.getString("preset_sha256")),"packaged requested preset checksum mismatch");
            result.put("requested_preset_sha256",sha(preset));
            byte[] input=read(new FileInputStream(job.getString("pcm_uint8_path")));
            check(sha(input).equals(job.getString("pcm_uint8_sha256")),"uint8 PCM checksum mismatch");
            int block=44100/fps; check(input.length==total*block,"PCM does not cover every complete frame");
            result.put("pcm_uint8_sha256",sha(input)).put("pcm_samples_per_frame",block);
            String index=new String(read(context.getAssets().open("presets.idx")),StandardCharsets.UTF_8);
            ArrayList<String> members=new ArrayList<>(); StringBuilder skip=new StringBuilder();
            for (String row:index.split("\n")) { String member=row.replace("\r","").split("\t")[0]; if (member.isEmpty()) continue; members.add(member); if (!member.equals(name)) skip.append(member).append('\n'); }
            check(members.size()==9606&&new HashSet<>(members).size()==9606&&members.contains(name),"complete APK preset index mismatch");
            File privateJob=new File(context.getFilesDir(),"jobs/"+id); check(privateJob.mkdirs()||privateJob.isDirectory(),"private job directory unavailable");
            File skipPath=new File(privateJob,"skip.txt"); byte[] mask=skip.toString().getBytes(StandardCharsets.UTF_8); write(skipPath,mask);
            write(new File(skipPath.toString()+".blank"),new byte[0]);
            result.put("packaged_presets",members.size()).put("skip_mask_sha256",sha(mask));
            JSONObject identity=new JSONObject(new String(read(context.getAssets().open("backend-identity.json")),StandardCharsets.UTF_8));
            result.put("backend_identity",identity).put("core_sha256",shaFile(new File(context.getApplicationInfo().nativeLibraryDir,"libprojectmtv.so")));
            result.put("android_fingerprint",Build.FINGERPRINT).put("abi",Build.SUPPORTED_ABIS[0]);
            LabBridge.configureSeed(job.getInt("seed")); LabBridge.setClock(0);
            File textures=new File(context.getFilesDir(),"textures");
            ProjectMJNI.init(context.getAssets(),skipPath.toString(),textures.toString());
            long readyDeadline=SystemClock.elapsedRealtime()+60000;
            while (ProjectMJNI.getPresetCount()!=1&&SystemClock.elapsedRealtime()<readyDeadline) SystemClock.sleep(10);
            check(ProjectMJNI.getPresetCount()==1,"index did not become ready with exactly one eligible preset");
            result.put("eligible_count",1);
            ProjectMJNI.setAutoChange(false); ProjectMJNI.setBeatCuts(false); ProjectMJNI.setBlankDetection(false);
            ProjectMJNI.setMusicCategory("all"); ProjectMJNI.setMeshSize(48,32); ProjectMJNI.setPresetDuration(3600);
            ProjectMJNI.setSoftCutDuration(0); ProjectMJNI.setTransitionMode(ProjectMJNI.TRANSITION_CLASSIC,false);
            ProjectMJNI.onMemoryPressure();
            result.put("prewarm_policy","actual onMemoryPressure 20-second pause; logical job must remain below20s");
            check(total/(double)fps<20,"prewarm pause would expire; split long protocol or review deterministic policy");
            display=EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY); int[] version=new int[2];
            check(display!=EGL14.EGL_NO_DISPLAY&&EGL14.eglInitialize(display,version,0,version,1),"EGL initialize failed");
            EGLConfig[] configs=new EGLConfig[1]; int[] count=new int[1];
            int[] attributes={EGL14.EGL_RENDERABLE_TYPE,0x40,EGL14.EGL_SURFACE_TYPE,EGL14.EGL_PBUFFER_BIT,
                EGL14.EGL_RED_SIZE,8,EGL14.EGL_GREEN_SIZE,8,EGL14.EGL_BLUE_SIZE,8,EGL14.EGL_ALPHA_SIZE,8,EGL14.EGL_NONE};
            check(EGL14.eglChooseConfig(display,attributes,0,configs,0,1,count,0)&&count[0]>0,"no RGBA8888 GLES3 pbuffer config");
            for (int attr:new int[]{EGL14.EGL_MAX_PBUFFER_WIDTH,EGL14.EGL_MAX_PBUFFER_HEIGHT,EGL14.EGL_MAX_PBUFFER_PIXELS}) {
                int[] value=new int[1]; check(EGL14.eglGetConfigAttrib(display,configs[0],attr,value,0),"EGL config query failed"); result.put("egl_limit_"+attr,value[0]);
                check(attr==EGL14.EGL_MAX_PBUFFER_WIDTH?width<=value[0]:attr==EGL14.EGL_MAX_PBUFFER_HEIGHT?height<=value[0]:(long)width*height<=value[0],"requested pbuffer exceeds EGL limit");
            }
            eglContext=EGL14.eglCreateContext(display,configs[0],EGL14.EGL_NO_CONTEXT,new int[]{EGL14.EGL_CONTEXT_CLIENT_VERSION,3,EGL14.EGL_NONE},0);
            surface=EGL14.eglCreatePbufferSurface(display,configs[0],new int[]{EGL14.EGL_WIDTH,width,EGL14.EGL_HEIGHT,height,EGL14.EGL_NONE},0);
            check(eglContext!=EGL14.EGL_NO_CONTEXT&&surface!=EGL14.EGL_NO_SURFACE&&EGL14.eglMakeCurrent(display,surface,surface,eglContext),"EGL pbuffer/context creation failed");
            int[] dimension=new int[1]; EGL14.eglQuerySurface(display,surface,EGL14.EGL_WIDTH,dimension,0); check(dimension[0]==width,"pbuffer width changed"); EGL14.eglQuerySurface(display,surface,EGL14.EGL_HEIGHT,dimension,0);check(dimension[0]==height,"pbuffer height changed");
            String[] gl=LabBridge.glInfo().split("\n",3);check(gl.length==3,"incomplete GL identity");
            result.put("gl_vendor",gl[0]).put("gl_renderer",gl[1]).put("gl_version",gl[2]).put("egl_version",version[0]+"."+version[1]);
            LabBridge.clearDefaultFramebuffer();check(LabBridge.glError()==0,"initial default-framebuffer clear failed");
            result.put("initial_default_framebuffer","RGBA black(0,0,0,1) cleared once before core surface creation");
            ProjectMJNI.onSurfaceCreated();coreCreated=true;ProjectMJNI.onSurfaceChanged(width,height);
            check(LabBridge.glError()==0,"core surface setup emitted GL error");
            Set<Integer> selected=new HashSet<>(); JSONArray picks=job.getJSONArray("capture_frames");
            for(int i=0;i<picks.length();i++){int frame=picks.getInt(i);check(frame>=0&&frame<total,"capture index outside rendered frames");selected.add(frame);}
            String captureMode=job.getString("capture_mode");check(captureMode.equals("full")||captureMode.equals("selected"),"invalid capture mode");
            result.put("capture_mode",captureMode).put("capture_frames",picks).put("seed",job.getInt("seed")).put("rendered_frames",0);
            int readbacks=0;
            MessageDigest all=MessageDigest.getInstance("SHA-256");JSONArray captures=new JSONArray();int changeCounter=-1;
            try(BufferedWriter metadata=new BufferedWriter(new OutputStreamWriter(new FileOutputStream(new File(output,"frames.jsonl")),StandardCharsets.UTF_8))){
                byte[] audio=new byte[block];
                for(int frame=0;frame<total;frame++){
                    LabBridge.setClock((frame+1)/(double)fps);System.arraycopy(input,frame*block,audio,0,block);
                    LabBridge.prepareDefaultReadBuffer();check(LabBridge.glError()==0,"default read-buffer setup failed");
                    ProjectMJNI.addWaveform(audio,audio.length);ProjectMJNI.onDrawFrame();
                    String observed=ProjectMJNI.getCurrentPresetName();check(name.equals(observed),"requested preset failed or fallback occurred: observed="+observed);
                    int changes=ProjectMJNI.getPresetChangeCounter();if(changeCounter<0)changeCounter=changes;check(changes==changeCounter,"preset changed during measurement");
                    check(ProjectMJNI.getPresetCount()==1,"eligible set changed during job");check(LabBridge.glError()==0,"core frame emitted GL error at"+frame);
                    boolean captured=captureMode.equals("full")||selected.contains(frame);String frameHash=null;byte[] rgb=null;
                    if(captured){
                        byte[] rgba=LabBridge.captureRgba(width,height);check(rgba!=null&&rgba.length==width*height*4,"incomplete RGBA capture");check(LabBridge.glError()==0,"readback emitted GL error at"+frame);
                        rgb=new byte[width*height*3];for(int pixel=0;pixel<width*height;pixel++){rgb[pixel*3]=rgba[pixel*4];rgb[pixel*3+1]=rgba[pixel*4+1];rgb[pixel*3+2]=rgba[pixel*4+2];}
                        if(captureMode.equals("full"))all.update(rgb);frameHash=sha(rgb);readbacks++;
                    }
                    JSONObject row=new JSONObject().put("frame",frame).put("preset_filename",observed).put("change_counter",changes).put("sha256",frameHash==null?JSONObject.NULL:frameHash).put("captured",captured).put("pcm_bytes",audio.length);
                    metadata.write(row.toString());metadata.newLine();
                    if(selected.contains(frame)){
                        JSONObject artifact=thumbnail(output,frame,rgb,width,height).put("frame",frame).put("sha256",frameHash).put("bytes",rgb.length);
                        if(job.optBoolean("retain_native_frames",false)){String file=String.format(Locale.ROOT,"frame-%04d.rgb",frame);write(new File(output,file),rgb);artifact.put("path",file);}
                        captures.put(artifact);
                    }
                    result.put("rendered_frames",frame+1);
                }
            }
            if(captureMode.equals("full"))result.put("sha256_all_frames",hex(all.digest()));
            result.put("selected_files",captures).put("captured_frames",readbacks).put("thumbnail_protocol","RGB orientation flip; AndroidBitmap.createScaledBitmap256x144 filter=true bilinear; lossless PNG");
            result.put("frames_metadata_sha256",shaFile(new File(output,"frames.jsonl"))).put("status","success");
        }catch(Throwable error){try{result.put("status","failed").put("error",error.toString());}catch(Exception ignored){}returned.putString("stream","FAILED: "+error+"\n");}
        finally{
            try{if(coreCreated)ProjectMJNI.release();}catch(Throwable error){try{result.put("status","failed").put("cleanup_error",error.toString());}catch(Exception ignored){}}
            if(display!=EGL14.EGL_NO_DISPLAY){EGL14.eglMakeCurrent(display,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_SURFACE,EGL14.EGL_NO_CONTEXT);if(surface!=EGL14.EGL_NO_SURFACE)EGL14.eglDestroySurface(display,surface);if(eglContext!=EGL14.EGL_NO_CONTEXT)EGL14.eglDestroyContext(display,eglContext);EGL14.eglTerminate(display);}
            try{result.put("elapsed_wall_seconds",(SystemClock.elapsedRealtime()-wallStart)/1000.0);if(output!=null)atomic(new File(output,"result.json"),result);}catch(Exception error){returned.putString("stream","FAILED publishing: "+error+"\n");}
            returned.putString("result",result.toString());finish("success".equals(result.optString("status"))?Activity.RESULT_OK:Activity.RESULT_CANCELED,returned);
        }
    }
}
