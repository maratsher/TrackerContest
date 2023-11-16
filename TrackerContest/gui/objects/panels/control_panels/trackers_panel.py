from typing import Dict, List, Tuple, AnyStr
import imgui
import numpy as np

from TrackerContest.gui.objects.panels import Panel

from TrackerContest.core import Bus


class TrackersPanel(Panel):
    def __init__(self, name: str = "Trackers"):
        super().__init__(name)

        self.trackers: Dict = {
            "Krolik": {"color": (1.0, 0.0, 0.0), "address": "127.0.0.1:56456", "selected": True},
            "Pyatochok": {"color": (0.0, 1.0, 0.0), "address": "127.0.0.1:56456", "selected": True},
            "Vinni": {"color": (0.0, 0.0, 1.0), "address": "127.0.0.1:56456", "selected": True},
        }
        self.selected_trackers: Dict = self.trackers.copy()

        Bus.subscribe("connected-new-tracker", self.connected_new_tracker)

    def _draw_content(self):
        imgui.set_window_font_scale(2)
        imgui.text("Подключенные трекеры:")
        imgui.set_window_font_scale(1.5)
        for tracker_name in self.trackers.keys():
            color: Tuple = self.trackers.get(tracker_name).get('color')
            address: AnyStr = self.trackers.get(tracker_name).get('address')
            imgui.text_colored(f"{tracker_name} ({address})", *color)
            imgui.same_line()
            changed, self.selected_trackers[tracker_name]["selected"] = imgui.checkbox(f"##{tracker_name}{address}",
                                                                                       self.selected_trackers[tracker_name]["selected"])

            if changed:
                Bus.publish("changed-draw-mode", {"name": tracker_name,
                                                  "draw": self.selected_trackers[tracker_name]["selected"]})
    def connected_new_tracker(self, name: str, color: np.ndarray, address: str):
        self.trackers[name] = {"color": color, "address": address, "selected": True}
