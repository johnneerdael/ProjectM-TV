package com.example.projectm.visualizer;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.EncodeHintType;
import com.google.zxing.WriterException;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;
import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel;
import java.io.IOException;
import java.util.EnumMap;

/** Black/white QR pixels with an unbroken four-module quiet zone. */
final class UploadQrCode {
    static int[] pixels(String address, int size) throws IOException {
        EnumMap<EncodeHintType, Object> hints = new EnumMap<>(EncodeHintType.class);
        hints.put(EncodeHintType.MARGIN, 4);
        hints.put(EncodeHintType.ERROR_CORRECTION, ErrorCorrectionLevel.M);
        try {
            BitMatrix matrix = new QRCodeWriter().encode(address, BarcodeFormat.QR_CODE, size, size, hints);
            int[] pixels = new int[size * size];
            for (int y = 0; y < size; y++) for (int x = 0; x < size; x++)
                pixels[y * size + x] = matrix.get(x, y) ? 0xff000000 : 0xffffffff;
            return pixels;
        } catch (WriterException failure) {
            throw new IOException("Cannot display the upload QR code", failure);
        }
    }
    private UploadQrCode() {}
}
