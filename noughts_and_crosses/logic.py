import curses
from curses import textpad
import random
import pickle
from datetime import datetime
from typing import NamedTuple
from enum import Enum

circle_symbol = '◯'
cross_symbol = 'X'
noughts_side = ['noughts', 'n', 'o']
crosses_side = ['crosses', 'c', 'x']

MAX_MESSAGE_LENGTH = 27
HORIZONTAL_PADDING = 2
VERTICAL_PADDING = 4
INFO_LINES_COUNT = 6


class Winner(Enum):
    NOBODY = 0
    PLAYER = 1
    AI = 2
    SAVING = 3


def get_all_fields(h, w):
    all_fields = set()
    for y in range(VERTICAL_PADDING, h+2):
        for x in range(HORIZONTAL_PADDING, w):
            all_fields.add((y, x))
    return all_fields


def draw_filled(stdscr, cursor, circles, crosses, o_symbol, x_symbol, side_symbol):
    for circle in circles:
        stdscr.addstr(circle[0], circle[1], o_symbol)

    for cross in crosses:
        stdscr.addstr(cross[0], cross[1], x_symbol)

    stdscr.addstr(cursor[0], cursor[1], side_symbol, curses.A_STANDOUT)


def draw_new_symbol(stdscr, cursor, new_coords, sym, side_symbol):
    stdscr.addstr(new_coords[0], new_coords[1], sym)
    stdscr.addstr(cursor[0], cursor[1], side_symbol, curses.A_STANDOUT)


def gameover(stdscr, winner):
    for x in [0, 1, 2]:
        stdscr.addstr(x, 0, " "*MAX_MESSAGE_LENGTH)
    if winner == Winner.NOBODY:
        stdscr.addstr(1, 0, "Stalemate!")
    elif winner == Winner.PLAYER:
        stdscr.addstr(1, 0, "You won!")
    elif winner == Winner.AI:
        stdscr.addstr(1, 0, "You lost. We'll get them next time.")
    elif winner == Winner.SAVING:
        stdscr.addstr(1, 0, "Game state is saved, closing...")
    stdscr.getch()


def choose_side():
    return random.choice(noughts_side + crosses_side)


def is_winning_move(pos, taken, sequence):
    line = 0
    for direction in [(0, 1), (1, 1), (1, 0), (1, -1)]:
        for depth in range(-sequence+1, sequence):
            if (pos[0]+direction[0]*depth, pos[1]+direction[1]*depth) in taken:
                line += 1
            else:
                line = 0
            if line == sequence:
                return True
    return False


def process_move(stdscr, turn_coords, cursor_coords, coords, free_fields, turn_symbol, win_seq, cursor_symbol):
    coords.add(turn_coords)
    free_fields.remove(turn_coords)
    draw_new_symbol(stdscr, cursor_coords, turn_coords, turn_symbol, cursor_symbol)
    if is_winning_move(turn_coords, coords, win_seq):
        winner = Winner.PLAYER if turn_coords == cursor_coords else Winner.AI
        gameover(stdscr, winner)
        return "over"
    return True if turn_coords == cursor_coords else False


