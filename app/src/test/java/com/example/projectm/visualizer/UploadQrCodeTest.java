package com.example.projectm.visualizer;

import com.google.zxing.BinaryBitmap;
import com.google.zxing.RGBLuminanceSource;
import com.google.zxing.common.HybridBinarizer;
import com.google.zxing.qrcode.QRCodeReader;
import org.junit.Test;
import static org.junit.Assert.*;

public class UploadQrCodeTest {
    @Test public void displayedPixelsDecodeToTheExactUploadSession() throws Exception {
        String address = "http://192.168.100.200:65535/34dd9412461dc5942727b84681564628";
        for (int size : new int[]{240, 480, 960}) {
            int[] pixels = UploadQrCode.pixels(address, size);
            assertEquals(size * size, pixels.length);
            assertEquals(address, new QRCodeReader().decode(new BinaryBitmap(new HybridBinarizer(
                    new RGBLuminanceSource(size, size, pixels)))).getText());
            for (int x = 0; x < size; x++) {
                assertEquals(0xffffffff, pixels[x]);
                assertEquals(0xffffffff, pixels[(size - 1) * size + x]);
            }
        }
    }
}
