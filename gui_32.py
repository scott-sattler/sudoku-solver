from tkinter import *
import tempfile
from sudokuclass import solver_engine
from testing_tools import test_matrices, pretty_print, verified_solution
from time import *

# stack overflow
ICON = (b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
        b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
        b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x01\x00\x00\x00\x01') + b'\x00' * 1282 + b'\xff' * 64

_, ICON_PATH = tempfile.mkstemp()
with open(ICON_PATH, 'wb') as icon_file:
    icon_file.write(ICON)


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

class CanvasGUI:

    def __init__(self, master):
        self.master = master  # todo wtf this do?
        master.title("")
        master.iconbitmap(default=ICON_PATH)
        master.resizable(width=False, height=False)
        master.config(background="white")

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

        self.text_id_matrix = test_matrices(00)  # all zeros matrix
        self.shaded_id_matrix = test_matrices(00)  # TODO OMG I SHOULD NOT BE DOING THIS SO HACKY?
        self.text_id_small_matrix_00 = test_matrices(00)

        self.offset = 40  # todo

        # todo package this into a separate def?
        self.board_container = Canvas(
            master)  # height=50.000/9/25*self.dynamic_size, width=225.000/9/25*self.dynamic_size
        # self.board_container.config(bg='white', borderwidth=0, highlightthickness=0)
        self.board_container.pack()  # side=TOP, fill=BOTH

        # hardcoded some style stuff (offset/5+2)
        self.canvas_board = Canvas(master)
        self.canvas_board.config(height=225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2,
                                 width=225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2)
        self.canvas_board.config(bg='white', borderwidth=0, highlightthickness=0)
        self.board_canvas_width = (self.canvas_board.winfo_reqwidth()) / 9.000 / 25 * self.dynamic_size
        self.board_canvas_height = (self.canvas_board.winfo_reqheight()) / 9.000 / 25 * self.dynamic_size
        self.canvas_board.pack()
        # self.canvas_board.bind('<Button-1>', self.mini_matrix_board_selector)

        self.control_panel = Canvas(master)
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
        # highlightthickness is used to center the spacers  # todo hacky
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
        ####self.options_menu_00 = Canvas(self.canvas_board, width=150, height=150, bg='orange', highlightthickness=0)
        self.options_menu_00 = Canvas(om_master, width=110, height=56, bg='grey90')
        self.options_menu_00.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_00.bind('<Button-1>', self.board_selector)
        self.options_menu_00.create_text(55 + 2, 25 + 3, text="Empty", font=(self.board_font, int(font_size)))
        ####self.options_menu_01 = Canvas(self.canvas_board, width=149, height=150, bg='yellow', highlightthickness=0)
        self.options_menu_01 = Canvas(om_master, width=110, height=56, bg='grey90')
        self.options_menu_01.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_01.bind('<Button-1>', self.board_selector)
        self.options_menu_01.create_text(55 + 2, 25 + 3, text="Easy", font=(self.board_font, int(font_size)))
        ####self.options_menu_02 = Canvas(self.canvas_board, width=150, height=150, bg='red', highlightthickness=0)
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
        self.current_board = test_matrices(00)  # todo necessary?
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

    def cell_shader(self):  # TODO move into another function somewhere?
        self.id_matrix_cleanup(self.shaded_id_matrix)  # delete shaded cells
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.canvas_board.itemcget(self.text_id_matrix[i][j], 'text') != "":  # todo check the text value
                    self.shaded_id_matrix[i][j] = self.canvas_board.create_rectangle(j * 50 + self.offset / 8,
                                                                                     i * 50 + self.offset / 8,
                                                                                     (j + 1) * 50 + self.offset / 8,
                                                                                     (i + 1) * 50 + self.offset / 8,
                                                                                     width=0, fill="gray77")
                    self.canvas_board.lower(self.shaded_id_matrix[i][j])
                    # TODO correct i j ?

    def board_selector(self, event):
        if event.widget == self.options_menu_00:
            board = test_matrices(00)
        elif event.widget == self.options_menu_01:
            board = test_matrices(1)
        elif event.widget == self.options_menu_02:
            board = test_matrices(11)  # hard

        self.current_board = board  # todo
        self.update_board()
        self.cell_shader()
        self.solve_button_label_disabled.pack_forget()
        self.forget_options_menu()

    def update_board(self):
        # update entire board
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell_zero_check = self.current_board[i][j]  # TODO rename cell_zero_check
                if cell_zero_check == 0:
                    cell_zero_check = ""
                self.canvas_board.itemconfig(self.text_id_matrix[i][j], text=cell_zero_check)

        self.previous_board = self.current_board

    def solver_engine(self):  # TODO NAME?

        if self.agenda == []:
            self.agenda = [self.current_board]  # populate agenda with the selected board  # todo redundant??
        self.current_board = self.agenda.pop(0)  # TODO? this is unnecessary; hackery  ?
        # empty_element = self.sudoku_solver.find_empty_cell(self.current_board)
        empty_element = self.sudoku_solver.find_empty_cell_greedy(self.current_board)
        if empty_element == None or self.abort == TRUE:  # solved condition
            self.update_board()  # don't need to pass the current board

            self.agenda = []  # todo necessarY?

            # abort
            self.options_button_abort.pack_forget()
            self.abort = FALSE

            if benchmarking: self.time_2 = time(); print(self.time_2 - self.time_1)
            return

        three_rule_permitted_values = self.sudoku_solver.find_node_element_values(empty_element, self.current_board)
        self.agenda = self.sudoku_solver.extend_nodes_and_insert(self.agenda, self.current_board,
                                                                 three_rule_permitted_values)

        self.update_board()

        if self.agenda != []:
            self.master.after(1, self.solver_engine)

    def solve_execute(self):  # TODO REMOVE?
        if benchmarking: self.time_1 = time()
        self.solver_engine()

    def stop_solver(self, second):  # TODO fix second hack
        self.abort = TRUE

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

    def debug_printer(self, event):
        print("foo")
        print(event.x, event.y)

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


