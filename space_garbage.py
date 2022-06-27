import asyncio
from curses_tools import draw_frame
import os
from pathlib import Path
from random import randint, choice

from curses_tools import get_frame_size
from game_scenario import get_garbage_delay_tics
from obstacles import Obstacle
from utils import coroutines, obstacles, obstacles_in_last_collisions, sleep, YEAR_DURATION

GARBAGE_FRAMES = [Path('animations', 'garbage', file).read_text() for file in os.listdir(Path('animations', 'garbage'))]


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Column position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    obstacle = Obstacle(row, column, *get_frame_size(garbage_frame))
    obstacles.append(obstacle)

    while row < rows_number:
        obstacle.row = row
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            break
    obstacles.remove(obstacle)
    del obstacle


async def fill_orbit_with_garbage(canvas, max_x):
    while True:
        from utils import year
        delay = get_garbage_delay_tics(year)
        try:
            await sleep(delay)
        except TypeError:
            await sleep(YEAR_DURATION)
            continue
        coroutines.append(fly_garbage(
            canvas,
            randint(1, max_x - 1),
            garbage_frame=choice(GARBAGE_FRAMES),
            speed=1
        ))