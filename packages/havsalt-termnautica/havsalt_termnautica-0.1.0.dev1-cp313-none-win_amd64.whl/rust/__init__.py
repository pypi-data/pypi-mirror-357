from colex import RESET as _RESET
from charz import Screen as _Screen, Camera as _Camera, Texture as _Texture

from .render import render_all as _render_all


__all__ = ["RustScreen"]


CONSOLE_CLEAR_CODE = "\x1b[2J\x1b[H"
CURSOR_HIDE_CODE = "\x1b[?25l"
CURSOR_SHOW_CODE = "\x1b[?25h"


class RustScreen(_Screen):
    def refresh(self) -> None:
        self._resize_if_necessary()
        self.clear()
        centering_x = 0
        centering_y = 0
        if _Camera.current.mode & _Camera.MODE_CENTERED:
            (centering_x, centering_y) = self.get_actual_size().to_tuple()
        # TODO: MODE_INCLUDE_SIZE
        out = _render_all(
            self,
            tuple(_Texture.texture_instances.values()),
            _Camera.current,
            centering_x // 2,
            centering_y // 2,
        )
        self.show(out)

    def show(self, out: str) -> None:
        actual_size = self.get_actual_size()
        # construct frame
        if self.is_using_ansi():
            out += _RESET
            cursor_move_code = f"\x1b[{actual_size.y - 1}A" + "\r"
            out += cursor_move_code
        # write and flush
        self.stream.write(out)
        self.stream.flush()

    def on_cleanup(self) -> None:
        if self.hide_cursor and self.is_using_ansi():
            self.stream.write(CURSOR_SHOW_CODE)
            self.stream.flush()
        if self.final_clear:
            old_fill = self.transparency_fill
            self.transparency_fill = " "
            self.clear()
            out = _render_all(
                self,
                [],
                _Camera.current,
                0,
                0,
            )
            self.show(out)
            self.transparency_fill = old_fill
