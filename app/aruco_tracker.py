from math import atan2, degrees
from typing import Dict, List, Tuple

import cv2
import numpy as np


def create_aruco_detector(dictionary_name: str = "DICT_4X4_50", refine_corners: bool = False):
    dictionary_id = getattr(cv2.aruco, dictionary_name, cv2.aruco.DICT_4X4_50)
    dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
    parameters = cv2.aruco.DetectorParameters()
    parameters.adaptiveThreshWinSizeMin = 3
    parameters.adaptiveThreshWinSizeMax = 33
    parameters.adaptiveThreshWinSizeStep = 10
    parameters.adaptiveThreshConstant = 7
    parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX if refine_corners else cv2.aruco.CORNER_REFINE_NONE
    parameters.cornerRefinementWinSize = 5
    parameters.cornerRefinementMaxIterations = 30
    parameters.cornerRefinementMinAccuracy = 0.05
    parameters.minMarkerPerimeterRate = 0.02
    parameters.maxMarkerPerimeterRate = 4.0
    return cv2.aruco.ArucoDetector(dictionary, parameters)


def preprocess_for_detection(frame, blur_level: int, denoise_level: int, equalize_hist: bool = False):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if equalize_hist:
        gray = cv2.equalizeHist(gray)

    if denoise_level > 0:
        h = float(denoise_level)
        gray = cv2.fastNlMeansDenoising(gray, None, h=h, templateWindowSize=7, searchWindowSize=21)

    if blur_level > 0:
        kernel = blur_level * 2 + 1
        gray = cv2.GaussianBlur(gray, (kernel, kernel), 0)

    return gray


def detect_markers(detector, gray):
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is None:
        return []

    result = []
    for i, marker_id in enumerate(ids.flatten().tolist()):
        pts = corners[i][0].astype(np.float32)
        cx = float(np.mean(pts[:, 0]))
        cy = float(np.mean(pts[:, 1]))
        size = float(
            np.mean(
                [
                    np.linalg.norm(pts[1] - pts[0]),
                    np.linalg.norm(pts[2] - pts[1]),
                    np.linalg.norm(pts[3] - pts[2]),
                    np.linalg.norm(pts[0] - pts[3]),
                ]
            )
        )

        edge = pts[1] - pts[0]
        angle = degrees(atan2(float(edge[1]), float(edge[0])))
        if angle < 0:
            angle += 360.0

        result.append(
            {
                "id": int(marker_id),
                "corners": pts,
                "center": (cx, cy),
                "size": size,
                "angle": angle,
            }
        )
    return result


def mirror_markers(markers: List[Dict], frame_width: int) -> List[Dict]:
    mirrored = []
    for marker in markers:
        pts = marker["corners"].copy()
        pts[:, 0] = (frame_width - 1) - pts[:, 0]
        cx, cy = marker["center"]
        mirrored.append(
            {
                "id": marker["id"],
                "corners": pts,
                "center": ((frame_width - 1) - cx, cy),
                "size": marker["size"],
                "angle": marker["angle"],
                "phantom": bool(marker.get("phantom", False)),
                "health": float(marker.get("health", 1.0)),
            }
        )
    return mirrored


def draw_markers(frame, markers: List[Dict]) -> None:
    for marker in markers:
        pts = marker["corners"].astype(int)
        marker_id = marker["id"]
        cx, cy = marker["center"]
        size = marker["size"]
        angle = marker["angle"]
        phantom = bool(marker.get("phantom", False))
        health = max(0.0, min(1.0, float(marker.get("health", 1.0))))
        live_color = (255, 255, 0)
        phantom_color = (0, 140, 255)
        base_color = phantom_color if phantom else live_color
        color_scale = 0.2 + 0.8 * health
        border_color = tuple(int(channel * color_scale) for channel in base_color)
        center_color = tuple(int(channel * color_scale) for channel in ((0, 90, 255) if phantom else (0, 255, 255)))
        label = f"ID {marker_id}  S {size:.1f}px  A {angle:.1f}deg"
        if phantom:
            label = f"PHANTOM H {health:.2f}  {label}"
        else:
            label = f"H {health:.2f}  {label}"

        thickness = 1 if phantom else 2
        cv2.polylines(frame, [pts], True, border_color, thickness)
        cv2.circle(frame, (int(cx), int(cy)), 4, center_color, -1)
        cv2.putText(
            frame,
            label,
            (int(cx) + 8, int(cy) - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            border_color,
            2,
            cv2.LINE_AA,
        )


def normalize_xy(center: Tuple[float, float], frame_shape, zero_center):
    h, w = frame_shape[:2]
    cx, cy = center

    if zero_center is None:
        zero_x, zero_y = w * 0.5, h * 0.5
    else:
        zero_x, zero_y = zero_center

    x_rel = ((cx - zero_x) / max(1.0, w * 0.5)) * 0.5 + 0.5
    y_rel = ((cy - zero_y) / max(1.0, h * 0.5)) * 0.5 + 0.5
    return x_rel, y_rel


def normalize_angle(angle: float, zero_angle: float) -> float:
    offset = (angle - zero_angle) % 360.0
    return offset / 360.0
