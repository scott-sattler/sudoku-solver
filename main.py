

class Sudoku:
    def __init__(self):
        # primary data structure
        self.board_gui_data = [[CellData() for _ in range(9)] for __ in range(9)]



if __name__ == '__main__':
    BOARD_SIZE = 9
    CELL_SIZE = 50  # cell size: minimum > 25... probably

    benchmarking = False

    root = Tk()
    app = SudokuApp(root, CELL_SIZE)
    root.mainloop()