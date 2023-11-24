from typing import List, Tuple

import numpy as np
import cv2


class Drawer:
    @staticmethod
    def draw_bboxes(frame: np.ndarray, bbox_list: List[Tuple[np.ndarray]]) -> np.ndarray:
        for bbox, color in bbox_list:
            if bbox is None:
                continue
            frame = Drawer.draw_bbox(frame, color, bbox)

        return frame

    @staticmethod
    def draw_bbox(frame: np.ndarray, color: tuple, bbox: np.ndarray):
        color = Drawer.convert_color_imgui_to_opencv(color)
        cv2.rectangle(
            frame, (bbox[0], bbox[1]), (bbox[2] + bbox[0], bbox[3] + bbox[1]), color, 3)
        return frame

    @staticmethod
    def convert_color_imgui_to_opencv(color_imgui: tuple):
        color_opencv = tuple(int(c * 255) for c in color_imgui[:3])
        return color_opencv
