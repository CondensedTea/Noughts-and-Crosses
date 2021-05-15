from curses import wrapper
from logic import game, choose_side
import click


@click.command()
@click.option('--height', '-h', default=3, help='Number of rows on gameboard')
@click.option('--width', '-w', default=3, help='Number of columns on gameboard')
@click.option('--side', '-s', default=choose_side(), help='Player\'s side: can be n[oughts] or c[rosses]')
@click.option('--load', '-l', default=None, help='Path to save file of the game')
def start(height, width, side, load):
    wrapper(game, height, width, side, load)

if __name__ == '__main__':
    start()
