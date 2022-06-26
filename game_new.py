import asyncio
import curses
import itertools
from functools import partial
import math
from pathlib import Path
import random
import os
import time

from curses_tools import draw_frame, read_controls, get_frame_size
from explosion import explode
from obstacles import show_obstacles, has_collision
from physics import update_speed
from space_garbage import fly_garbage, fill_orbit_with_garbage
from utils import (sleep, obstacles, coroutines, obstacles_in_last_collisions,
                   SPACESHIP_ANIMATION, show_game_over, draw_info_panel, count_time)

SKY_FRAMES = [
    (20, curses.A_DIM),
    (3, curses.A_NORMAL),
    (5, curses.A_BOLD),
    (3, curses.A_NORMAL),
]

TIC_TIMEOUT = 0.1
GARBAGE_ANIMATIONS_PATH = os.path.join('animations', 'garbage')
SPACESHIP_HEIGHT, SPACESHIP_WIDTH = get_frame_size(SPACESHIP_ANIMATION[0])
INFO_PANEL_HEIGHT, INFO_PANEL_WIDTH = 2, 55


async def blink(canvas, row, column, symbol='*'):
    """Display animation of blinking stars."""
    while True:
        canvas.addstr(row, column, symbol)
        delay = random.randint(1, 30)
        await sleep(delay)
        for duration, style in SKY_FRAMES:
            canvas.addstr(row, column, symbol, style)
            await sleep(duration)


async def fire(canvas, start_row, start_column, rows_speed=-2, columns_speed=0):
    """Display animation of a gun shot. Direction and speed can be specified."""
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                await explode(canvas, row, column)
                return

        row += rows_speed
        column += columns_speed


async def automate_fire(canvas, row, column, frame, fire_size=2):
    for i in range(fire_size):
        fire_start_y = row
        fire_start_x = column + math.floor(SPACESHIP_WIDTH / 2)
        coroutines.append(fire(canvas, fire_start_y, fire_start_x))
        await asyncio.sleep(0)


def keep_frame_inside_border(frame, row, column, canvas):
    """Return coordinates unchanged if frame inside the border. Otherwise, return the nearest possible coordinates."""
    max_y, max_x = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(frame)
    row = min(row + frame_height, max_y - 1) - frame_height
    column = min(column + frame_width, max_x - 1) - frame_width
    row = max(row, 1)
    column = max(column, 1)
    return row, column


async def animate_spaceship(canvas, spaceship_animation, row, column, rows_speed=0, columns_speed=0):
    """Display spaceship animation."""
    for frame in itertools.cycle(spaceship_animation):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        rows_speed, columns_speed = update_speed(rows_speed, columns_speed, rows_direction, columns_direction)
        row += rows_speed
        column += columns_speed
        row, column = keep_frame_inside_border(frame, row, column, canvas)
        draw_frame(canvas, row, column, frame)
        if space_pressed:
            coroutines.append(automate_fire(canvas, row, column, frame))
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)
        for obstacle in obstacles:
            if obstacle.has_collision(row, column, SPACESHIP_HEIGHT, SPACESHIP_WIDTH):
                await explode(canvas, row, column)
                coroutines.append(show_game_over(canvas))
                return


def draw(canvas, spaceship_animation):
    curses.curs_set(False)
    canvas.nodelay(True)
    max_y, max_x = canvas.getmaxyx()
    symbols = '+*.:'
    stars_number = round(max_y * max_x / 50)
    spaceship_start_position = (max_y / 2, max_x / 2)

    info_panel = canvas.derwin(INFO_PANEL_HEIGHT, INFO_PANEL_WIDTH, max_y - 4, 2)

    for i in range(stars_number):
        coroutines.append(blink(
            canvas,
            row=random.randint(1, max_y - 2),
            column=random.randint(1, max_x - 2),
            symbol=random.choice(symbols)
        ))
    coroutines.append(animate_spaceship(canvas, spaceship_animation,
                                        *spaceship_start_position, rows_speed=0, columns_speed=0))
    for i in range(12):
        coroutines.append(fill_orbit_with_garbage(canvas, max_x))
    coroutines.append(show_obstacles(canvas, obstacles))
    coroutines.append(draw_info_panel(info_panel))
    loop = asyncio.get_event_loop()
    coroutines.append(count_time())

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        curses.update_lines_cols()


def main():
    curses.update_lines_cols()
    curses.wrapper(partial(draw, spaceship_animation=SPACESHIP_ANIMATION))


if __name__ == '__main__':
    main()
