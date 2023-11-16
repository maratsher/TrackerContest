from __future__ import annotations

import contextlib
import enum
import os

import glfw

import imgui


class ImGuiFonts:
    class FontType(enum.Enum):
        REGULAR = enum.auto()
        BOLD = enum.auto()
        ITALIC = enum.auto()
        BOLDITALIC = enum.auto()

    __fonts = {}

    @staticmethod
    def __calculate_scaling_factor(glfw_window):
        window_width, window_height = glfw.get_window_size(glfw_window)
        framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(glfw_window)
        return max(float(framebuffer_width) / window_width, float(framebuffer_height) / window_height)

    @staticmethod
    def init_fonts(font_size, fonts_path, glfw_window=None):
        ImGuiFonts.__fonts = dict()

        io = imgui.get_io()

        io.fonts.clear()

        # scaling factor for high-density screens
        if glfw_window:
            scaling_factor = ImGuiFonts.__calculate_scaling_factor(glfw_window)
            io.font_global_scale = 1.0 / scaling_factor

        font_names = [name for name in os.listdir(fonts_path) if name.endswith('ttf')]

        for font_type in ImGuiFonts.FontType:
            for font_name in font_names:
                if font_type.name.lower() == font_name.split('.')[0].lower():
                    font = io.fonts.add_font_from_file_ttf(os.path.join(fonts_path, font_name),
                                                           font_size, None,
                                                           io.fonts.get_glyph_ranges_cyrillic())
                    ImGuiFonts.__fonts[font_type] = font

                    break

    @staticmethod
    def get_font(font_type: FontType = FontType.REGULAR):
        if font_type not in ImGuiFonts.__fonts:
            print("Font not initialized")
            return None

        return ImGuiFonts.__fonts[font_type]

    @staticmethod
    @contextlib.contextmanager
    def apply_font(font_type: FontType = FontType.REGULAR):
        font = ImGuiFonts.get_font(font_type)
        
        if font:
            imgui.push_font(font)
        
        yield 
        
        if font:
            imgui.pop_font()
