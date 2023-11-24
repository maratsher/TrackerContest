import imgui


from TrackerContest.gui.objects.panels import Panel

from TrackerContest.core import Bus


class TrackersPanel(Panel):
    def __init__(self, name: str = "Trackers"):
        super().__init__(name)

    def _draw_content(self):
        pass

