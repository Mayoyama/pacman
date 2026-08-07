from typing import Any


class SpriteRenderer:
    SPRITE_OFFSET_X = 8
    SPRITE_OFFSET_Y = 7

    def set_sprite(self, sprite_data: Any, sprite_size_line: int,
                   sprite_width: int, sprite_height: int) -> None:
        """Store sprite image data for later rendering."""
        self._sprite_data = sprite_data
        self._sprite_size_line = sprite_size_line
        self._sprite_width = sprite_width
        self._sprite_height = sprite_height

    def draw_sprite(self, sprite_pos: tuple[int, int]) -> None:
        """Draws the sprite image onto the maze at the given cell.

        Converts 'sprite_pos' to its pixel location via '_cell_to_pixel',
        then copies the sprite's pixels onto the image buffer starting at
        that position, using each pixel's alpha channel to blend it with
        the maze underneath so transparent areas of the sprite don't
        overwrite the maze.
        """
        if not self._sprite_data or not sprite_pos:
            return

        r, c = sprite_pos

        sprite_x, sprite_y = self._cell_to_pixel(r, c)
        sprite_x -= self.SPRITE_OFFSET_X
        sprite_y -= self.SPRITE_OFFSET_Y

        for y in range(self._sprite_height):
            for x in range(self._sprite_width):
                src_offset = (y * self._sprite_size_line) + (x * 4)

                blue = self._sprite_data[src_offset + 0]
                green = self._sprite_data[src_offset + 1]
                red = self._sprite_data[src_offset + 2]
                alpha = self._sprite_data[src_offset + 3]

                if alpha == 0:
                    continue

                dest_x = sprite_x + x
                dest_y = sprite_y + y

                if (
                 0 <= dest_x < self._image_width
                 and 0 <= dest_y < self._image_height):
                    offset = (dest_y * self._size_line) + (dest_x * 4)

                    self._data[offset + 0] = blue
                    self._data[offset + 1] = green
                    self._data[offset + 2] = red
                    self._data[offset + 3] = 255
