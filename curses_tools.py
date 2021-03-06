SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
ALT_LEFT_KEY_CODE = ord('a')
RIGHT_KEY_CODE = 261
ALT_RIGHT_KEY_CODE = ord('d')
UP_KEY_CODE = 259
ALT_UP_KEY_CODE = ord('w')
DOWN_KEY_CODE = 258
ALT_DOWN_KEY_CODE = ord('s')


def read_controls(canvas):
    """Read keys pressed and returns tuple with controls state."""
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code in (UP_KEY_CODE, ALT_UP_KEY_CODE):
            rows_direction = -1

        if pressed_key_code in (DOWN_KEY_CODE, ALT_DOWN_KEY_CODE):
            rows_direction = 1

        if pressed_key_code in (RIGHT_KEY_CODE, ALT_RIGHT_KEY_CODE):
            columns_direction = 1

        if pressed_key_code in (LEFT_KEY_CODE, ALT_LEFT_KEY_CODE):
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def get_centered_frame_coordinates(canvas, frame):
    """Return upper left corner y, x coordinates of the frame to draw it centered."""
    frame_height, frame_width = get_frame_size(frame)
    max_y, max_x = canvas.getmaxyx()
    start_row = round(max_y / 2 - frame_height / 2)
    start_column = round(max_x / 2 - frame_width / 2)
    return start_row, start_column
