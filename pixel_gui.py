import tkinter as tk
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


class CellData:
    def __init__(self, value=None, text_id=None, canvas_id=None, locked=False):
        self.value = value  # actual value to display (as text)
        self.text_id = text_id
        self.canvas_id = canvas_id
        self.locked = locked  # locked when loading a board

    def __repr__(self):
        return str((self.value, self.text_id, self.canvas_id))


class CanvasGUI(tk.Tk):
    # todo: lock loaded board cells

    def __init__(self, *args, **kwargs):


        debug = False

        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)
        self.container.config(background="white")
        self.container.pack(side="top", fill="both", expand=True)

        # self.container.grid_rowconfigure(0, weight=1)
        # self.container.grid_columnconfigure(0, weight=1)

        if debug: return  # noqa

        # todo: some sort of container, eg dictionary
        self.button_lookup = dict()

        self.title_label = None

        self.control_panel_container = None
        self.solve_button = None
        self.select_button = None
        self.verify_button = None

        self.select_menu_container = None
        self.options_menu_00 = None
        self.options_menu_01 = None
        self.options_menu_02 = None

        self.num_selector = None


        self.title("")
        self.iconbitmap(default=ICON_PATH)
        self.resizable(width=False, height=False)
        # self.config(background="white")
        self.config(background="#ffffff")

        self.cell_size = 50
        cell_size = 50
        self.offset = 40  # todo
        self.dynamic_size = BOARD_SIZE * cell_size

        self.board_font = "fixedsys"
        self.font_size = int(12 / 25.000 * cell_size)
        self.abort = False  # todo better way of doing this?

        # primary data structure
        self.board_gui_data = [[CellData() for _ in range(9)] for __ in range(9)]

        self.board_index_lookup = dict()
        self.num_selector_lookup = dict()  # todo: move? reorg

        self.selected_cell = None

        self.board_width = 465
        # self.board_height =
        self.canvas_board_width = 225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2  # todo: review for accuracy
        self.canvas_board_height = 225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2  # todo: review for accuracy
        # print('w', self.canvas_board_width, 'h', self.canvas_board_height)

        self.title_container = tk.Canvas(self.container)
        # self.title_container.pack()

        self.canvas_board = tk.Canvas(self.container)
        # self.canvas_board.bind("<Button-1>", self.event_handler)
        # self.canvas_board.bind("<Button-1>", self.process_user_input)
        # self.canvas_board.pack()

        self.canvas_board.config(
            height=self.canvas_board_height,
            width=self.canvas_board_width
        )

        self.canvas_board_width = self.canvas_board.winfo_reqwidth()  # todo: why tho?
        self.canvas_board_height = self.canvas_board.winfo_reqheight()  # todo: why tho?
        # print('cb.winfo_req_', self.canvas_board.winfo_reqwidth(), self.canvas_board.winfo_reqheight())

        self.canvas_board.config(borderwidth=0, highlightthickness=0)
        self.canvas_board.config(bg='white')
        # self.board_canvas_width = (self.canvas_board.winfo_reqwidth()) / 9.000 / 25 * self.dynamic_size
        # self.board_canvas_height = (self.canvas_board.winfo_reqheight()) / 9.000 / 25 * self.dynamic_size
        # print('w', self.board_canvas_width, 'h', self.board_canvas_height)
        self.canvas_board.pack()
        # self.canvas_board.bind('<Button-1>', self.mini_matrix_board_selector)


        self.fill_count = 0  # todo: for testing/debugging
        # ["#FFFFFF", "#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF", "#C0C0C0", "#808080", "#800000", "#808000", "#008000", "#800080", "#008080", "#000080"]  # noqa
        # self.fill = ['red',     'green',   'blue',    'yellow',  'grey', 'cyan',    'magenta', 'orange',  'purple',  'grey']  # noqa
        self.fill =   ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', 'grey', '#00FFFF', '#FF00FF', '#FF9900', '#8000FF', 'grey']  # noqa

        # todo: move to main
        # order dependent
        self.create_title()
        self.initialize_board()
        self.controls()

        self.initialize_num_selector_popup()
        self.bindings()



    def bindings(self):
        # self.bind("<Button-1>", self.print_widget_under_mouse)

        self.bind("<Button-1>", self.event_handler)
        # self.bind("<Button-3>", self.event_handler)



    def initialize_num_selector_popup(self):
        # todo: minor misalignment... rounding errors?
        cell_size = self.cell_size
        width = cell_size * 3
        height = cell_size * 3
        border_width = 3
        rect_b_width = 2

        self.num_selector = tk.Canvas(self.canvas_board)
        self.num_selector.config(
            width=width,
            height=height,

            highlightthickness=0,
            borderwidth=border_width,
            bg='white',
            # relief='flat',
        )
        self.num_selector.place(relx=0, rely=0)
        self.num_selector["state"] = tk.DISABLED
        self.num_selector.place_forget()

        for i in range(3):
            for j in range(3):
                canvas_id = self.num_selector.create_rectangle(
                    j * (width/3) + border_width + rect_b_width,
                    i * (width/3) + border_width + rect_b_width,
                    j * (width/3) + cell_size + border_width/3,
                    i * (width/3) + cell_size + border_width/3,
                    width=rect_b_width, fill=self.fill[self.fill_count],  # fill='cyan',
                    tags='num',
                )

                self.fill_count = (self.fill_count + 1) % len(self.fill)
                num = (i * 3) + (j + 1)
                self.num_selector_lookup[canvas_id] = num

                text_id = self.num_selector.create_text(
                    j * (width / 3) + (border_width + rect_b_width + cell_size) / 2,
                    i * (width / 3) + (border_width + rect_b_width + cell_size) / 2,
                    font=(self.board_font, self.font_size),
                    text=num,
                    tags='num',
                )
                self.num_selector_lookup[text_id] = num

    def convert_board(self):
        """ convert to array of int arrays """
        return [[cell.value for cell in row] for row in self.board_gui_data]

    def event_handler(self, e):
        debug = False  # todo: remove
        if debug:
            print(e, e.widget)
            print()

        empty_board = self.options_menu_00
        easy_board = self.options_menu_01
        hard_board = self.options_menu_02
        boards = [empty_board, easy_board, hard_board]

        def board_input(event):
            debug = False  # todo: remove
            offset = self.offset / 8  # canvas lines/cells offset

            board = event.widget
            x = event.x_root - board.winfo_rootx()
            y = event.y_root - board.winfo_rooty()
            cbw = self.canvas_board_width  # todo: change this to something like, self.canvas_board.winfo_reqwidth()
            cbh = self.canvas_board_height  # todo: change this to something like, self.canvas_board.winfo_reqwidth()
            cb = self.canvas_board
            if (cbw - offset) > x > offset and (cbh - offset) > y > offset:
                obj_ids = board.find_closest(x, y)
                current = board.gettags("current")
                if debug: print('items', obj_ids, 'current', current)  # noqa
                for id_ in obj_ids:
                    if not id_: continue
                    if current and board.gettags(id_)[0] == 'cell':
                        if debug: print('(i, j):', self.board_index_lookup.get(id_))  # noqa
                        self.selected_cell = self.board_index_lookup.get(id_)
                        self.toggle_selector(event)
                    elif current and board.gettags(id_)[0] == 'num':
                        val = self.num_selector_lookup.get(id_)
                        i, j = self.selected_cell
                        if debug: print('i j val:', (i, j, val))  # noqa
                        self.limited_update([(i, j, val), ])
                        self.selected_cell = None
                        self.toggle_selector(event)

                    board.itemconfigure(id_, fill=self.fill[self.fill_count])
                    self.fill_count = (self.fill_count + 1) % len(self.fill)

        def board_selector(event):
            # todo: fix TestMatrices() usage
            from testing.test_cases import TestMatrices

            board = TestMatrices().matrix_00()
            print(event, event.widget)
            if event.widget == self.options_menu_01:
                board = TestMatrices().matrix_01()
            elif event.widget == self.options_menu_02:
                board = TestMatrices().matrix_11()  # hard

            self.update_entire_board(board)
            self.cell_shader(board)  # todo: incorporate lock here ?
            self.solve_button.config(text='SOLVE')
            self.solve_button['state'] = tk.NORMAL
            self.select_menu_container.place_forget()

        def solve_board():
            from solver_engine import SolverEngine
            se = SolverEngine()

            board_data = self.convert_board()
            generator_solver = se.solve_board(board_data)

            for next_limited_update in generator_solver:
                if self.abort:
                    # generator_solver.send('stop')
                    self.abort = False
                    break

                if not next_limited_update:
                    break
                self.limited_update(next_limited_update)
                self.update()

            self.solve_button.config(text='SOLVE')
            self.solve_button['state'] = tk.DISABLED

            self.select_button['state'] = tk.NORMAL

        def click_solve():
            if self.solve_button['state'] == tk.DISABLED:
                return
            if self.solve_button.cget('text') == 'SOLVE':
                self.solve_button.config(text='ABORT?')
                self.select_menu_container.place_forget()
                self.select_button['state'] = tk.DISABLED
                solve_board()
                self.select_button['state'] = tk.NORMAL
            else:  # solve_button.cget('text') == 'ABORT?'
                self.abort = True

        print('mouse-button:', e.num)
        if e.widget in [self.canvas_board, self.num_selector]:
            """ handles board user entry """
            board_input(e)
        elif e.widget == self.select_button and self.select_button['state'] != tk.DISABLED:
            """ spawns difficulty menu after clicking 'select' """
            if self.select_menu_container.winfo_viewable():
                self.select_menu_container.place_forget()
            else:
                """ place() doesn't work without arguments """
                """ even if place(*args) is called at creation """
                self.select_menu_container.place(relx=.5, rely=.5, anchor=tk.CENTER)
        elif e.widget in boards:
            board_selector(e)
        elif e.widget == self.solve_button:
            click_solve()
        elif e.widget == self.verify_button:
            from solver_engine import SolverEngine
            se = SolverEngine()
            if se.validate_board(self.convert_board()):
                print('VALIDATED! :D')
            else:
                print('INVALID BOARD! :(')

    # todo: move fn down
    def toggle_selector(self, e):
        board_width = self.canvas_board.winfo_width()
        board_height = self.canvas_board.winfo_height()
        x = e.x_root - self.canvas_board.winfo_rootx()
        y = e.y_root - self.canvas_board.winfo_rooty()
        x_rel = x / board_width
        y_rel = y / board_height

        # anchor = tk.NW
        anchor = ''
        if .33 < y_rel < .66 and .33 < x_rel < .66:
            anchor = 'nw'

        if y_rel > .66:
            anchor = 's'
        elif y_rel < .33:
            anchor = 'n'
        if x_rel > .66:
            anchor += 'e'
        elif x_rel < .33:
            anchor += 'w'

        if self.num_selector.cget("state") == tk.DISABLED:
            self.num_selector["state"] = tk.NORMAL
            self.num_selector.place(relx=x_rel, rely=y_rel, anchor=anchor)
            self.num_selector.focus_set()
        else:
            self.num_selector["state"] = tk.DISABLED
            self.num_selector.place_forget()


    def create_title(self):
        font_size = self.font_size

        self.title_container = tk.Canvas(self.container)
        self.title_container.config(borderwidth=0, highlightthickness=0)
        self.title_container.pack(before=self.canvas_board)  # todo: order of execution dependence

        self.title_label = tk.Label(
            self.title_container,
            text="SUDOKU SOLVER",
            font=(self.board_font, font_size * 2),
            bg="#fff",
            padx=20,
        )
        self.title_label.pack()

    def initialize_board(self):
        """
        - create board lines
        - initialize (populate) board_gui_data matrix
            create canvas and text box for each cell
        """
        board_size = len(self.board_gui_data)

        font_size = self.font_size
        cell_size = self.cell_size
        offset = self.offset
        cbw = self.canvas_board.winfo_reqwidth()
        cbh = self.canvas_board.winfo_reqheight()

        # board_width = self.board_width

        # create lines (the +4 is the grid offset from the cells - style)
        for x_shift in range(board_size - 1):
            if (x_shift + 1) % 3 != 0:
                x_0 = (x_shift + 1) * cell_size + offset / 8
                x_1 = (x_shift + 1) * cell_size + offset / 8
                y_0 = 0 + offset / 8
                y_1 = cbh - offset / 8
                width = 1
            else:
                x_0 = (x_shift + 1) * cell_size + offset / 10
                x_1 = (x_shift + 1) * cell_size + offset / 10
                y_0 = 0
                y_1 = cbh
                width = 3
            self.canvas_board.create_line(x_0, y_0, x_1, y_1, width=width)

        for y_shift in range(board_size - 1):
            if (y_shift + 1) % 3 != 0:
                x_0 = 0 + offset / 8
                x_1 = cbh - offset / 8
                y_0 = (y_shift + 1) * cell_size + offset / 8
                y_1 = (y_shift + 1) * cell_size + offset / 8
                width = 1
            else:
                x_0 = 0
                x_1 = cbh
                y_0 = (y_shift + 1) * cell_size + offset / 8
                y_1 = (y_shift + 1) * cell_size + offset / 8
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
                    width=0, fill="#ffffff",
                    tags="cell",
                )

                txt_id = self.canvas_board.create_text(
                    cell_size / 2 + (j * cell_size) + 4,
                    cell_size / 2 + (i * cell_size) + 4,
                    font=(self.board_font, font_size),
                    text='',  # str(i) + str(j)
                    tags="cell",
                )

                self.canvas_board.lower(canvas_id)
                self.board_gui_data[i][j].canvas_id = canvas_id
                self.board_gui_data[i][j].text_id = txt_id

                self.board_index_lookup[txt_id] = (i, j)
                self.board_index_lookup[canvas_id] = (i, j)


    def controls(self):
        # todo: consider self.matrix_select["menu"].config(bg='white') vs config

        font_size = self.font_size * 1.2

        # todo refactor
        def create_and_configure(instance, text=None):
            font_size = self.font_size * 1.2
            if type(instance) is not type(tk.Canvas()):
                instance.config(font=(self.board_font, int(font_size)))
            instance.config(bg='white', borderwidth=0, highlightthickness=0)
            if type(instance) is type(tk.Button()):
                instance.config(text=text, anchor=tk.CENTER)
                instance.config(relief='sunken', borderwidth=0)
                instance.config(font=(self.board_font, int(font_size)))

        # note: Canvas has useful options and functionality versus Frame
        self.control_panel_container = tk.Canvas(self.container)
        create_and_configure(self.control_panel_container)
        self.control_panel_container.config(
            height=self.cell_size, width=self.canvas_board.winfo_reqwidth(),
        )
        self.control_panel_container.pack(fill=tk.Y, side=tk.BOTTOM, pady=10)


        # solve button
        self.solve_button = tk.Button(self.control_panel_container)
        # self.solve_button.place(relx=1/4, rely=.5, anchor=tk.CENTER)
        create_and_configure(self.solve_button, 'SOLVE')
        self.solve_button['state'] = tk.DISABLED
        self.solve_button.grid(row=0, column=0)

        # verify button
        self.verify_button = tk.Button(self.control_panel_container)
        create_and_configure(self.verify_button, 'VERIFY')
        # self.verify_button.place(relx=2/4, rely=.5, anchor=tk.CENTER)
        self.verify_button.grid(row=0, column=1)

        # select button
        self.select_button = tk.Button(self.control_panel_container)
        create_and_configure(self.select_button, 'SELECT')
        # self.select_button.place(relx=3/4, rely=.5, anchor=tk.CENTER)
        self.select_button.grid(row=0, column=2)



        # todo: refactor this menu
        # difficulty selector
        self.select_menu_container = tk.Canvas(self.canvas_board, width=400, height=100)

        self.options_menu_00 = tk.Canvas(self.select_menu_container, width=110, height=56, bg='grey90')
        self.options_menu_00.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_00.bind('<Button-1>', self.event_handler)
        self.options_menu_00.create_text(55 + 2, 25 + 3, text="Empty", font=(self.board_font, int(font_size)))

        self.options_menu_01 = tk.Canvas(self.select_menu_container, width=110, height=56, bg='grey90')
        self.options_menu_01.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_01.bind('<Button-1>', self.event_handler)
        self.options_menu_01.create_text(55 + 2, 25 + 3, text="Easy", font=(self.board_font, int(font_size)))

        self.options_menu_02 = tk.Canvas(self.select_menu_container, width=110, height=56, bg='grey90')
        self.options_menu_02.config(highlightthickness=2, highlightbackground='black')
        self.options_menu_02.bind('<Button-1>', self.event_handler)
        self.options_menu_02.create_text(55 + 2, 25 + 3, text="Hard", font=(self.board_font, int(font_size)))

        # todo: consider previews?
        # self.select_menu_container.place(relx=.5, rely=.5, anchor=tk.CENTER)
        # self.select_menu_container.place_forget()

        # OLD todo STYLE keep both border edges or over lap them?
        self.options_menu_00.place(relx=.218, rely=.5, anchor=tk.CENTER)
        self.options_menu_01.place(relx=.5, rely=.5, anchor=tk.CENTER)
        self.options_menu_02.place(relx=(1 - .218), rely=.5, anchor=tk.CENTER)



    def create_options_menu(self):
        # place options menu stuff here
        return  # remove this

    # todo: consider refactor ?
    def cell_shader(self, shaded_cells):
        """ colors cells dark """
        len_i = len(self.board_gui_data)
        len_j = len(self.board_gui_data[0])
        for i in range(len_i):
            for j in range(len_j):
                canvas_id = self.board_gui_data[i][j].canvas_id
                text_id = self.board_gui_data[i][j].text_id
                number = shaded_cells[i][j]
                fill = 'gray77'
                if not number:  # reset old value
                    fill = ''
                    number = ''

                self.canvas_board.itemconfigure(canvas_id, fill=fill)
                self.canvas_board.itemconfigure(text_id, text=number)
                self.canvas_board.lower(canvas_id)



    def update_entire_board(self, new_board) -> None:
        for i in range(len(new_board)):
            for j in range(len(new_board[0])):  # assumes rectangular
                self.board_gui_data[i][j].value = new_board[i][j]

                text_id = self.board_gui_data[i][j].text_id
                number = self.board_gui_data[i][j].value
                if number == 0:
                    number = ''

                self.canvas_board.itemconfig(text_id, text=number)

    def limited_update(self, changed_cells) -> None:
        """ changed_cells parameter of type [(i, j, value)] """
        if not changed_cells:
            return

        for i, j, val in changed_cells:
            self.board_gui_data[i][j].value = val

            text_id = self.board_gui_data[i][j].text_id
            if val == 0:  # prevents display of zeros
                val = ''

            self.canvas_board.itemconfig(text_id, text=val)


    def print_widget_under_mouse(self, e):
        offset = 5  # canvas border offset

        print('\n' + str(e))
        print(self.winfo_width(), self.winfo_height())

        x_rel = self.winfo_pointerx()
        y_rel = self.winfo_pointery()
        widget = self.winfo_containing(x_rel, y_rel)

        x = e.x_root - self.canvas_board.winfo_rootx()
        y = e.y_root - self.canvas_board.winfo_rooty()

        print('xy rel:', x, y)
        print('xy abs:', x_rel, y_rel)

        print("widget:", widget, widget.winfo_id())
        print(type(widget))

        self.fill_count = (self.fill_count + 1) % len(self.fill)

        cbw = self.canvas_board_width
        cbh = self.canvas_board_height
        cb = self.canvas_board
        if (cbw - offset) > x > offset and (cbh - offset) > y > offset:
            obj_ids = cb.find_closest(x, y)
            current = cb.gettags("current")
            print('items', obj_ids, 'current', current)
            for id_ in obj_ids:
                if not id_:
                    continue
                if current and cb.gettags(id_)[0] == 'cell':
                    cb.itemconfigure(id_, fill=self.fill[self.fill_count])



    # todo: deprecated
    # # todo move?
    # def forget_options_menu(
    #         self):  # TODO REMOVE THIS? just use self.select_menu_container.place_forget() where ever it was called
    #     # todo can use state=normal/disabled/hidden
    #     self.select_menu_container.place_forget()
    #     '''
    #     self.options_menu_00.place_forget()
    #     self.options_menu_01.place_forget()
    #     self.options_menu_02.place_forget()
    #     '''
    #     # self.options_menu_00.grid_forget()
    #     # self.options_menu_01.grid_forget()
    #     # self.options_menu_02.grid_forget()


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

    # root_frame = tk()
    # sudoku_gui = CanvasGUI(root_frame, CELL_SIZE)  # .pack(side="top", fill="both", expand=True)
    # root_frame.mainloop()
    app = CanvasGUI()
    app.mainloop()

'''

# TODO http://stackoverflow.com/questions/19284857/instance-attribute-attribute-name-defined-outside-init

# TODO create subclasses http://stackoverflow.com/questions/17056211/python-tkinter-option-menu

# TODO 3d sudoku?

# TODO microsoft Visual Studio style (highlight and border when mouse over, otherwise no border)

# TODO CHANGE 50 BOARD VALUES

# todo broke scaling size with style
# TODO font changes with cell size, but not with Sudoku board size

# TODO STYLE: offset cells for the 3 pixels lines?

# todo taskbar icon not displaying

'''
