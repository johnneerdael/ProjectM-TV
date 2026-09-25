package com.example.projectm.visualizer;

import android.annotation.TargetApi;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioPlaybackCaptureConfiguration;
import android.media.AudioRecord;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;

/**
 * "Media capture" audio source (Android 10+): records what media apps play and feeds it to the
 * engine. Needed where the Visualizer on the output mix hears nothing, e.g. a SHIELD with Dolby
 * output over HDMI eARC: Android attaches output-mix effects to an idle output there.
 *
 * Only audio with USAGE_MEDIA is captured, so notification, system and assistant sounds never
 * reach the visuals. Android requires a foreground service of type mediaProjection, with a
 * notification, while capturing.
 */
@TargetApi(29)
public class AudioCaptureService extends Service {
    private static final String TAG = "ProjectMTV";
    static final String EXTRA_RESULT_CODE = "result_code";
    static final String EXTRA_RESULT_DATA = "result_data";
    private static final String CHANNEL_ID = "audio_capture";
    private static final int NOTIFICATION_ID = 1;
    private static final int SAMPLE_RATE = 48000;
    private static final int CHANNELS = 2;
    // About the size of the buffers the Visualizer normalizes (768-1536 frames on the SHIELD).
    private static final int BLOCK_FRAMES = 1024;

    /** Told on the main thread when capture starts or stops. */
    interface Listener {
        void onCaptureStateChanged(boolean running);
    }

    static volatile Listener listener;
    /** False while the activity is paused: keep capturing, but don't feed the engine. */
    static volatile boolean feeding = true;

    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private MediaProjection projection;
    private final MediaProjection.Callback projectionCallback = new MediaProjection.Callback() {
        @Override
        public void onStop() {
            Log.i(TAG, "Audio source: media capture stopped by the system");
            stopSelf();
        }
    };
    private AudioRecord record;
    private Thread reader;
    private volatile boolean running;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (reader != null || intent == null) return START_NOT_STICKY;
        // The service must be in the foreground before the projection is created (Android 14).
        startForeground(NOTIFICATION_ID, notification(), ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
        try {
            MediaProjectionManager manager = getSystemService(MediaProjectionManager.class);
            Intent data = intent.getParcelableExtra(EXTRA_RESULT_DATA);
            projection = data == null ? null
                    : manager.getMediaProjection(intent.getIntExtra(EXTRA_RESULT_CODE, 0), data);
            if (projection == null) throw new IllegalStateException("no media projection");
            projection.registerCallback(projectionCallback, mainHandler);
            record = createRecord(projection);
            record.startRecording();
            if (record.getRecordingState() != AudioRecord.RECORDSTATE_RECORDING) {
                throw new IllegalStateException("recording did not start");
            }
        } catch (RuntimeException e) {
            Log.e(TAG, "Audio source: media capture failed to start", e);
            stopSelf();
            return START_NOT_STICKY;
        }
        running = true;
        reader = new Thread(this::readLoop, "PlaybackCapture");
        reader.start();
        Log.i(TAG, "Audio source: media capture started (media apps only, " + SAMPLE_RATE + " Hz)");
        notifyListener(true);
        return START_NOT_STICKY;
    }

    private static AudioRecord createRecord(MediaProjection projection) {
        AudioPlaybackCaptureConfiguration config = new AudioPlaybackCaptureConfiguration.Builder(projection)
                .addMatchingUsage(AudioAttributes.USAGE_MEDIA)
                .build();
        AudioFormat format = new AudioFormat.Builder()
                .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                .setSampleRate(SAMPLE_RATE)
                .setChannelMask(AudioFormat.CHANNEL_IN_STEREO)
                .build();
        int minBytes = AudioRecord.getMinBufferSize(SAMPLE_RATE, AudioFormat.CHANNEL_IN_STEREO,
                AudioFormat.ENCODING_PCM_16BIT);
        return new AudioRecord.Builder()
                .setAudioFormat(format)
                .setBufferSizeInBytes(Math.max(minBytes, BLOCK_FRAMES * CHANNELS * 2 * 4))
                .setAudioPlaybackCaptureConfig(config)
                .build();
    }

    private void readLoop() {
        android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_AUDIO);
        short[] pcm = new short[BLOCK_FRAMES * CHANNELS];
        byte[] waveform = new byte[BLOCK_FRAMES];
        while (running) {
            int read = record.read(pcm, 0, pcm.length);
            if (read < 0) {
                if (running) {
                    Log.e(TAG, "Audio source: media capture read error " + read);
                    mainHandler.post(this::stopSelf);
                }
                return;
            }
            if (read == 0 || !feeding) continue;
            int frames = PcmConverter.toUnsignedMono8(pcm, read, CHANNELS, waveform);
            if (frames > 0) ProjectMJNI.addWaveform(waveform, frames);
        }
    }

    private Notification notification() {
        NotificationManager manager = getSystemService(NotificationManager.class);
        manager.createNotificationChannel(new NotificationChannel(CHANNEL_ID, "Audio capture",
                NotificationManager.IMPORTANCE_LOW));
        return new Notification.Builder(this, CHANNEL_ID)
                .setSmallIcon(R.drawable.ic_music_note)
                .setContentTitle(getString(R.string.app_name))
                .setContentText("Listening to media audio for the visuals")
                .setOngoing(true)
                .build();
    }

    private void notifyListener(boolean isRunning) {
        mainHandler.post(() -> {
            Listener l = listener;
            if (l != null) l.onCaptureStateChanged(isRunning);
        });
    }

    @Override
    public void onDestroy() {
        boolean wasRunning = running;
        running = false;
        if (record != null) {
            record.stop();  // unblocks read()
            try {
                if (reader != null) reader.join(500);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            record.release();
            record = null;
        }
        reader = null;
        if (projection != null) {
            projection.unregisterCallback(projectionCallback);
            projection.stop();
            projection = null;
        }
        if (wasRunning) Log.i(TAG, "Audio source: media capture ended");
        notifyListener(false);
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
