from __future__ import annotations

import signal

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

from TrackerContest.gui.imgui_fonts import ImGuiFonts


class ImGuiApp:
    def __init__(self, window_width, window_height, fullscreen):
        self._window_width = window_width
        self._window_height = window_height

        self._fullscreen = fullscreen

        self.__window = None
        self.__renderer = None

        self.__init_app()

    @staticmethod
    def init_glfw_window(name, width, height, fullscreen):
        if not glfw.init():
            print("[ERROR] Could not initialize OpenGL context")
            exit(1)

        # OS X supports only forward-compatible core profiles from 3.2
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        # Select window mode
        primary_monitor = None
        if fullscreen:
            primary_monitor = glfw.get_primary_monitor()
            width, height = glfw.get_video_mode(primary_monitor).size

        # Create a windows and its OpenGL context
        window = glfw.create_window(width, height, name, primary_monitor, None)
        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            print("[ERROR] Could not initialize Window")
            exit(1)

        return window

    @staticmethod
    def set_custom_style():
        colors = imgui.get_style().colors
        colors[imgui.COLOR_WINDOW_BACKGROUND] = imgui.Vec4(0.00, 0.00, 0.00, 0.78)
        colors[imgui.COLOR_FRAME_BACKGROUND] = imgui.Vec4(0.29, 0.29, 0.29, 0.54)
        colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = imgui.Vec4(0.59, 0.59, 0.59, 0.40)
        colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = imgui.Vec4(0.59, 0.59, 0.59, 0.67)
        colors[imgui.COLOR_BUTTON] = imgui.Vec4(0.59, 0.59, 0.59, 0.89)
        colors[imgui.COLOR_BUTTON_HOVERED] = imgui.Vec4(0.55, 0.55, 0.55, 0.98)
        colors[imgui.COLOR_BUTTON_ACTIVE] = imgui.Vec4(0.53, 0.53, 0.53, 0.98)
        colors[imgui.COLOR_HEADER] = imgui.Vec4(0.59, 0.59, 0.59, 0.39)
        colors[imgui.COLOR_HEADER_HOVERED] = imgui.Vec4(0.35, 0.35, 0.35, 0.78)
        colors[imgui.COLOR_HEADER_ACTIVE] = imgui.Vec4(0.23, 0.23, 0.23, 0.78)
        colors[imgui.COLOR_TEXT_SELECTED_BACKGROUND] = imgui.Vec4(0.53, 0.53, 0.53, 0.25)

    def __init_app(self):
        # Init interrupt handler
        InterruptHandler.signal()

        # Create imgui context
        imgui.create_context()

        # Create glfw windows and renderer
        self.__window = self.init_glfw_window("App", self._window_width, self._window_height, self._fullscreen)
        self.__renderer = GlfwRenderer(self.__window)

        #glfw.set_key_callback(self.__window, self.key_callback)

        # Init theme
        imgui.style_colors_dark()
        self.set_custom_style()

        # Init fonts
        ImGuiFonts.init_fonts(font_size=16, fonts_path="TrackerContest/resources/fonts/PT_Sans/",
                              glfw_window=self.__window)
        self.__renderer.refresh_font_texture()

        return self

    def __shutdown(self):
        self._terminate()

        self.__renderer.shutdown()
        glfw.terminate()

    def _terminate(self):
        pass

    def _update(self):
        pass

    def draw_content(self):
        pass

    def key_callback(self, window, key, scancode, action, mods):
        pass

    def keyboard_input(self):
        if imgui.is_key_pressed(glfw.KEY_F11):
            if not self._fullscreen:
                primary_monitor = glfw.get_primary_monitor()
                mode = glfw.get_video_mode(primary_monitor)
                glfw.set_window_monitor(self.__window, primary_monitor, 0, 0, mode.size[0], mode.size[1], 0)
            else:
                glfw.set_window_monitor(self.__window, None, 0, 0, self._window_width, self._window_height, 0)
            self._fullscreen = not self._fullscreen

    def run(self):
        if not self.__renderer:
            print("[ERROR] glfw windows is not initialized. Call ImGuiApp.init()")
            exit(1)

        while not glfw.window_should_close(self.__window) and not InterruptHandler.interrupted:
            glfw.poll_events()
            self.__renderer.process_inputs()

            imgui.new_frame()

            self._update()

            self.draw_content()

            self.keyboard_input()

            gl.glClearColor(0.0, 0.0, 0.0, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            imgui.render()
            self.__renderer.render(imgui.get_draw_data())
            glfw.swap_buffers(self.__window)

        self.__shutdown()


class InterruptHandler:
    interrupted = False

    @staticmethod
    def signal():
        signal.signal(signal.SIGINT, InterruptHandler.exit)
        signal.signal(signal.SIGTERM, InterruptHandler.exit)

    @staticmethod
    def exit(*args):
        InterruptHandler.interrupted = True


if __name__ == "__main__":
    app = ImGuiApp(720, 480, fullscreen=False)
    app.run()
