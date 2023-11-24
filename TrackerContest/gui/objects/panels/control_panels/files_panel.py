from pathlib import Path

import imgui

from TrackerContest.core import Bus
from TrackerContest.gui.objects.panels import Panel


class FilesControl(Panel):
    def __init__(self, name: str = "Files"):
        super().__init__(name)

        self._input_path = ""
        self._save_path = ""

        self._input_status = ""
        self._save_status = ""

    def _draw_content(self):
        imgui.dummy(0, 10)

        imgui.set_window_font_scale(1.5)
        imgui.indent(10)
        window_width, window_height = imgui.get_window_size()

        imgui.columns(2, 'files', border=False)

        imgui.set_column_width(0, window_width / 4)
        imgui.set_column_width(1, window_width * 3 / 4)
        imgui.align_text_to_frame_padding()
        imgui.set_window_font_scale(1.4)

        imgui.text("Input video")
        imgui.next_column()
        imgui.push_style_var(imgui.STYLE_FRAME_BORDERSIZE, 1.0)
        changed_ip, self._input_path = imgui.input_text('##input_path:', self._input_path)
        imgui.pop_style_var()

        imgui.next_column()

        imgui.text("Output save")
        imgui.next_column()
        imgui.push_style_var(imgui.STYLE_FRAME_BORDERSIZE, 1.0)
        changed_sp, self._save_path = imgui.input_text('##output_path:', self._save_path)
        imgui.pop_style_var()

        imgui.columns(1)
        imgui.unindent(10)

        if changed_ip:
            input_path = Path(self._input_path)
            if input_path.exists() and input_path.suffix == ".mp4":
                Bus.publish("init-video", self._input_path)
                self._input_status = f"Video path: {self._input_path}"
            else:
                self._input_status = "Video does not exist"
        if changed_sp:
            saved_path = Path(self._save_path)
            if saved_path.is_dir():
                self._save_path = "Dir exist"
            else:
                self._save_path = "Saved dir does not exist"

        imgui.dummy(0, 5)
        imgui.set_window_font_scale(1.7)
        imgui.text(self._input_status)
        imgui.text(self._save_status)
