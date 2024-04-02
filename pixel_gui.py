from tkinter import *
import tempfile
from old.OLD_testing_tools import test_matrices

# from time import *

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
def verified_solution():
    return

###############################################################################
# END testing tools file
###############################################################################


class CellData:
    def __init__(self, number=None, text=None, canvas=None):
        self.number = number  # actual value to display (as text)
        self.text = text  # text id todo: change to text_id?
        self.canvas = canvas  # canvas id?

    def __repr__(self):
        return str(self.number), str(self.text), str(self.canvas)


class CanvasGUI:
    def __init__(self, root, cell_size=50, debug=False):
        if debug: return  # noqa

        # todo: some sort of container, eg dictionary
        self.title_label = None
        self.solve_button = None
        self.solve_button_label = None
        self.solve_button_label_disabled = None
        self.options_button = None
        self.options_button_label = None
        self.options_button_abort = None

        self.select_menu_container = None
        self.options_menu_00 = None
        self.options_menu_01 = None
        self.options_menu_02 = None

        self.master = root  # todo: rename
        root.title("")
        root.iconbitmap(default=ICON_PATH)
        root.resizable(width=False, height=False)
        root.config(background="white")

        self.cell_size = cell_size
        self.offset = 40  # todo
        self.dynamic_size = BOARD_SIZE * cell_size

        self.board_font = "fixedsys"
        self.font_size = int(12 / 25.000 * cell_size)
        self.abort = FALSE  # todo better way of doing this?

        # primary data structure
        self.board_gui_data = [[CellData() for _ in range(9)] for __ in range(9)]

        # todo: remove
        width = len(self.board_gui_data[0])
        height = len(self.board_gui_data)

        # OLD todo package this into a separate def?
        self.board_container = Canvas(
            root)  # height=50.000/9/25*self.dynamic_size, width=225.000/9/25*self.dynamic_size
        # self.board_container.config(bg='white', borderwidth=0, highlightthickness=0)
        self.board_container.pack()  # side=TOP, fill=BOTH

        # OLD todo: hardcoded some style stuff (offset/5+2)
        self.canvas_board = Canvas(root)
        self.canvas_board.config(
            height=225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2,
            width=225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2
        )
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

        # todo: move to main
        self.create_title()
        self.initialize_board()
        self.controls()

    def create_title(self):
        font_size = self.font_size
        self.title_label = Label(
            self.board_container,
            text="SUDOKU SOLVER",
            font=(self.board_font, font_size * 2),
            bg="#fff"
        )
        self.title_label.pack()

    def initialize_board(self):
        """
        - create board lines
        - initialize (populate) board_gui_data matrix
            create canvas and text box for each cell
        """
        font_size = self.font_size
        cell_size = self.cell_size
        offset = self.offset
        board_canvas_height = self.board_canvas_height
        board_size = len(self.board_gui_data)

        # create lines (the +4 is the grid offset from the cells - style)
        for x_shift in range(board_size - 1):
            if (x_shift + 1) % 3 != 0:
                x_0 = (x_shift + 1) * cell_size + offset / 8
                x_1 = (x_shift + 1) * cell_size + offset / 8
                y_0 = 0 + offset / 8
                y_1 = board_canvas_height - 465  # todo: hardcoded 461 ... lol 465 tho
                width = 1
            else:
                x_0 = (x_shift + 1) * cell_size + offset / 10
                x_1 = (x_shift + 1) * cell_size + offset / 10
                y_0 = 0
                y_1 = board_canvas_height
                width = 3
            self.canvas_board.create_line(x_0, y_0, x_1, y_1, width=width)

        for y_shift in range(board_size - 1):
            if (y_shift + 1) % 3 != 0:
                x_0 = 0 + self.offset / 8
                x_1 = self.board_canvas_height - 465
                y_0 = (y_shift + 1) * cell_size + self.offset / 8
                y_1 = (y_shift + 1) * cell_size + self.offset / 8
                width = 1
            else:
                x_0 = 0
                x_1 = self.board_canvas_height
                y_0 = (y_shift + 1) * cell_size + self.offset / 8
                y_1 = (y_shift + 1) * cell_size + self.offset / 8
                width = 3
            self.canvas_board.create_line(x_0, y_0, x_1, y_1, width=width)

        # initialize board_gui_data matrix
        # creates canvas and text box for each cell
        for i in range(len(self.board_gui_data)):
            for j in range(len(self.board_gui_data[0])):  # assumes rectangular
                canvas_id = self.canvas_board.create_rectangle(
                    j * 50 + self.offset / 8,
                    i * 50 + self.offset / 8,
                    (j + 1) * 50 + self.offset / 8,
                    (i + 1) * 50 + self.offset / 8,
                    width=0, fill="#ffffff"
                )

                txt_id = self.canvas_board.create_text(
                    cell_size / 2 + (j * cell_size) + 4,
                    cell_size / 2 + (i * cell_size) + 4,
                    font=(self.board_font, font_size),
                    text=''  # str(i) + str(j)
                )

                self.canvas_board.lower(canvas_id)

                self.board_gui_data[i][j].canvas = canvas_id
                self.board_gui_data[i][j].text = txt_id


    def controls(self):
        # OLD TODO standardize the format
        # OLD TODO eg self.matrix_select["menu"].config(bg='white') vs config

        font_size = self.font_size

        def style_config(instance):
            instance.config(
                font=(self.board_font, int(font_size * 1.2)),
                bg='white',
                borderwidth=0,
                highlightthickness=0
            )

        # OLD todo move/combine spacers
        # highlight-thickness is used to center the spacers  # OLD todo hacky
        for i in range(10):
            spacer = Canvas(
                self.control_panel,
                width=50, height=10,
                bg='white',
                highlightthickness=2,
                highlightbackground='white'
            )
            spacer.grid(row=0, column=i)
            spacer = Canvas(
                self.control_panel,
                width=50, height=10,
                bg='white',
                highlightthickness=0
            )
            spacer.grid(row=2, column=i)

        # solve button
        self.solve_button = Canvas(self.control_panel)
        self.solve_button.grid(row=1, column=1, columnspan=3)

        self.solve_button_label = Label(self.solve_button, text="SOLVE")
        style_config(self.solve_button_label)
        self.solve_button_label.pack()
        self.solve_button_label.bind('<Button-1>', lambda event: self.click_solve())

        self.solve_button_label_disabled = Label(self.solve_button_label, text="SOLVE", fg='grey')
        style_config(self.solve_button_label_disabled)
        self.solve_button_label_disabled.pack()

        # options ("select" menu) button canvas
        self.options_button = Canvas(self.control_panel, width=150, height=50)
        self.options_button.grid(row=1, column=6, columnspan=3)

        self.options_button_label = Label(self.options_button, text="SELECT")
        style_config(self.options_button_label)
        self.options_button_label.pack()
        self.options_button_label.bind('<Button-1>', lambda event: self.display_difficulty_menu())

        self.options_button_abort = Label(self.options_button_label, text="ABORT?", fg='black')  # todo color
        style_config(self.options_button_abort)
        self.options_button_abort.bind('<Button-1>', lambda event: self.stop_solver())

        # difficulty selector
        self.select_menu_container = Canvas(self.canvas_board, width=400, height=100)
        # def options_menu_options(self, text):  # todo rename?
        # TODO manually centered text (why + 2)
        om_master = self.select_menu_container  # self.control_panel # self.canvas_board

        # self.options_menu_00 = Canvas(self.canvas_board, width=150, height=150, bg='orange', highlightthickness=0)
        self.options_menu_00 = Canvas(om_master, width=110, height=56, bg='grey90')
        self.options_menu_00.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_00.bind('<Button-1>', self.board_selector)
        self.options_menu_00.create_text(55 + 2, 25 + 3, text="Empty", font=(self.board_font, int(font_size)))

        # self.options_menu_01 = Canvas(self.canvas_board, width=149, height=150, bg='yellow', highlightthickness=0)
        self.options_menu_01 = Canvas(om_master, width=110, height=56, bg='grey90')
        self.options_menu_01.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_01.bind('<Button-1>', self.board_selector)
        self.options_menu_01.create_text(55 + 2, 25 + 3, text="Easy", font=(self.board_font, int(font_size)))

        # self.options_menu_02 = Canvas(self.canvas_board, width=150, height=150, bg='red', highlightthickness=0)
        self.options_menu_02 = Canvas(om_master, width=110, height=56, bg='grey90')
        self.options_menu_02.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_02.bind('<Button-1>', self.board_selector)
        self.options_menu_02.create_text(55 + 2, 25 + 3, text="Hard", font=(self.board_font, int(font_size)))

    def click_solve(self):
        self.forget_options_menu()
        self.solve_button_label_disabled.pack()
        self.options_button_abort.pack()
        self.solve_board()

    def display_difficulty_menu(self):
        """ spawns difficulty menu after clicking 'select' """
        self.select_menu_container.place(relx=.5, rely=.5, anchor=CENTER)

        # todo STYLE keep both border edges or over lap them?
        self.options_menu_00.place(relx=.218, rely=.5, anchor=CENTER)
        self.options_menu_01.place(relx=.5, rely=.5, anchor=CENTER)
        self.options_menu_02.place(relx=(1 - .218), rely=.5, anchor=CENTER)

        self.solve_button_label_disabled.pack()  # re-enable solver button

        # todo: review/move
        '''
        self.make_mini_boards(test_matrices(01), 0, 0)
        self.make_mini_boards(test_matrices(02), 1, 0)
        self.make_mini_boards(test_matrices(03), 2, 0)
        #self.make_mini_boards(test_matrices(11), 0, 1)
        '''

    def create_options_menu(self):
        # place options menu stuff here
        return  # remove this

    # todo: consider FURTHER refactor ?
    def cell_shader(self, shaded_cells):
        """ colors cells dark """
        len_i = len(self.board_gui_data)
        len_j = len(self.board_gui_data[0])
        for i in range(len_i):
            for j in range(len_j):
                canvas_id = self.board_gui_data[i][j].canvas
                text_id = self.board_gui_data[i][j].text
                number = shaded_cells[i][j]
                fill = 'gray77'
                if not number:  # reset old value
                    fill = ''
                    number = ''

                self.canvas_board.itemconfigure(canvas_id, fill=fill)
                self.canvas_board.itemconfigure(text_id, text=number)
                self.canvas_board.lower(canvas_id)


    def board_selector(self, event):
        # todo: fix TestMatrices() usage
        from testing.test_cases import TestMatrices

        board = TestMatrices().matrix_00()

        if event.widget == self.options_menu_01:
            board = TestMatrices().matrix_01()
        elif event.widget == self.options_menu_02:
            board = TestMatrices().matrix_11()  # hard

        self.update_entire_board(board)
        self.cell_shader(board)
        self.solve_button_label_disabled.pack_forget()
        self.forget_options_menu()

    def update_entire_board(self, new_board) -> None:
        for i in range(len(new_board)):
            for j in range(len(new_board[0])):  # assumes rectangular
                self.board_gui_data[i][j].number = new_board[i][j]

                text_id = self.board_gui_data[i][j].text
                number = self.board_gui_data[i][j].number
                if number == 0:
                    number = ''

                self.canvas_board.itemconfig(text_id, text=number)

    def limited_update(self, changed_cells) -> None:
        if not changed_cells:
            return

        for i, j, val in changed_cells:
            self.board_gui_data[i][j].number = val

            text_id = self.board_gui_data[i][j].text
            if val == 0:  # prevents display of zeros
                val = ''

            self.canvas_board.itemconfig(text_id, text=val)

    # todo: keep here or move to solver file?
    def convert_board(self):
        """ convert to array of int arrays """
        return [[cell.number for cell in row] for row in self.board_gui_data]

    # todo: refactor out, to main
    def solve_board(self):
        from copy import deepcopy
        board_data = self.convert_board()

        from solver_engine import SolverEngine
        se = SolverEngine()

        # seed agenda
        agenda = [board_data]
        last_board = deepcopy(board_data)
        while agenda:
            curr_board = agenda.pop()
            next_empty = se.find_empty(curr_board)

            if self.abort or not next_empty:
                self.update_entire_board(curr_board)
                self.options_button_abort.pack_forget()
                self.abort = False
                break

            i, j = next_empty
            for val in range(9, 0, -1):
                curr_board[i][j] = val
                rule_h_v = se.hv_rule_check(curr_board, i, j)
                rule_s = se.s_rule_check(curr_board, i, j)
                if rule_h_v and rule_s:
                    agenda.append(deepcopy(curr_board))

                    next_limited_update = list()
                    for i_u in range(9):
                        for j_u in range(9):
                            val = curr_board[i_u][j_u]
                            if val != last_board[i_u][j_u]:
                                next_limited_update.append((i_u, j_u, val))
                    self.limited_update(next_limited_update)
                    self.master.update()  # GUI update
                    last_board = deepcopy(curr_board)


    # def solve_execute(self):
    #     self.solver_engine()


    def stop_solver(self):
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

    # todo: removed due to design change
    # def id_matrix_cleanup(self, matrix):
    #     for each_row in matrix:
    #         for each_cell in each_row:
    #             if each_cell != 0:
    #                 self.canvas_board.delete(each_cell)

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
        self.update_entire_board()
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


