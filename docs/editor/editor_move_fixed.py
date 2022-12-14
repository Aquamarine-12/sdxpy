import curses
import sys

class Window:
    def __init__(self, nrow, ncol):
        assert 0 <= nrow and 0 <= ncol
        self.nrow = nrow
        self.ncol = ncol

# [cursor]
class Cursor:
    def __init__(self, row, col):
        assert 0 <= row and 0 <= col
        self.row = row
        self.col = col
# [/cursor]

    def __str__(self):
        return f"({self.row}, {self.col})"

class Editor:
    def __init__(self):
        self.scr = None
        self.win = None
        self.cur = None
        self.running = True
        self.actions = {
            "Q": self.quit,
            "q": self.quit,
            "KEY_UP": self.up,
            "KEY_DOWN": self.down,
            "KEY_LEFT": self.left,
            "KEY_RIGHT": self.right
        }

    def __call__(self, scr, contents):
        self.setup(scr, contents)
        self.interact()

    def setup(self, scr, contents):
        self.scr = scr
        self.contents = contents
        self.win = Window(curses.LINES - 1, curses.COLS - 1)
        self.cur = Cursor(0, 0)

    def interact(self):
        while self.running:
            self.display()
            key = self.scr.getkey()
            if key in self.actions:
                self.actions[key]()

    def display(self):
        self.scr.erase()
        for i, line in enumerate(self.contents[:self.win.nrow]):
            self.scr.addstr(i, 0, line[:self.win.ncol])
        self.scr.move(self.cur.row, self.cur.col)

    def quit(self):
        self.running = False

    def left(self):
        if self.cur.col > 0:
            self.cur.col -= 1

    def right(self):
        line_len = len(self.contents[self.cur.row])
        if self.cur.col < min(self.win.ncol - 1, line_len - 1):
            self.cur.col += 1

    # [move]
    def up(self):
        if self.cur.row > 0:
            self.cur.row -= 1
        self.limit_col()

    def down(self):
        if self.cur.row < min(self.win.nrow - 1, len(self.contents) - 1):
            self.cur.row += 1
        self.limit_col()

    def limit_col(self):
        self.cur.col = min(self.cur.col, len(self.contents[self.cur.row]) - 1)
    # [/move]

def make_contents():
    line = '0123456789'
    result = []
    for i in range(len(line)):
        result.append(line[:i+1])
    return result

if __name__ == "__main__":
    editor = Editor()
    contents = make_contents()
    try:
        curses.wrapper(editor, contents)
    except Exception as exc:
        print(exc)
