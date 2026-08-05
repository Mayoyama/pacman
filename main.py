from mazegenerator import MazeGenerator
from rendering import UI_state, RenderSettings, FrameBuffer


def main() -> None:
    mazegen = MazeGenerator((16, 16), False, (7, 7), (-1, -1), 0)
    ui_state = UI_state()
    rend_settings = RenderSettings()
    maze = mazegen.maze
    start = mazegen.maze_entry
    maze_h = len(maze)
    maze_w = len(maze[0])
    frame_buffer = FrameBuffer((maze_w, maze_h), rend_settings)


if __name__ == "__main__":
    main()
