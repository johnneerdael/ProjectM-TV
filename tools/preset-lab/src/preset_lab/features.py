import cv2
import numpy as np


def measure_frame(frame: np.ndarray, previous: np.ndarray | None, fps: float) -> dict:
    if frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8 or fps <= 0:
        raise ValueError("frame must be RGB uint8 with a positive frame rate")
    if previous is not None and (previous.shape != frame.shape or previous.dtype != np.uint8):
        raise ValueError("previous frame must have matching RGB dimensions")
    rgb = frame.astype(np.float32) / 255
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    result = {"brightness": float(luma.mean()), "contrast": float(luma.std()),
              "saturation": float(hsv[..., 1].mean() / 255),
              "edge_energy": float(cv2.Laplacian(luma, cv2.CV_32F).var()),
              "coverage": float(np.mean(rgb.max(axis=2) > 0.04)),
              "clipping_ratio": float(np.mean(np.all(rgb >= 0.99, axis=2))),
              "frame_change": 0.0, "luma_change": 0.0, "color_change": 0.0,
              "motion_speed": 0.0, "motion_density": 0.0, "rotation": 0.0,
              "expansion": 0.0, "translation_x": 0.0, "translation_y": 0.0,
              "motion_residual": 0.0, "motion_fit_available": False, "flow_support": 0.0}
    if previous is None:
        return result
    previous_rgb = previous.astype(np.float32) / 255
    previous_luma = previous_rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    result["frame_change"] = float(np.abs(rgb - previous_rgb).mean())
    result["luma_change"] = abs(float(luma.mean() - previous_luma.mean()))
    result["color_change"] = float(np.linalg.norm(rgb.mean(axis=(0, 1)) - previous_rgb.mean(axis=(0, 1))) / np.sqrt(3))
    gx = cv2.Sobel(previous_luma, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(previous_luma, cv2.CV_32F, 0, 1)
    valid = np.hypot(gx, gy) > 0.02
    valid[:3] = valid[-3:] = False
    valid[:, :3] = valid[:, -3:] = False
    result["flow_support"] = float(valid.mean())
    if valid.sum() < 12:
        return result
    old_gray = np.clip(previous_luma * 255, 0, 255).astype(np.uint8)
    gray = np.clip(luma * 255, 0, 255).astype(np.uint8)
    flow = cv2.calcOpticalFlowFarneback(old_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    height, width = luma.shape
    velocity = flow * np.array([fps / width, fps / height], np.float32)
    speeds = np.linalg.norm(velocity, axis=2)
    result["motion_speed"] = float(speeds[valid].mean())
    result["motion_density"] = float(np.mean(speeds > 0.01))
    step = max(1, min(width, height) // 24)
    ys, xs = np.mgrid[3:height - 3:step, 3:width - 3:step]
    selected = valid[ys, xs]
    x, y = xs[selected] / width - 0.5, ys[selected] / height - 0.5
    design = np.column_stack((x, y, np.ones(len(x))))
    measured = velocity[ys[selected], xs[selected]]
    if len(x) < 8:
        return result
    weights = np.ones(len(x))
    coefficients = np.zeros((3, 2))
    for _ in range(3):
        root = np.sqrt(weights)[:, None]
        coefficients = np.linalg.lstsq(design * root, measured * root, rcond=None)[0]
        residual = np.linalg.norm(measured - design @ coefficients, axis=1)
        scale = max(float(np.median(residual)) * 2, 1e-4)
        weights = np.minimum(1, scale / np.maximum(residual, 1e-8))
    result.update(motion_fit_available=True,
                  translation_x=float(coefficients[2, 0]), translation_y=float(coefficients[2, 1]),
                  expansion=float((coefficients[0, 0] + coefficients[1, 1]) / 2),
                  rotation=float((coefficients[0, 1] - coefficients[1, 0]) / 2),
                  motion_residual=float(np.mean(residual)))
    return result