def game_init(stdscr, height, width, player_side, saved_game_path):
    class Box(NamedTuple):
        x1: int = VERTICAL_PADDING - 1
        x2: int = height + VERTICAL_PADDING
        y1: int = HORIZONTAL_PADDING - 1
        y2: int = width + HORIZONTAL_PADDING

    curses.curs_set(0)
    curses.halfdelay(20)
    circles = set()
    crosses = set()
    player_symbol = circle_symbol if player_side in noughts_side else cross_symbol
    ai_symbol = cross_symbol if player_symbol is circle_symbol else circle_symbol
    turn_was_made = True if player_side in noughts_side else False
    free_fields = get_all_fields(height+2, width+2)
    info_y_pos = iter(range(INFO_LINES_COUNT))
    seq = min(height, width)
    cursor = (VERTICAL_PADDING+1, HORIZONTAL_PADDING+1)
    if saved_game_path is not None:
        with open(saved_game_path, "rb+") as f:
            (height, width, side, circles, crosses) = pickle.load(f)

    if player_side in noughts_side:
        player = circles
        ai = crosses
    else:
        ai = circles
        player = crosses

    stdscr.addstr(next(info_y_pos), 0, "Game of noughts and crosses", curses.A_BOLD)
    stdscr.addstr(next(info_y_pos), 0, "You are playing {}".format("Noughts" if player_side in noughts_side else "Crosses"))
    box = Box()
    textpad.rectangle(stdscr, box.x1, box.y1, box.x2, box.y2)
    stdscr.addstr(2 + 1 + height + 1 + next(info_y_pos), 0, "Press [f] make a turn")  # 2 for info lines before the game board
    stdscr.addstr(2 + 1 + height + 1 + next(info_y_pos), 0, "Use arrows to move")   # 1 for margin before and after the board
    stdscr.addstr(2 + 1 + height + 1 + next(info_y_pos), 0, "Press [q] to quit")   # height - height of the board
    stdscr.addstr(2 + 1 + height + 1 + next(info_y_pos), 0, "Press [s] to save and quit")  # info_y_pos - iterator for lines pos
    return circles, crosses, player_symbol, ai_symbol, turn_was_made, free_fields, seq, cursor, player, ai


def game(stdscr, height, width, side, saved_game_path):
    [circles, crosses,
     player_symbol, ai_symbol,
     turn_was_made, free_fields,
     win_seq, cursor,
     player, ai] = game_init(stdscr, height, width, side, saved_game_path)

    draw_filled(stdscr, cursor, circles, crosses, circle_symbol, cross_symbol, player_symbol)

    while True:
        if side in noughts_side and turn_was_made:
            turn = random.choice(tuple(free_fields))
            turn_was_made = process_move(stdscr, turn, cursor, ai, free_fields, ai_symbol, win_seq, player_symbol)
            if turn_was_made is "over":
                break
        if len(free_fields) == 0:
            gameover(stdscr, winner=Winner.NOBODY)
            break
        draw_filled(stdscr, cursor, circles, crosses, circle_symbol, cross_symbol, player_symbol)
        key = stdscr.getch()
        if key == curses.KEY_UP and cursor[0] > VERTICAL_PADDING:
            new_cursor = (cursor[0]-1, cursor[1])
        elif key == curses.KEY_RIGHT and cursor[1] < width+1:    # 1 - margin around the board
            new_cursor = (cursor[0], cursor[1]+1)
        elif key == curses.KEY_DOWN and cursor[0] < height+2+1:  # 2 - info lines before the board
            new_cursor = (cursor[0]+1, cursor[1])                # 1 - margin around the board
        elif key == curses.KEY_LEFT and cursor[1] > HORIZONTAL_PADDING:
            new_cursor = (cursor[0], cursor[1]-1)
        elif key == ord('q'):
            break

        elif key == ord('s'):
            save = (height, width, side, circles, crosses)
            with open('save-%s.pickle' % datetime.today().strftime('%b-%d-%H-%M-%S'), "wb+") as f:
                pickle.dump(save, f)
            gameover(stdscr, winner=Winner.SAVING)
            break

        elif key == ord('f'):
            if cursor in free_fields:
                turn_was_made = process_move(stdscr, cursor, cursor, player, free_fields, player_symbol, win_seq, player_symbol)
                if turn_was_made is "over":
                    break

                if len(free_fields) == 0:
                    gameover(stdscr, winner=Winner.NOBODY)
                    break

            if side in crosses_side and turn_was_made:
                turn = random.choice(tuple(free_fields))
                turn_was_made = process_move(stdscr, turn, cursor, ai, free_fields, ai_symbol, win_seq, player_symbol)
                if turn_was_made is "over":
                    break

            if len(free_fields) == 0:
                gameover(stdscr, winner=Winner.NOBODY)
                break

            new_cursor = cursor
        else:
            new_cursor = cursor
        stdscr.addstr(cursor[0], cursor[1], ' ')
        cursor = new_cursor
