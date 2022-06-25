import asyncio
import curses
import itertools
from functools import partial
import math
import random
import os
import time

from curses_tools import draw_frame, read_controls, get_frame_size
from space_garbage import fly_garbage

SKY_FRAMES = [
    (20, curses.A_DIM),
    (3, curses.A_NORMAL),
    (5, curses.A_BOLD),
    (3, curses.A_NORMAL),
]

TIC_TIMEOUT = 0.1
GARBAGE_ANIMATIONS_PATH = os.path.join('animations', 'garbage')


async def blink(canvas, row, column, symbol='*'):
    """Display animation of blinking stars."""
    while True:
        canvas.addstr(row, column, symbol)
        delay = random.randint(1, 30)
        for i in range(delay):
            await asyncio.sleep(0)
        for duration, style in SKY_FRAMES:
            canvas.addstr(row, column, symbol, style)
            for i in range(duration):
                await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
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
        row += rows_speed
        column += columns_speed


def keep_frame_inside_border(frame, row, column, canvas):
    """Return coordinates unchanged if frame inside the border. Otherwise, return the nearest possible coordinates."""
    max_y, max_x = canvas.getmaxyx()
    frame_height, frame_width = get_frame_size(frame)
    row = min(row + frame_height, max_y - 1) - frame_height
    column = min(column + frame_width, max_x - 1) - frame_width
    row = max(row, 1)
    column = max(column, 1)
    return row, column


async def animate_spaceship(canvas, spaceship_animation, row, column, rows_speed=1, columns_speed=1):
    """Display spaceship animation."""
    for frame in itertools.cycle(spaceship_animation):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row += rows_direction * rows_speed
        column += columns_direction * columns_speed
        row, column = keep_frame_inside_border(frame, row, column, canvas)
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


def draw(canvas, spaceship_animation):
    curses.curs_set(False)
    canvas.nodelay(True)
    max_y, max_x = curses.window.getmaxyx(canvas)
    symbols = '+*.:'
    stars_number = round(max_y * max_x / 50)
    spaceship_start_position = (max_y / 2, max_x / 2)
    spaceship_start_frame = spaceship_animation[0]
    spaceship_frame_width = get_frame_size(spaceship_start_frame)[1]
    fire_start_x = spaceship_start_position[0] - 1
    fire_start_y = spaceship_start_position[1] + math.floor(spaceship_frame_width / 2)
    fire_start_position = (fire_start_x, fire_start_y)

    # global coroutines
    for i in range(stars_number):
        coroutine = blink(
            canvas,
            row=random.randint(1, max_y - 2),
            column=random.randint(1, max_x - 2),
            symbol=random.choice(symbols)
        )
        coroutines.append(coroutine)
    coroutines.append(fire(canvas, *fire_start_position, rows_speed=-0.8))
    coroutines.append(animate_spaceship(canvas, spaceship_animation,
                                        *spaceship_start_position, rows_speed=5, columns_speed=5))
    coroutines.append(fly_garbage(
            canvas,
            random.randint(1, max_x - 1),
            '123\n789',
            speed=0.5
        )
    )

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
    with open('animations/spaceship_frame_1.txt') as file:
        spaceship_frame_1 = file.read()
    with open('animations/spaceship_frame_2.txt') as file:
        spaceship_frame_2 = file.read()
    spaceship_animation = (spaceship_frame_1, spaceship_frame_1, spaceship_frame_2, spaceship_frame_2)
    curses.update_lines_cols()
    curses.wrapper(partial(draw, spaceship_animation=spaceship_animation))


if __name__ == '__main__':
    coroutines = []
    main()
