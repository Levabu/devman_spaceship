import asyncio
from typing import NamedTuple

from curses_tools import draw_frame, get_centered_frame_coordinates
from game_scenario import PHRASES
from obstacles import Obstacle

coroutines = []
obstacles: list[Obstacle] = []
obstacles_in_last_collisions: list[Obstacle] = []

YEAR_DURATION = 15
year = 1957


class Gun(NamedTuple):
    rows_speed: int
    columns_speed: int


async def sleep(duration: int):
    for _ in range(duration):
        await asyncio.sleep(0)


async def show_game_over(canvas, game_over_frame):
    coordinates = get_centered_frame_coordinates(canvas, game_over_frame)
    while True:
        draw_frame(canvas, *coordinates, game_over_frame)
        await asyncio.sleep(0)


async def count_time():
    global year
    while True:
        await sleep(YEAR_DURATION)
        year += 1


async def draw_info_panel(canvas):
    while True:
        info = f'Year {year}'
        try:
            message = PHRASES[year]
        except KeyError:
            message = ''
        info = info if not message else f'{info} — {message}'
        draw_frame(canvas, 1, 1, info)
        await asyncio.sleep(0)
        draw_frame(canvas, 1, 1, info, negative=True)


def choose_guns():
    fire_size = 2 if year < 2020 else 3
    if year < 2020:
        guns = [Gun(rows_speed=-2, columns_speed=0)]
    else:
        guns = [
            Gun(-2, 0),
            Gun(-2, -1), Gun(-2, 1),
            Gun(-2, -2), Gun(-2, 2),
            Gun(-1, -2), Gun(-1, 2),
            Gun(-1, -1), Gun(-1, 1),
            Gun(0, -2), Gun(0, 2)
        ]
    return fire_size, guns
