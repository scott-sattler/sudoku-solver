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

    BOARD_SIZE = 9
    CELL_SIZE = 50  # cell size: minimum > 25... probably

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

        self.select_board_menu_container = None
        self.empty_board_button = None
        self.easy_board_button = None
        self.hard_board_button = None

        self.num_selector_popup = None
        self.has_lock = None
        self.can_take_lock = list()  # todo: unimplemented; unsure of


        self.title("")
        self.iconbitmap(default=ICON_PATH)
        self.resizable(width=False, height=False)
        self.config(background="white")  # "#ffffff"

        self.offset = 40  # todo
        self.dynamic_size = self.BOARD_SIZE * self.CELL_SIZE

        self.board_font = "fixedsys"
        self.font_size = int(12 / 25.000 * self.CELL_SIZE)
        self.abort = False  # todo: better way of doing this?; consider removal/refactor

        # primary data structure
        self.board_gui_data = [[CellData() for _ in range(9)] for __ in range(9)]

        self.board_index_lookup = dict()
        self.num_selector_lookup = dict()  # todo: move? reorg

        self.selected_cell = None

        self.play_board_width = 225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2  # todo: review for accuracy
        self.play_board_height = 225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2  # todo: review for accuracy

        self.title_container = tk.Canvas(self.container)
        self.play_board = tk.Canvas(self.container)

        self.play_board.config(
            height=self.play_board_height,
            width=self.play_board_width)

        self.play_board.config(bg='white', borderwidth=0, highlightthickness=0)
        self.play_board.pack()


        # todo: for testing/debugging
        self.fill_count = 0
        # self.fill = ['red',     'green',   'blue',    'yellow',  'grey', 'cyan',    'magenta', 'orange',  'purple',  'grey']  # noqa
        self.fill =   ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', 'grey', '#00FFFF', '#FF00FF', '#FF9900', '#8000FF', 'grey']  # noqa


        # todo: move to main
        # order dependent
        self.initialize_title()
        self.initialize_play_board()
        self.initialize_control_board()
        self.initialize_board_selector_menu()
        self.initialize_num_selector_popup()
        self.bindings()


    def bindings(self):
        # self.bind("<Button-1>", self.print_widget_under_mouse)

        # self.bind("<Button-1>", self.event_handler)
        self.bind("<ButtonRelease-1>", self.event_handler)
        self.bind("<Button-2>", self.event_handler)
        self.bind("<space>", lambda e: print(self.selected_cell))


    def convert_board(self):
        """ convert to array of int arrays """
        return [[cell.value for cell in row] for row in self.board_gui_data]

    def event_handler(self, e):
        empty_board = self.empty_board_button
        easy_board = self.easy_board_button
        hard_board = self.hard_board_button
        boards = [empty_board, easy_board, hard_board]

        def board_input(event):
            board = event.widget  # play board OR num selector
            x = event.x_root - board.winfo_rootx()
            y = event.y_root - board.winfo_rooty()
            cb = self.play_board
            cbw = cb.winfo_reqwidth()
            cbh = cb.winfo_reqwidth()
            offset = self.offset / (self.BOARD_SIZE - 1)  # canvas lines/cells offset

            # if the mouse event occurred within the event's board
            if (cbw - offset) > x > offset and (cbh - offset) > y > offset:
                obj_ids = board.find_closest(x, y)
                id_ = obj_ids[0]

                # if board cell was selected
                if board.gettags(id_)[0] == 'cell':
                    # i, j = self.board_index_lookup.get(id_)
                    # is_locked = self.board_gui_data[i][j].locked
                    # if is_locked:
                    #     return

                    if not self.selected_cell:
                        self.selected_cell = self.board_index_lookup.get(id_)
                    else:
                        self.selected_cell = None
                    self.toggle_num_selector(event)

                # if the num selector was selected
                elif board.gettags(id_)[0] == 'num':
                    val = self.num_selector_lookup.get(id_)
                    i, j = self.selected_cell
                    pb_obj_id = self.board_gui_data[i][j].canvas_id

                    self.limited_update([(i, j, val), ])
                    self.selected_cell = None
                    self.toggle_num_selector(event)

                    cb.itemconfigure(pb_obj_id, fill=self.fill[self.fill_count])
                    self.fill_count = (self.fill_count + 1) % len(self.fill)

        # todo: refactor matrix import into main
        def board_selector(event):
            from testing.test_cases import TestMatrices

            board = TestMatrices().matrix_00()

            if event.widget == self.easy_board_button:
                board = TestMatrices().matrix_01()
            elif event.widget == self.hard_board_button:
                board = TestMatrices().matrix_11()  # hard

            self.update_entire_board(board)
            self.cell_shader(board)
            self.solve_button['state'] = tk.NORMAL
            self.select_board_menu_container.place_forget()

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
                self.select_board_menu_container.place_forget()
                self.select_button['state'] = tk.DISABLED
                solve_board()
                self.select_button['state'] = tk.NORMAL
            else:  # solve_button.cget('text') == 'ABORT?'
                self.abort = True

        def reset_state():
            self.select_board_menu_container.place_forget()
            self.num_selector_popup.place_forget()
            self.selected_cell = None
            self.has_lock = None

        if e.num == 2:
            self.debugging_tools_change_obj_color(e)
            return

        print(e, e.widget)

        # if debug: print("<Button-1>") if e.num == 1 else ...
        if e.widget in [self.play_board, self.num_selector_popup]:
            """ handles board user entry """
            # ~ self.select_board_menu_container.winfo_viewable():
            if self.has_lock in [None, self.play_board]:
                board_input(e)
                self.has_lock = self.play_board
            else:
                reset_state()
        elif e.widget == self.select_button and self.select_button['state'] != tk.DISABLED:
            """ spawns difficulty menu after clicking 'select' """
            # does not have lock
            if self.has_lock != self.select_board_menu_container:
                # other has lock
                if self.has_lock is not None:
                    reset_state()
                """ place() doesn't work without arguments ??? """
                """ even if place(*args) is called at creation """
                self.select_board_menu_container.place(
                    relx=.5, rely=.5, width=400, height=100, anchor=tk.CENTER)
                self.has_lock = self.select_board_menu_container
            # ~ self.select_board_menu_container.winfo_viewable():
            elif self.select_board_menu_container == self.has_lock:
                # self.select_board_menu_container.place_forget()
                # self.has_lock = None
                reset_state()
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
        self.update()

    def initialize_title(self):
        font_size = self.font_size

        self.title_container = tk.Canvas(self.container)
        self.title_container.config(borderwidth=0, highlightthickness=0)
        self.title_container.pack(before=self.play_board)  # todo: order of execution dependence

        self.title_label = tk.Label(
            self.title_container,
            text="SUDOKU SOLVER",
            font=(self.board_font, font_size * 2),
            bg="#fff",
            padx=20,
        )
        self.title_label.pack()

    def initialize_play_board(self):
        """
        - create board lines
        - initialize (populate) board_gui_data matrix
            create canvas and text box for each cell
        """
        board_size = len(self.board_gui_data)

        font_size = self.font_size
        cell_size = self.CELL_SIZE
        offset = self.offset
        cbw = self.play_board.winfo_reqwidth()
        cbh = self.play_board.winfo_reqheight()

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
            self.play_board.create_line(x_0, y_0, x_1, y_1, width=width)

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
            self.play_board.create_line(x_0, y_0, x_1, y_1, width=width)

        # initialize board_gui_data matrix
        # creates canvas and text box for each cell
        for i in range(len(self.board_gui_data)):
            for j in range(len(self.board_gui_data[0])):  # assumes rectangular
                canvas_id = self.play_board.create_rectangle(
                    j * 50 + self.offset / 8,
                    i * 50 + self.offset / 8,
                    (j + 1) * 50 + self.offset / 8,
                    (i + 1) * 50 + self.offset / 8,
                    width=0, fill="#ffffff",
                    tags="cell",
                )

                txt_id = self.play_board.create_text(
                    cell_size / 2 + (j * cell_size) + 4,
                    cell_size / 2 + (i * cell_size) + 4,
                    font=(self.board_font, font_size),
                    text='',  # str(i) + str(j)
                    tags="cell",
                )

                self.play_board.lower(canvas_id)
                self.board_gui_data[i][j].canvas_id = canvas_id
                self.board_gui_data[i][j].text_id = txt_id

                self.board_index_lookup[txt_id] = (i, j)
                self.board_index_lookup[canvas_id] = (i, j)

    def initialize_num_selector_popup(self):
        # todo: minor misalignment... rounding errors?
        cell_size = self.CELL_SIZE
        width = cell_size * 3
        height = cell_size * 3
        border_width = 3
        rect_b_width = 2

        self.num_selector_popup = tk.Canvas(self.play_board)
        self.num_selector_popup.config(
            width=width,
            height=height,

            highlightthickness=0,
            borderwidth=border_width,
            bg='white',
            # relief='flat',
        )
        self.num_selector_popup.place(relx=0, rely=0)
        self.num_selector_popup["state"] = tk.DISABLED
        self.num_selector_popup.place_forget()

        for i in range(3):
            for j in range(3):
                canvas_id = self.num_selector_popup.create_rectangle(
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

                text_id = self.num_selector_popup.create_text(
                    j * (width / 3) + (border_width + rect_b_width + cell_size) / 2,
                    i * (width / 3) + (border_width + rect_b_width + cell_size) / 2,
                    font=(self.board_font, self.font_size),
                    text=num,
                    tags='num',
                )
                self.num_selector_lookup[text_id] = num

    def initialize_control_board(self):
        """ these buttons differ from board select menu buttons """
        def formatted_button(master, text, font_resize):
            font_size = int(self.font_size * font_resize)
            button = tk.Button(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg='white', relief='sunken', borderwidth=0)
            button.config(font=(self.board_font, font_size))
            return button

        # note: Canvas has useful options and functionality versus Frame
        self.control_panel_container = tk.Canvas(self.container)
        self.control_panel_container.config(
            height=self.CELL_SIZE,
            width=self.play_board.winfo_reqwidth())
        self.control_panel_container.pack(fill=tk.Y, side=tk.BOTTOM, pady=10)

        # solve, verify, and select buttons
        cpc = self.control_panel_container  # buttons parent

        self.solve_button = formatted_button(cpc, 'SOLVE', 1.2)
        self.solve_button.grid(row=0, column=0)
        self.solve_button['state'] = tk.DISABLED

        self.verify_button = formatted_button(cpc, 'VERIFY', 1.2)
        self.verify_button.grid(row=0, column=1)

        self.select_button = formatted_button(cpc, 'SELECT', 1.2)
        self.select_button.grid(row=0, column=2)

    def initialize_board_selector_menu(self):
        """ to add borders, these buttons differ from control board buttons """
        def formatted_button(master, text, font_resize):
            # """ border necessary due to tk limitations """
            # border = tk.Frame(master, highlightbackground='black', highlightthickness=2)
            # font_size = int(self.font_size * font_resize)
            # button = tk.Button(border)
            # button.config(text=text, anchor=tk.CENTER)
            # button.config(bg='white', relief='sunken', borderwidth=0)
            # button.config(font=(self.board_font, font_size))
            # button.config(height=1, width=7)  # width in chars
            # button.pack()
            # return border

            """  """
            """ labels necessary due to tk limitations """
            """ functionally most similar to buttons """
            font_size = int(self.font_size * font_resize)
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg='white', relief='sunken', borderwidth=0)
            button.config(highlightbackground='black', highlightthickness=2)
            button.config(font=(self.board_font, font_size))
            button.config(height=1, width=7)  # width in chars
            button.config(pady=8)
            return button

        # difficulty selector backdrop
        self.select_board_menu_container = (tk.Canvas(self.play_board))
        self.select_board_menu_container.config(
            highlightthickness=2, highlightbackground='black')

        # exclusively for button alignment  # todo: local?
        select_board_menu_backdrop = (tk.Frame(self.select_board_menu_container))
        select_board_menu_backdrop.place(relx=.5, rely=.5, anchor=tk.CENTER)

        size = .8  # button font relative size
        sbmb = select_board_menu_backdrop

        self.empty_board_button = formatted_button(sbmb, "Empty", size)
        self.empty_board_button.grid(row=0, column=1)

        self.easy_board_button = formatted_button(sbmb, "Easy", size)
        self.easy_board_button.grid(row=0, column=2)

        self.hard_board_button = formatted_button(sbmb, "Hard", size)
        self.hard_board_button.grid(row=0, column=3)

    # todo: consider refactor ?
    def cell_shader(self, shaded_cells):
        """ colors cells dark """
        for i in range(len(self.board_gui_data)):
            for j in range(len(self.board_gui_data[0])):
                canvas_id = self.board_gui_data[i][j].canvas_id
                text_id = self.board_gui_data[i][j].text_id
                number = shaded_cells[i][j]
                fill = 'gray77'
                if not number:  # reset old value
                    fill = ''
                    number = ''

                self.play_board.itemconfigure(canvas_id, fill=fill)
                self.play_board.itemconfigure(text_id, text=number)
                self.play_board.lower(canvas_id)
                self.board_gui_data[i][j].locked = True

    def limited_update(self, changed_cells) -> None:
        """ changed_cells parameter of type [(i, j, value)] """
        if not changed_cells:
            return

        for i, j, val in changed_cells:
            self.board_gui_data[i][j].value = val

            text_id = self.board_gui_data[i][j].text_id
            if val == 0:  # prevents display of zeros
                val = ''

            self.play_board.itemconfig(text_id, text=val)

    def update_entire_board(self, new_board) -> None:
        for i in range(len(new_board)):
            for j in range(len(new_board[0])):  # assumes rectangular
                self.board_gui_data[i][j].value = new_board[i][j]

                text_id = self.board_gui_data[i][j].text_id
                number = self.board_gui_data[i][j].value
                if number == 0:
                    number = ''

                self.play_board.itemconfig(text_id, text=number)

    def toggle_num_selector(self, e):
        board_width = self.play_board.winfo_width()
        board_height = self.play_board.winfo_height()
        x = e.x_root - self.play_board.winfo_rootx()
        y = e.y_root - self.play_board.winfo_rooty()
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

        if not self.num_selector_popup.winfo_viewable():
            self.num_selector_popup.place(relx=x_rel, rely=y_rel, anchor=anchor)
        else:
            self.num_selector_popup.place_forget()


    def debugging_tools_change_obj_color(self, e):
        # bug: does not correctly change color of main board's numbers

        board = e.widget
        print(board)

        board = e.widget  # play board OR num selector
        x = e.x_root - board.winfo_rootx()
        y = e.y_root - board.winfo_rooty()
        print(x, y)

        print(board.winfo_children())

        obj_ids = []
        if hasattr(board, 'find_closest'):
            obj_ids = board.find_closest(x, y)
        obj_tags = ()
        if hasattr(board, 'gettags'):
            obj_tags = board.gettags("current")

        print('obj_tag', obj_tags)
        print('items', obj_ids)

        id_ = None
        if obj_ids:
            id_ = obj_ids[0]
        tag = None
        if obj_tags:
            tag = obj_tags[0]

        if tag == 'cell':
            i, j = self.board_index_lookup.get(id_)
            play_board_id = self.board_gui_data[i][j].canvas_id
            self.play_board.itemconfigure(play_board_id, fill=self.fill[self.fill_count])
        elif tag == 'num':
            board.itemconfigure(id_, fill=self.fill[self.fill_count])
        elif obj_tags:
            board.itemconfigure(id_, fill=self.fill[self.fill_count])
        else:
            board.config(background=self.fill[self.fill_count])

        self.fill_count = (self.fill_count + 1) % len(self.fill)
        print()



    # todo: deprecated
    # # todo move?
    # def forget_options_menu(
    #         self):  # TODO REMOVE THIS? just use self.select_board_menu_container.place_forget() where ever it was called
    #     # todo can use state=normal/disabled/hidden
    #     self.select_board_menu_container.place_forget()
    #     '''
    #     self.empty_board_button.place_forget()
    #     self.easy_board_button.place_forget()
    #     self.hard_board_button.place_forget()
    #     '''
    #     # self.empty_board_button.grid_forget()
    #     # self.easy_board_button.grid_forget()
    #     # self.hard_board_button.grid_forget()


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
