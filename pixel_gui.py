from tkinter import *
import tempfile
from sudokuclass import solver_engine
from testing_tools import test_matrices, pretty_print, verified_solution
from time import *

# stack overflow
ICON = (
    b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
    b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
    b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x01\x00\x00\x00\x01'
) + b'\x00' * 1282 + b'\xff' * 64

_, ICON_PATH = tempfile.mkstemp()
with open(ICON_PATH, 'wb') as icon_file:
    icon_file.write(ICON)


###############################################################################
# testing tools file
###############################################################################

# move to separate file
def pretty_print(matrix):
    SIZE = len(matrix[0])

    for row in range(SIZE):
        if row % 3 == 0:
            print('\n', "-------------------------------------", end=' ')  # todo hardcoded
        print()
        for column in range(SIZE):
            if column % 3 == 0:
                print("|", "", end=' ')
            if matrix[row][column] != 0:
                print(matrix[row][column], "", end=' ')
            else:
                print(" ", "", end=' ')
        print("|", "", end=' ')
    print('\n', "-------------------------------------", end=' ')  # todo hardcoded
    return ""


# move to separate file
def verified_solution():
    return


# move to separate file
class TestMatrices:
    @staticmethod
    def matrix_00():
        test_matrix = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0]]
        return test_matrix

    @staticmethod
    def matrix_01():
        test_matrix = [[5, 0, 2, 0, 9, 0, 7, 8, 6],
                       [9, 0, 3, 0, 6, 0, 5, 0, 0],
                       [6, 7, 1, 8, 0, 0, 3, 2, 9],
                       [0, 0, 0, 7, 5, 1, 9, 0, 0],
                       [8, 9, 0, 4, 0, 2, 0, 6, 7],
                       [0, 0, 4, 6, 8, 9, 0, 0, 0],
                       [4, 2, 7, 0, 0, 8, 6, 9, 3],
                       [0, 0, 9, 0, 7, 0, 8, 0, 2],
                       [3, 5, 8, 0, 2, 0, 4, 0, 1]]
        return test_matrix

    @staticmethod
    def matrix_02():
        test_matrix = [[5, 0, 2, 0, 9, 0, 7, 8, 6],
                       [9, 0, 3, 0, 6, 0, 5, 0, 0],
                       [6, 7, 1, 8, 0, 0, 3, 2, 9],
                       [0, 0, 0, 7, 5, 1, 9, 0, 0],
                       [8, 9, 0, 4, 0, 2, 0, 6, 7],
                       [0, 0, 4, 6, 8, 9, 0, 0, 0],
                       [4, 2, 7, 0, 0, 8, 6, 9, 3],
                       [0, 0, 9, 0, 7, 0, 8, 0, 2],
                       [3, 5, 8, 0, 2, 0, 4, 0, 1]]
        return test_matrix

    @staticmethod
    def matrix_03():
        test_matrix = [[0, 8, 0, 0, 0, 1, 0, 0, 5],
                       [0, 0, 7, 0, 0, 0, 0, 9, 0],
                       [6, 0, 0, 0, 0, 0, 3, 0, 0],
                       [0, 1, 0, 0, 0, 2, 0, 0, 8],
                       [0, 0, 0, 0, 7, 0, 0, 0, 0],
                       [0, 0, 3, 5, 0, 0, 6, 0, 0],
                       [0, 9, 0, 0, 6, 0, 0, 0, 1],
                       [5, 0, 0, 0, 0, 3, 0, 2, 0],
                       [0, 0, 4, 8, 0, 0, 7, 0, 0]]
        return test_matrix

    # Easy 11 [4][0-2] # + 1 - 3
    @staticmethod
    def matrix_010():
        test_matrix = [[0, 0, 0, 7, 0, 0, 0, 0, 0],
                       [1, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 4, 3, 0, 2, 0, 0],
                       [4, 2, 3, 0, 0, 0, 0, 0, 6],
                       [0, 0, 0, 5, 0, 9, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 4, 1, 8],
                       [0, 0, 0, 0, 8, 1, 0, 0, 0],
                       [0, 0, 2, 0, 0, 0, 0, 5, 0],
                       [0, 4, 0, 0, 0, 0, 3, 0, 0]]
        return test_matrix

    # 17 element with solution
    @staticmethod
    def matrix_011():
        test_matrix = [[0, 0, 0, 7, 0, 0, 0, 0, 0],
                       [1, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 4, 3, 0, 2, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 6],
                       [0, 0, 0, 5, 0, 9, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 4, 1, 8],
                       [0, 0, 0, 0, 8, 1, 0, 0, 0],
                       [0, 0, 2, 0, 0, 0, 0, 5, 0],
                       [0, 4, 0, 0, 0, 0, 3, 0, 0]]
        return test_matrix

    # 17 element without solution HARD TO SOLVE
    @staticmethod
    def matrix_012():
        test_matrix = [[0, 0, 0, 8, 0, 1, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 4, 3, 0],
                       [5, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 7, 0, 8, 0, 0],
                       [0, 0, 0, 0, 0, 0, 1, 0, 0],
                       [0, 2, 0, 0, 3, 0, 0, 0, 0],
                       [6, 0, 0, 0, 0, 0, 0, 7, 5],
                       [0, 0, 3, 4, 0, 0, 0, 0, 0],
                       [0, 0, 0, 2, 0, 0, 6, 0, 0]]
        return test_matrix

    # Easy 12 [5][2] [NO SOLUTION]
    @staticmethod
    def matrix_013():
        test_matrix = [[0, 0, 0, 8, 0, 1, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 4, 3, 0],
                       [5, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 7, 0, 8, 0, 0],
                       [0, 0, 0, 0, 0, 0, 1, 0, 0],
                       [0, 2, 0, 0, 3, 0, 0, 0, 0],
                       [6, 0, 0, 0, 0, 0, 0, 7, 5],
                       [0, 0, 3, 4, 0, 0, 0, 0, 0],
                       [0, 0, 0, 2, 0, 0, 6, 0, 0]]
        return test_matrix

    @staticmethod
    def matrix_014():
        test_matrix = [[0, 2, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 6, 0, 0, 0, 0, 3],
                       [0, 7, 4, 0, 8, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 3, 0, 0, 2],
                       [0, 8, 0, 0, 4, 0, 0, 1, 0],
                       [6, 0, 0, 5, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 1, 0, 7, 8, 0],
                       [5, 0, 0, 0, 0, 9, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 4, 0]]
        return test_matrix

    @staticmethod
    def matrix_015():
        test_matrix = [[1, 2, 3, 4, 5, 6, 7, 8, 0],
                       [0, 0, 0, 6, 0, 0, 0, 0, 3],
                       [0, 7, 4, 0, 8, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 3, 0, 0, 2],
                       [0, 8, 0, 0, 4, 0, 0, 1, 0],
                       [6, 0, 0, 5, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 1, 0, 7, 8, 0],
                       [5, 0, 0, 0, 0, 9, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 4, 0]]
        return test_matrix

    @staticmethod
    def matrix_016():
        test_matrix = [[0, 0, 0, 0, 0, 0, 0, 3, 1],
                       [6, 0, 0, 0, 2, 0, 0, 0, 0],
                       [0, 0, 0, 0, 7, 0, 0, 0, 0],
                       [0, 5, 0, 1, 0, 8, 0, 0, 0],
                       [2, 0, 0, 0, 0, 0, 6, 0, 0],
                       [0, 0, 0, 3, 0, 0, 0, 7, 0],
                       [0, 0, 0, 0, 4, 0, 2, 0, 0],
                       [0, 3, 0, 5, 0, 0, 0, 0, 0],
                       [7, 0, 0, 0, 0, 0, 0, 0, 0]]
        return test_matrix

    @staticmethod
    def matrix_016_s():
        test_matrix = [[9, 2, 4, 6, 8, 5, 7, 3, 1],
                       [6, 7, 1, 4, 2, 3, 8, 5, 9],
                       [3, 8, 5, 9, 7, 1, 4, 2, 6],
                       [4, 5, 7, 1, 6, 8, 3, 9, 2],
                       [2, 9, 3, 7, 5, 4, 6, 1, 8],
                       [1, 6, 8, 3, 9, 2, 5, 7, 4],
                       [5, 1, 9, 8, 4, 7, 2, 6, 3],
                       [8, 3, 2, 5, 1, 6, 9, 4, 7],
                       [7, 4, 6, 2, 3, 9, 1, 8, 5]]
        return test_matrix


