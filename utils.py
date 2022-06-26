import asyncio
from pathlib import Path

from curses_tools import draw_frame, get_centered_frame_coordinates
from obstacles import Obstacle

TIC_TIMEOUT = 0.1

coroutines = []
obstacles: list[Obstacle] = []
obstacles_in_last_collisions: list[Obstacle] = []

spaceship_frame_1 = Path('animations', 'spaceship_frame_1.txt').read_text()
spaceship_frame_2 = Path('animations', 'spaceship_frame_2.txt').read_text()
SPACESHIP_ANIMATION = (spaceship_frame_1, spaceship_frame_1, spaceship_frame_2, spaceship_frame_2)

GAME_OVER_PATH = Path('animations', 'game_over.txt')

year = 1957


async def sleep(duration: int):
    for i in range(duration):
        await asyncio.sleep(0)


async def show_game_over(canvas):
    frame = GAME_OVER_PATH.read_text()
    coordinates = get_centered_frame_coordinates(canvas, frame)
    while True:
        draw_frame(canvas, *coordinates, frame)
        await asyncio.sleep(0)


async def count_time():
    global year
    while True:
        await asyncio.sleep(1.5)
        year += 1


async def draw_info_panel(canvas):
    while True:
        canvas.addstr(1, 1, f'{year}')
        await asyncio.sleep(0)