if __name__ == '__main__':
    BOARD_SIZE = 9
    CELL_SIZE = 50  # cell size: minimum > 25... probably

    benchmarking = False

    root = Tk()
    sudoku_gui = CanvasGUI(root, CELL_SIZE)
    root.mainloop()


'''
# TODO arrange canvas/frames/whatever NOT based on draw order COMPLETE-ISH
# TODO http://stackoverflow.com/questions/19284857/instance-attribute-attribute-name-defined-outside-init

# TODO font changes with cell size, but not with Sudoku board size

# TODO create subclasses http://stackoverflow.com/questions/17056211/python-tkinter-option-menu

# TODO cell vs element
# TODO 3d sudoku?

# TODO microsoft Visual Studio style (highlight and border when mouse over, otherwise no border)

# TODO CHANGE 50 BOARD VALUES
# todo broke scaling size with style

# TODO STYLE: offset cells for the 3 pixels lines?
# TODO STYLE: switch select and solve buttons?

# TODO REFACTOR after learning to handel these <Tkinter.Event instance at 0x02FFBF08> returned from a bind
# TODO Fix font issues

# TODO config vs configure (config == configure)
# TODO PERFORMANCE: keep greedy len matrix and, eg, keep using the greedy matrix until the current node is discarded
# TODO PERFORMANCE: cont: ... can make even better than that. don't want to get too tangent

# TODO REFACTORING: use the create_text method on canvas objects where appropriate (it inherits bindings and is transparent etc)

# TODO visual: the squares are not all exactly the same size and positions are not all exactly the same (off by a couple of pixels here and there)

# TODO visual: lots of visual hackery. bottom of mini boards are not aligned, but are otherwise aligned

# todo wtf does this do __name__ == "__main__":

# todo "create?"

# todo scaling probably a bad idea (would it ever be used? and worth the time/work?)

# todo taskbar icon not displaying

# TODO CRITICAL: i caused 2 or 3 system wide crashes. it may have been from the abort function. not going to test right now

# TODO DIST: TASKBAR ICON NOT SHOWING


'''