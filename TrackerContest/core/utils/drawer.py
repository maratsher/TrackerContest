from typing import List, Tuple

import numpy as np
import cv2


class Drawer:
    @staticmethod
    def draw_bboxes(frame: np.ndarray, bbox_list: List[Tuple[np.ndarray]]) -> np.ndarray:
        for color, bbox in bbox_list:
            frame = Drawer.draw_bbox(frame, color, bbox)

        return frame

    @staticmethod
    def draw_bbox(frame: np.ndarray, color: np.ndarray, bbox: np.ndarray):
        frame = cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        return frame