###############################################################################
# END testing tools file
###############################################################################


class CanvasGUI:

    def __init__(self, root):
        self.master = root
        root.title("")
        root.iconbitmap(default=ICON_PATH)
        root.resizable(width=False, height=False)
        root.config(background="white")

        self.dynamic_size = BOARD_SIZE * cell_size

        self.agenda = []
        self.current_board = []
        self.previous_board = []
        self.time_1 = 0
        self.time_2 = 0
        self.board_font = "fixedsys"
        self.font_size = int(12 / 25.000 * cell_size)
        self.abort = FALSE  # todo better way of doing this?

        self.sudoku_solver = solver_engine()

        self.default_matrix = [[0 for _ in range(9)] for __ in range(9)]
        self.text_id_matrix = [[0 for _ in range(9)] for __ in range(9)]  # self.default_matrix
        self.shaded_id_matrix = [[0 for _ in range(9)] for __ in range(9)]  # self.default_matrix
        self.text_id_small_matrix_00 = [[0 for _ in range(9)] for __ in range(9)]  # self.default_matrix

        self.offset = 40  # todo

        # todo package this into a separate def?
        self.board_container = Canvas(
            root)  # height=50.000/9/25*self.dynamic_size, width=225.000/9/25*self.dynamic_size
        # self.board_container.config(bg='white', borderwidth=0, highlightthickness=0)
        self.board_container.pack()  # side=TOP, fill=BOTH

        # hardcoded some style stuff (offset/5+2)
        self.canvas_board = Canvas(root)
        self.canvas_board.config(height=225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2,
                                 width=225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2)
        self.canvas_board.config(bg='white', borderwidth=0, highlightthickness=0)
        self.board_canvas_width = (self.canvas_board.winfo_reqwidth()) / 9.000 / 25 * self.dynamic_size
        self.board_canvas_height = (self.canvas_board.winfo_reqheight()) / 9.000 / 25 * self.dynamic_size
        self.canvas_board.pack()
        # self.canvas_board.bind('<Button-1>', self.mini_matrix_board_selector)

        self.control_panel = Canvas(root)
        # self.control_panel.config(height=50.000/9/25*self.dynamic_size, width=225.000/9/25*self.dynamic_size)
        self.control_panel.config(bg='white', borderwidth=0, highlightthickness=0)
        self.canvas_board.config(borderwidth=0, highlightthickness=0)
        self.control_panel.pack(side=BOTTOM, fill=BOTH)

        self.create_title()
        self.initialize_board()
        self.controls()

    def controls(self):  # TODO standardize the format eg  self.matrix_select["menu"].config(bg='white') vs config
        font_size = self.font_size

        def style_config(method):  # todo this a method? correct name?
            method.config(font=(self.board_font, int(font_size * 1.2)), bg='white', borderwidth=0, highlightthickness=0)

        # todo move/combine spacers
        # highlight-thickness is used to center the spacers  # todo hacky
        for i in range(10):
            spacer = Canvas(self.control_panel, width=50, height=10, bg='white', highlightthickness=2,
                            highlightbackground='white')
            spacer.grid(row=0, column=i)
            spacer = Canvas(self.control_panel, width=50, height=10, bg='white', highlightthickness=0)
            spacer.grid(row=2, column=i)

        # to do combine all of this solve?
        self.solve_button = Canvas(self.control_panel)
        self.solve_button.grid(row=1, column=1, columnspan=3)

        self.solve_button_label = Label(self.solve_button, text="SOLVE")
        style_config(self.solve_button_label)
        self.solve_button_label.pack()
        self.solve_button_label.bind('<Button-1>', self.click_solve)

        self.solve_button_label_disabled = Label(self.solve_button_label, text="SOLVE", fg='grey')
        style_config(self.solve_button_label_disabled)
        self.solve_button_label_disabled.pack()

        self.options_button = Canvas(self.control_panel, width=150, height=50)
        self.options_button.grid(row=1, column=6, columnspan=3)

        self.options_button_label = Label(self.options_button, text="SELECT")
        style_config(self.options_button_label)
        self.options_button_label.pack()
        self.options_button_label.bind('<Button-1>', self.click_select)

        self.options_button_abort = Label(self.options_button_label, text="ABORT?", fg='black')  # todo color
        style_config(self.options_button_abort)
        self.options_button_abort.bind('<Button-1>', self.stop_solver)

        # TODO move this out somewhere or def it all
        # todo too much copy/paste
        self.select_menu_container = Canvas(self.canvas_board, width=400, height=100)
        # def options_menu_options(self, text):  # todo rename?
        # TODO manually centered text (why + 2)
        # todo combine things n' stuff
        om_master = self.select_menu_container  # self.control_panel # self.canvas_board

        # OLD todo: not sure what line below does
        # self.options_menu_00 = Canvas(self.canvas_board, width=150, height=150, bg='orange', highlightthickness=0)
        self.options_menu_00 = Canvas(om_master, width=110, height=56, bg='grey90')
        self.options_menu_00.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_00.bind('<Button-1>', self.board_selector)
        self.options_menu_00.create_text(55 + 2, 25 + 3, text="Empty", font=(self.board_font, int(font_size)))

        # OLD todo: not sure what line below does
        # self.options_menu_01 = Canvas(self.canvas_board, width=149, height=150, bg='yellow', highlightthickness=0)
        self.options_menu_01 = Canvas(om_master, width=110, height=56, bg='grey90')
        self.options_menu_01.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_01.bind('<Button-1>', self.board_selector)
        self.options_menu_01.create_text(55 + 2, 25 + 3, text="Easy", font=(self.board_font, int(font_size)))

        # OLD todo: not sure what line below does
        # self.options_menu_02 = Canvas(self.canvas_board, width=150, height=150, bg='red', highlightthickness=0)
        self.options_menu_02 = Canvas(om_master, width=110, height=56, bg='grey90')
        self.options_menu_02.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_02.bind('<Button-1>', self.board_selector)
        self.options_menu_02.create_text(55 + 2, 25 + 3, text="Hard", font=(self.board_font, int(font_size)))

    def click_solve(self, second):  # TODO second argument not necessary (use lambda or other solution)
        self.forget_options_menu()
        self.solve_button_label_disabled.pack()
        self.options_button_abort.pack()
        self.solve_execute()
        # if i include abort.pack_forget here, it executes before solver_execute finishes

    def click_select(self, second):  # TODO rename TODO fix second hack
        # TODO clear board
        # TODO this may also be done elsewhere, and can be removed
        self.current_board = self.default_matrix  # todo necessary?
        self.update_board()

        # self.options_menu_00.config(highlightthickness=4, highlightcolor='blue')
        ''' #y_rel = .88
        self.options_menu_00.place(relx=.15, rely=y_rel, anchor=CENTER)
        self.options_menu_01.place(relx=.5, rely=y_rel, x=-1, anchor=CENTER)
        self.options_menu_02.place(relx=.85, rely=y_rel, anchor=CENTER)
        '''
        self.select_menu_container.place(relx=.5, rely=.5, anchor=CENTER)

        # todo STYLE keep both border edges or over lap them?
        self.options_menu_00.place(relx=.218, rely=.5, anchor=CENTER)
        self.options_menu_01.place(relx=.5, rely=.5, anchor=CENTER)
        self.options_menu_02.place(relx=(1 - .218), rely=.5, anchor=CENTER)

        self.solve_button_label_disabled.pack()  # re-enable solver button

        # todo the test_matrices should be in a list, and that list can be used in mini_matrix_board_selector
        '''
        self.make_mini_boards(test_matrices(01), 0, 0)
        self.make_mini_boards(test_matrices(02), 1, 0)
        self.make_mini_boards(test_matrices(03), 2, 0)
        #self.make_mini_boards(test_matrices(11), 0, 1)
        '''

        self.cell_shader()

    def create_title(self):
        font_size = self.font_size
        self.title_label = Label(self.board_container, text="SUDOKU SOLVER", font=(self.board_font, font_size * 2),
                                 bg="#fff")
        self.title_label.pack()

    def create_options_menu(self):
        # place options menu stuff here
        return  # remove this

    def initialize_board(self):
        font_size = self.font_size
        # todo can these lines be assigned names? to then do something with later?
        # create lines (the +4 is the grid offset from the cells - style); hardcoded 461
        for x_shift in range(BOARD_SIZE - 1):
            if (x_shift + 1) % 3 != 0:
                self.canvas_board.create_line((x_shift + 1) * cell_size + self.offset / 8, 0 + self.offset / 8,
                                              (x_shift + 1) * cell_size + self.offset / 8,
                                              self.board_canvas_height - 465)
            else:
                self.canvas_board.create_line((x_shift + 1) * cell_size + self.offset / 10, 0,
                                              (x_shift + 1) * cell_size + self.offset / 10, self.board_canvas_height,
                                              width=3)
        for y_shift in range(BOARD_SIZE - 1):
            if (y_shift + 1) % 3 != 0:
                self.canvas_board.create_line(0 + self.offset / 8, (y_shift + 1) * cell_size + self.offset / 8,
                                              self.board_canvas_height - 465,
                                              (y_shift + 1) * cell_size + self.offset / 8)
            else:
                self.canvas_board.create_line(0, (y_shift + 1) * cell_size + self.offset / 8, self.board_canvas_height,
                                              (y_shift + 1) * cell_size + self.offset / 8, width=3)

        # initialize text_id_matrix matrix
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                x_position = cell_size / 2 + (x * cell_size) + 4  # readability
                y_position = cell_size / 2 + (y * cell_size) + 4
                cell = ""
                self.text_id_matrix[y][x] = self.canvas_board.create_text(x_position, y_position,
                                                                          font=(self.board_font, font_size), text=cell)
                # TODO check this [x][y]

    # todo: consider refactor
    def cell_shader(self):  # OLD TODO move into another function somewhere?
        self.id_matrix_cleanup(self.shaded_id_matrix)  # delete shaded cells
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.canvas_board.itemcget(self.text_id_matrix[i][j], 'text') != "":  # OLD todo check the text value
                    self.shaded_id_matrix[i][j] = self.canvas_board.create_rectangle(j * 50 + self.offset / 8,
                                                                                     i * 50 + self.offset / 8,
                                                                                     (j + 1) * 50 + self.offset / 8,
                                                                                     (i + 1) * 50 + self.offset / 8,
                                                                                     width=0, fill="gray77")
                    self.canvas_board.lower(self.shaded_id_matrix[i][j])
                    # OLD TODO correct i j ?

    def board_selector(self, event):
        if event.widget == self.options_menu_00:
            board = TestMatrices().matrix_00()
        elif event.widget == self.options_menu_01:
            board = TestMatrices().matrix_01()
            print(board)
        elif event.widget == self.options_menu_02:
            board = TestMatrices().matrix_11()  # hard

        self.current_board = board  # OLD todo
        self.update_board()
        self.cell_shader()
        self.solve_button_label_disabled.pack_forget()
        self.forget_options_menu()

    def update_board(self):
        # update entire board
        # todo range(len(self.current_board))
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell_zero_check = self.current_board[i][j]  # OLD TODO rename cell_zero_check
                if cell_zero_check == 0:
                    cell_zero_check = ""
                self.canvas_board.itemconfig(self.text_id_matrix[i][j], text=cell_zero_check)

        self.previous_board = self.current_board


    def solver_engine(self):
        # # todo: refactor
        #
        # # seed agenda
        # # todo copying old code: why am I checking for an empty board
        # # if not self.agenda:
        # #     self.agenda.append(self.current_board)
        #
        # if self.agenda == []:
        #     self.agenda = [self.current_board]  # populate agenda with the selected board  # todo redundant??
        #
        # while self.agenda:
        #     self.current_board = self.agenda.pop(0)
        #     # find empty
        #     empty_element = self.sudoku_solver.find_empty_cell_greedy(self.current_board)  # todo
        #     empty_element = []
        #     # abort todo: review lines
        #     # todo refactor
        #     if self.abort or not empty_element:
        #         self.update_board()  # don't need to pass the current board  # todo
        #         self.agenda = list()  # todo review
        #         self.options_button_abort.pack_forget()  # todo
        #         self.abort = False
        #         break
        #
        # # todo: what does this do?
        # three_rule_permitted_values = \
        #     self.sudoku_solver.find_node_element_values(empty_element, self.current_board)
        # self.agenda = \
        #     self.sudoku_solver.extend_nodes_and_insert(self.agenda, self.current_board, three_rule_permitted_values)
        #
        # self.update_board()
        #
        # # todo: what does this do? UI stuff?
        # if self.agenda != []:
        #     self.master.after(1, self.solver_engine)


        if self.agenda == []:
            self.agenda = [self.current_board]  # populate agenda with the selected board  # todo redundant??
        self.current_board = self.agenda.pop(0)  # TODO? this is unnecessary; hackery  ?
        #empty_element = self.sudoku_solver.find_empty_cell(self.current_board)
        empty_element = self.sudoku_solver.find_empty_cell_greedy(self.current_board)
        if empty_element == None or self.abort == TRUE:  # solved condition
            self.update_board()  # don't need to pass the current board

            self.agenda = []  # todo necessarY?

            # abort
            self.options_button_abort.pack_forget()
            self.abort = FALSE

            if benchmarking: self.time_2 = time(); print (self.time_2 - self.time_1)
            return

        three_rule_permitted_values = self.sudoku_solver.find_node_element_values(empty_element, self.current_board)
        self.agenda = self.sudoku_solver.extend_nodes_and_insert(self.agenda, self.current_board, three_rule_permitted_values)

        self.update_board()

        if self.agenda != []:
            self.master.after(1, self.solver_engine)


    def solve_execute(self):
        self.solver_engine()

    def stop_solver(self, second):  # TODO fix second hack
        self.abort = True

    # todo move?
    def forget_options_menu(
            self):  # TODO REMOVE THIS? just use self.select_menu_container.place_forget() where ever it was called
        # todo can use state=normal/disabled/hidden
        self.select_menu_container.place_forget()
        '''
        self.options_menu_00.place_forget()
        self.options_menu_01.place_forget()
        self.options_menu_02.place_forget()
        '''
        # self.options_menu_00.grid_forget()
        # self.options_menu_01.grid_forget()
        # self.options_menu_02.grid_forget()

    def id_matrix_cleanup(self, matrix):
        for each_row in matrix:
            for each_cell in each_row:
                if each_cell != 0:
                    self.canvas_board.delete(each_cell)

    def make_mini_boards2(self, matrix, large_square_x, large_square_y):  # TODO change name [make] and move
        # todo fix large square x/y usage
        font_size = self.font_size / 3
        option_board = matrix  # TODO NAME option_board
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                x_position = ((cell_size / 2 + (x * cell_size) + 4) * 1 / 3)  # readability
                y_position = ((cell_size / 2 + (y * cell_size) + 4) * 1 / 3)
                # x_position += 37  # todo fix hardcode
                # y_position += 78
                #   x_position += 4  # todo fix hardcode
                #   y_position += 4
                # x_position *= large_square_x  # todo fix hardcode
                # y_position *= large_square_y
                #   x_position += large_square_x*150
                #   x_position += large_square_y*150
                cell_zero_check = option_board[y][x]  # TODO NAME cell_zero_check
                if cell_zero_check == 0:
                    cell_zero_check = " "
                self.text_id_small_matrix_00[y][x] = self.options_menu_02.create_text(x_position, y_position,
                                                                                      font=(self.board_font, font_size),
                                                                                      text=cell_zero_check)
                # self.text_id_small_matrix_00[y][x] = Label(font=(self.board_font, font_size), text=cell_zero_check)
                # self.text_id_small_matrix_00[y][x].config(bg='white')
                # self.text_id_small_matrix_00[y][x].place(x=x_position, y=y_position, height=14, width=12)

                # self.text_id_small_matrix_00[y][x].bind('<Button-1>', self.debug_printer)

    def make_mini_boards(self, matrix, large_square_x, large_square_y):  # TODO change name [make] and move
        # todo fix large square x/y usage
        font_size = self.font_size / 3
        option_board = matrix  # TODO NAME option_board
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                x_position = ((cell_size / 2 + (x * cell_size) + 4) * 1 / 3)  # readability
                y_position = ((cell_size / 2 + (y * cell_size) + 4) * 1 / 3)
                # x_position += 37  # todo fix hardcode
                # y_position += 78
                x_position += 4  # todo fix hardcode
                y_position += 4
                # x_position *= large_square_x  # todo fix hardcode
                # y_position *= large_square_y
                x_position += large_square_x * 150
                x_position += large_square_y * 150
                cell_zero_check = option_board[y][x]  # TODO NAME cell_zero_check
                if cell_zero_check == 0:
                    cell_zero_check = " "
                self.text_id_small_matrix_00[y][x] = self.canvas_board.create_text(x_position, y_position,
                                                                                   font=(self.board_font, font_size),
                                                                                   text=cell_zero_check)
                # self.text_id_small_matrix_00[y][x] = Label(font=(self.board_font, font_size), text=cell_zero_check)
                # self.text_id_small_matrix_00[y][x].config(bg='white')
                # self.text_id_small_matrix_00[y][x].place(x=x_position, y=y_position, height=14, width=12)

                # self.text_id_small_matrix_00[y][x].bind('<Button-1>', self.debug_printer)

    def forget_mini_matrices_menu(
            self):  # TODO what if I put these all on a canvas then forgot that canvas (would have to redraw lines tho)
        for x in range(9):
            for y in range(9):
                # print self.text_id_small_matrix_00
                changename = self.text_id_small_matrix_00[y][x]
                self.canvas_board.destroy(changename)

    # todo grab the matrices from a list (click_select as well)
    def mini_matrix_board_selector(self, event):  # todo rename
        if event.x < 153 and event.y < 178:
            board = test_matrices(1)
        else:
            print("foo")
            return
        self.current_board = board
        self.update_board()
        self.solve_button_label_disabled.pack_forget()

        self.forget_options_menu()
        # forget the mini matrices
        self.forget_mini_matrices_menu()


'''
    # TODO option menu not used
    def option_select_display(self):  # TODO this does not seem necessary
        #self.solve_button["text"] = "SOLVE"
        #self.solve_button["state"] = "normal"

        self.board_selector()
        self.update_board()

        self.id_matrix_cleanup(self.shaded_id_matrix)  # delete shaded cells
        self.cell_shader()
'''

'''
        #self.options_menu_options = {"All Zeros": test_matrices(00), "Matrix 01": test_matrices(01), "Matrix 02": test_matrices(02)}
        #self.options_menu_options = ("All Zeros", "Matrix 01", "Matrix 02")

'''

BOARD_SIZE = 9
cell_size = 50  # minimum = 25; TODO why can't it go below?

benchmarking = False

root = Tk()
sudoku_gui = CanvasGUI(root)
root.mainloop()
