import tkinter as tk
import tempfile
from old.OLD_testing_tools import test_matrices

# from time import *

ICON = (b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
        b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
        b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x01\x00\x00\x00\x01') + b'\x00' * 1282 + b'\xff' * 64

_, ICON_PATH = tempfile.mkstemp()
with open(ICON_PATH, 'wb') as icon_file:
    icon_file.write(ICON)


class CellData:
    def __init__(self, value=None, text_id=None, canvas_id=None, locked=False):
        self.value = value  # actual value to display (as text)
        self.text_id = text_id
        self.canvas_id = canvas_id
        self.locked = locked  # locked when loading a board
        # self.parent = None
        # self.color = '#ffffff'

    # def set_color(self, color=None) -> None:
    #     if color is None:
    #         color = self.color
    #     else:
    #         self.color = color
    #     self.parent.itemconfigure(fill=color)

    def __repr__(self):
        return str((self.value, self.text_id, self.canvas_id))


class CanvasGUI(tk.Tk):
    BOARD_SIZE = 9
    CELL_SIZE = 50

    def __init__(self, *args, **kwargs):
        import matrix_library as ml

        print('''
        todo: load/generate boards
        review and resolve existing todos
        
        ''')

        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)
        self.container.config(background="#ffffff")
        self.container.pack(side="top", fill="both", expand=True)

        self.title('')
        self.iconbitmap(default=ICON_PATH)
        self.resizable(width=False, height=False)
        self.config(background="#ffffff")  # white

        self.offset = 40  # todo
        self.dynamic_size = self.BOARD_SIZE * self.CELL_SIZE

        self.board_font = "fixedsys"
        self.font_size = int(12 / 25.000 * self.CELL_SIZE)
        self.abort = False  # todo: better way of doing this?; consider removal/refactor

        self.title_text = 'SUDOKU SOLVER'
        self.title_container = None
        self.title_label = None

        self.play_board = None

        self.control_panel_container = None
        self.solve_button = None
        self.select_button = None
        self.verify_button = None

        self.colors_button = None  # todo: implement
        self.cell_colors = False

        self.select_board_menu_container = None
        self.empty_board_button = None
        self.easy_board_button = None
        self.hard_board_button = None

        self.num_selector_popup = None

        self.board_state = None  # default/initialization state  # todo: recosider?
        self.board_state_change = False
        # self.is_solvable = False
        self.board_loaded = False  # todo: reconsider ?
        self.selected_cell = None
        self.has_lock = None
        self.can_take_lock = list()  # todo: unimplemented; unsure of

        self.validation_message = None

        self.board_index_lookup = dict()
        self.num_selector_lookup = dict()

        """ primary data structure """
        self.board_gui_data = [[CellData() for _ in range(9)] for __ in range(9)]

        # todo: review
        self.play_board_width = 225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2
        self.play_board_height = 225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2

        self.title_container = tk.Canvas(self.container)

        self.play_board = tk.Canvas(self.container)
        self.play_board.config(
            height=self.play_board_height,
            width=self.play_board_width,
            bg='#ffffff', borderwidth=0, highlightthickness=0,
        )
        self.play_board.pack()

        self.fill_count = 0  # allows cycling; current only in debug keybind
        '''            red        green      blue       yellow     grey       cyan       magenta    orange     purple  '''  # noqa
        self.fill = ['#FF3333', '#33FF33', '#3333FF', '#FFFF33', '#777777', '#33FFFF', '#FF33FF', '#FF9933', '#8833FF']  # noqa

        self.welcome_message = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ['S', 'E', 'L', 'E', 'C', 'T', 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ['Y', 'O', 'U', 'R', 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ['B', 'O', 'A', 'R', 'D', 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ['T', 'O', 0, 'B', 'E', 'G', 'I', 'N', 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        # order dependent  # todo: move to main
        self.initialize_title()
        self.initialize_play_board()
        self.initialize_control_board()
        self.initialize_board_selector_menu()
        self.initialize_num_selector_popup()
        self.bindings()

        self.update_entire_board(self.welcome_message, state_change=False)

        # self.update()
        # self.colors_button = tk.Label(self.container)
        # self.colors_button.config(text='C', font=(self.board_font, self.font_size),)
        # height = self.title_container.winfo_reqheight() / self.winfo_reqheight()
        # self.colors_button.place(relx=1, rely=height, anchor=tk.NE)


    def bindings(self):
        # self.bind("<Button-1>", self.event_handler)
        self.bind("<ButtonRelease-1>", self.event_handler)
        # self.bind("<Button-2>", self.event_handler)
        self.bind("<ButtonRelease-3>", self.event_handler)
        self.bind("<c>", lambda e: self.toggle_color())


        def button_enter(e):
            shade = 32
            rgb = e.widget['bg'][1:]
            rgb_hex = (rgb[:2], rgb[2:4], rgb[4:])
            to_ints = tuple(map(lambda x: int(f'{x:<02}', 16), rgb_hex))
            offset = tuple(map(lambda x: (x - shade) % 256, to_ints))
            # restore = tuple(map(lambda x: (x + shade) % 256, to_ints))
            cycled = '#' + ''.join(map(lambda x: f'{hex(x)[2:]:<02}', offset))
            e.widget['bg'] = cycled

        def button_leave(e):
            shade = 32
            rgb = e.widget['bg'][1:]
            rgb_hex = (rgb[:2], rgb[2:4], rgb[4:])
            to_ints = tuple(map(lambda x: int(f'{x:<02}', 16), rgb_hex))
            # offset = tuple(map(lambda x: (x - shade) % 256, to_ints))
            restore = tuple(map(lambda x: (x + shade) % 256, to_ints))
            cycled = '#' + ''.join(map(lambda x: f'{hex(x)[2:]:<02}', restore))
            e.widget['bg'] = cycled

        """ manually bind all buttons because my_boss chose dated framework """
        s_b_m_c = self.select_board_menu_container
        c_p_c = self.control_panel_container
        s_b_m_c_children = s_b_m_c.winfo_children()[0].winfo_children()
        """                ^ container              ^ backdrop              """
        c_p_c_children = c_p_c.winfo_children()[0].winfo_children()
        """              ^ container            ^ backdrop                  """
        all_children = s_b_m_c_children + c_p_c_children
        for button in all_children:
            button.bind("<Enter>", button_enter)
            button.bind("<Leave>", button_leave)

        # todo: debuggin' ma life away
        import utilities as u
        def debug_debug_info():
            print(f"{'has_lock ':.<30} {self.has_lock}")
            print(f"{'selected_cell ':.<30} {self.selected_cell}")
            print(f"{'board_state_change ':.<30} {self.board_state_change}")
            print()
        def invert_color(element):  # noqa
            if element is None: return  # noqa
            rgb = element.cget('bg')
            if rgb == 'SystemButtonFace': rgb = '#f0f0f0'  # noqa
            if rgb == 'white':  rgb = '#FFFFFF'  # noqa
            rgb = rgb[1:] if rgb[0] == '#' else rgb
            shade = 128
            rgb_hex = (rgb[:2], rgb[2:4], rgb[4:])
            to_ints = tuple(map(lambda x: int(x, 16), rgb_hex))
            offset = tuple(map(lambda x: (x + shade) % 256, to_ints))
            cycled = '#' + ''.join(map(lambda x: hex(x)[2:], offset))
            element.config(bg=cycled)
        key_map = {
            # note: unable to use shift binds
            '<Alt-h>': lambda e: print('text containing help commands'),
            '<Alt-d>': lambda e: debug_debug_info(),
            '<Alt-l>': lambda e: invert_color(self.has_lock),
            '<Alt-c>': lambda e: self.debugging_tools_change_obj_color(e, False),
            '<Alt-b>': lambda e: print(u.strip_print([[cell.value for cell in row] for row in self.board_gui_data])),  # noqa
        }
        for k, v in key_map.items():
            self.bind(k, v)

    def event_handler(self, e):
        """  """
        """ employs an application state pattern """
        """ motivation: organizational and clarity """
        empty_board = self.empty_board_button
        easy_board = self.easy_board_button
        hard_board = self.hard_board_button
        random_easy = self.random_easy_board_button
        random_hard = self.random_hard_board_button
        boards = [empty_board, easy_board, hard_board, random_easy, random_hard]


        def convert_board():
            """ convert to array of int arrays """
            return [[cell.value for cell in row] for row in self.board_gui_data]

        def board_input(event):
            if not self.board_loaded:
                return

            board = event.widget  # play board OR num selector
            x = event.x_root - board.winfo_rootx()  # todo: is this e.x?
            y = event.y_root - board.winfo_rooty()  # todo: is this e.y?
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
                    i, j = self.board_index_lookup.get(id_)
                    if self.board_gui_data[i][j].locked:
                        # ignore locked (loaded board) cells
                        reset_ui_state()
                    elif e.num == 3 and not self.selected_cell:
                        # delete cell entry on right click
                        self.limited_update([(i, j, 0)])
                        canvas_id = self.board_gui_data[i][j].canvas_id
                        self.play_board.itemconfigure(canvas_id, fill='#ffffff')
                    elif not self.selected_cell:
                        # record cell and spawn number selector popup
                        self.selected_cell = self.board_index_lookup.get(id_)
                        self.spawn_num_selector(event)
                        self.has_lock = self.play_board
                        # self.verify_button['state'] = tk.DISABLED
                        # self.solve_button['state'] = tk.DISABLED
                    else:
                        reset_ui_state()

                # if the num selector was selected
                elif board.gettags(id_)[0] == 'num':
                    val = self.num_selector_lookup.get(id_)
                    i, j = self.selected_cell
                    pb_obj_id = self.board_gui_data[i][j].canvas_id

                    self.limited_update([(i, j, val), ])
                    reset_ui_state()

                    color = self.fill[val - 1] if self.cell_colors else '#ffffff'
                    cb.itemconfigure(pb_obj_id, fill=color)
                    # self.fill_count = (self.fill_count + 1) % len(self.fill)

        # todo: refactor further ?; kept from old design
        # todo: refactor matrix import into main
        def board_selector(event):
            from testing.test_cases import TestMatrices

            board = TestMatrices().matrix_00()
            if event.widget == self.easy_board_button:
                board = TestMatrices().matrix_01()
            elif event.widget == self.hard_board_button:
                board = TestMatrices().matrix_11()  # hard
            elif event.widget == self.random_easy_board_button:
                print('generate easy board')
            elif event.widget == self.random_hard_board_button:
                print('generate hard board')

            self.update_entire_board(board)
            self.lock_and_shade_cells(board)


        def solve_board():
            from solver_engine import SolverEngine
            se = SolverEngine()

            board_data = convert_board()
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
            # self.select_button['state'] = tk.NORMAL

        # todo: keep validation result until board state changes
        # todo: probably refactor (eg board_state_change confusing)
        def click_solve():
            if self.solve_button['state'] == tk.DISABLED:
                return
            if self.solve_button.cget('text') == 'SOLVE':
                self.select_board_menu_container.place_forget()
                self.solve_button.config(text='ABORT?')
                self.verify_button['state'] = tk.DISABLED
                self.select_button['state'] = tk.DISABLED
                solve_board()
                self.select_button['state'] = tk.NORMAL
                self.verify_button['state'] = tk.NORMAL
                self.board_loaded = False
                verify()
                self.board_state_change = False
            else:  # solve_button.cget('text') == 'ABORT?'
                self.abort = True
                self.verify_button['state'] = tk.DISABLED

        def verify():
            from solver_engine import SolverEngine
            se = SolverEngine()

            if se.validate_board(convert_board()):
                self.title_label.config(
                    text='VALIDATED!',
                    width=len(self.title_text))
                # self.verify_button['state'] = tk.DISABLED
                self.title_label.config(bg='#53ec53')
                self.solve_button['state'] = tk.DISABLED
            else:
                self.title_label.config(
                    text='invalid :(',
                    width=len(self.title_text))
                self.title_label.config(bg='#ec5353')
            self.verify_button['state'] = tk.DISABLED

        def reset_ui_state():
            self.select_board_menu_container.place_forget()
            self.num_selector_popup.place_forget()
            self.selected_cell = None
            self.has_lock = None

        if e.num == 2:
            self.debugging_tools_change_obj_color(e)
            return

        # clears, on any input, valid/invalid results
        if self.title_label.cget('text') != self.title_text:
            self.title_label.config(text=self.title_text, bg='#ffffff')

        if e.widget in [self.play_board, self.num_selector_popup]:
            # todo: handling same types of things in different places
            # todo: handling same types of things in different places

            """ handles board user entry """
            # ~ self.select_board_menu_container.winfo_viewable():
            if self.has_lock in [None, self.play_board]:
                board_input(e)
            else:
                reset_ui_state()  # todo: review

        elif e.widget == self.select_button:
            """ spawns difficulty menu after clicking 'select' """
            if self.select_button['state'] == tk.DISABLED:
                return

            # does not have lock
            if self.has_lock != self.select_board_menu_container:
                # other has lock
                if self.has_lock is not None:
                    reset_ui_state()
                """ place() doesn't work without arguments ??? """
                """ even if place(*args) is called at creation """
                self.select_board_menu_container.place(
                    relx=.5, rely=.5, width=400, height=180, anchor=tk.CENTER)
                self.has_lock = self.select_board_menu_container
            # ~ self.select_board_menu_container.winfo_viewable():
            elif self.select_board_menu_container == self.has_lock:
                reset_ui_state()
        elif e.widget in boards:
            board_selector(e)
            self.solve_button['state'] = tk.NORMAL
            self.verify_button['state'] = tk.NORMAL
            self.board_loaded = True
            reset_ui_state()

        elif e.widget == self.solve_button:
            if self.has_lock:
                return
            click_solve()
        elif e.widget == self.verify_button:
            if not self.board_loaded or self.has_lock:
                return
            if self.verify_button['state'] == tk.NORMAL:
                verify()

        # todo: this was created as a sentinel for the title, but is misused in the click_solve() code...
        if self.board_state_change:
            """ restores title to original state on any user input """
            self.title_label.config(text=self.title_text, bg='#ffffff')
            self.board_state_change = False

            self.verify_button['state'] = tk.NORMAL

        self.update()

    def initialize_title(self):
        font_size = self.font_size

        self.title_container = tk.Canvas(self.container)
        self.title_container.config(borderwidth=0, highlightthickness=0)
        self.title_container.pack(before=self.play_board)  # todo: order of execution dependence

        self.title_label = tk.Label(
            self.title_container,
            text=self.title_text,
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
            width=width, height=height,
            bg='#ffffff', borderwidth=border_width, highlightthickness=0)
        self.num_selector_popup.place(relx=0, rely=0)
        self.num_selector_popup["state"] = tk.DISABLED
        self.num_selector_popup.place_forget()

        for i in range(3):
            for j in range(3):
                num = (i * 3) + (j + 1)
                color = self.fill[num - 1] if self.cell_colors else '#ffffff'
                # self.fill_count = (self.fill_count + 1) % len(self.fill)

                canvas_id = self.num_selector_popup.create_rectangle(
                    j * (width / 3) + border_width + rect_b_width,
                    i * (width / 3) + border_width + rect_b_width,
                    j * (width / 3) + cell_size + border_width / 3,
                    i * (width / 3) + cell_size + border_width / 3,
                    width=rect_b_width, fill=color,  # fill='cyan',
                    tags=('num', 'backdrop'),
                )
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
        def formatted_button(master, text, f_scale):
            # font_size = int(self.font_size * f_scale)
            # button = tk.Button(master)
            # button.config(text=text, anchor=tk.CENTER)
            # button.config(bg='#ffffff', relief='sunken', borderwidth=0)
            # button.config(font=(self.board_font, font_size))
            # return button

            font_size = int(self.font_size * f_scale)
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg='#ffffff', borderwidth=0)
            button.config(width=8)
            button.config(font=(self.board_font, font_size))
            return button

        # note: Canvas has useful options and functionality versus Frame
        self.control_panel_container = tk.Canvas(self.container)
        self.control_panel_container.config(
            width=self.play_board.winfo_reqwidth(),
            height=self.CELL_SIZE, bg='#ffffff', highlightthickness=0,)
        self.control_panel_container.pack(fill=tk.BOTH, side=tk.BOTTOM, ipady=10)

        # solve, verify, and select buttons
        c_p_c = self.control_panel_container  # buttons parent
        foo = tk.Frame(c_p_c, bg='#ffffff')
        foo.place(relx=.5, rely=.5, anchor=tk.CENTER)

        self.solve_button = formatted_button(foo, 'SOLVE', 1.2)
        self.solve_button.grid(row=0, column=0, rowspan=2)
        self.solve_button['state'] = tk.DISABLED

        self.verify_button = formatted_button(foo, 'VERIFY', 1.2)
        self.verify_button.grid(row=0, column=1, rowspan=2)
        self.verify_button['state'] = tk.DISABLED

        self.select_button = formatted_button(foo, 'SELECT', 1.2)
        self.select_button.grid(row=0, column=2, rowspan=2)

    def initialize_board_selector_menu(self):
        """ to add borders, these buttons differ from control board buttons """
        def formatted_button(master, text, f_scale):
            # """ border necessary due to tk limitations """
            # border = tk.Frame(master, highlightbackground='black', highlightthickness=2)
            # font_size = int(self.font_size * f_scale)
            # button = tk.Button(border)
            # button.config(text=text, anchor=tk.CENTER)
            # button.config(bg='#ffffff', relief='sunken', borderwidth=0)
            # button.config(font=(self.board_font, font_size))
            # button.config(height=1, width=7)  # width in chars
            # button.pack()
            # return border

            """  """
            """ labels necessary due to tk limitations """
            """ functionally most similar to buttons """
            font_size = int(self.font_size * f_scale)
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg='#ffffff', relief='sunken', borderwidth=0)
            button.config(highlightbackground='black', highlightthickness=2)
            button.config(font=(self.board_font, font_size))
            button.config(height=1, width=7)  # width in chars
            button.config(pady=8)
            return button

        # difficulty selector backdrop
        self.select_board_menu_container = (tk.Canvas(self.play_board))
        self.select_board_menu_container.config(
            highlightthickness=2, highlightbackground='black')
        # place cannot be used here; settings are forgotten

        # exclusively for button alignment  # todo: local?
        select_board_menu_backdrop = tk.Frame(self.select_board_menu_container)
        select_board_menu_backdrop.place(relx=.5, rely=.5, anchor=tk.CENTER)

        size = .8  # button font relative size
        sbmb = select_board_menu_backdrop

        self.empty_board_button = formatted_button(sbmb, "Empty", size)
        self.empty_board_button.grid(row=0, column=0, padx=2, pady=3)

        self.easy_board_button = formatted_button(sbmb, "Easy", size)
        self.easy_board_button.grid(row=0, column=1, padx=2, pady=3)

        self.hard_board_button = formatted_button(sbmb, "Hard", size)
        self.hard_board_button.grid(row=0, column=2, padx=2, pady=3)

        # self.random_board_button = formatted_button(sbmb, "Random", size)
        # self.random_board_button.grid(row=2, column=0)

        self.random_easy_board_button = formatted_button(sbmb, "Random Easy", size)
        self.random_easy_board_button.config(width=14, padx=6)
        self.random_easy_board_button.grid(row=1, column=0, columnspan=2, padx=2, pady=0)

        self.random_hard_board_button = formatted_button(sbmb, "Random Hard", size)
        self.random_hard_board_button.config(width=14, padx=6)
        self.random_hard_board_button.grid(row=2, column=1, columnspan=2, padx=2, pady=3)


    # todo: consider refactor ?
    def lock_and_shade_cells(self, shaded_cells):
        """ locks and colors cells dark """
        for i in range(len(self.board_gui_data)):
            for j in range(len(self.board_gui_data[0])):
                canvas_id = self.board_gui_data[i][j].canvas_id
                text_id = self.board_gui_data[i][j].text_id
                number = shaded_cells[i][j]
                fill = '#D4D4D4'  # is 'grey83'; previous was 'gray77'
                if number == 0:  # reset old value
                    fill = ''
                    number = ''
                    self.board_gui_data[i][j].locked = False
                else:
                    self.board_gui_data[i][j].locked = True

                self.play_board.itemconfigure(canvas_id, fill=fill)
                self.play_board.itemconfigure(text_id, text=number)
                self.play_board.lower(canvas_id)

    def toggle_color(self):
        self.cell_colors = not self.cell_colors

        # recolor number selector popup
        count = 0
        for id_, val in self.num_selector_lookup.items():
            tags = self.num_selector_popup.itemcget(id_, "tags")
            if 'backdrop' not in tags:
                continue
            fill = '#ffffff'
            if self.cell_colors:
                fill = self.fill[count]
                count += 1
            self.num_selector_popup.itemconfigure(id_, fill=fill)


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
        self.board_state_change = True

    def update_entire_board(self, new_board, state_change=True) -> None:
        for i in range(len(new_board)):
            for j in range(len(new_board[0])):  # assumes rectangular
                self.board_gui_data[i][j].value = new_board[i][j]

                text_id = self.board_gui_data[i][j].text_id
                number = self.board_gui_data[i][j].value
                if number == 0:
                    number = ''

                self.play_board.itemconfig(text_id, text=number)
        if state_change:
            self.board_state_change = True

    def spawn_num_selector(self, e):
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

        self.num_selector_popup.place(relx=x_rel, rely=y_rel, anchor=anchor)


    def debugging_tools_change_obj_color(self, e, invert_color=False):
        # bug: does not correctly change color of main board's numbers
        board = e.widget
        print('board / e.widget', board)

        # board = e.widget  # play board OR num selector

        # top left corner of app
        print('e.widget winfo root xy', e.widget.winfo_rootx(), e.widget.winfo_rooty())

        # relative pixel screen position
        print('event xy_root', e.x_root, e.y_root)

        # app window x y position
        x = e.x_root - e.widget.winfo_rootx()
        y = e.y_root - e.widget.winfo_rooty()
        print('x y', x, y)
        # this takes absolute pixel screen position
        widget = self.winfo_containing(e.x_root, e.y_root)
        print("widget under mouse:", widget)
        print('.........................')

        # constant, actual dimensions of app
        # req_w = e.widget.winfo_reqwidth()
        # req_h = e.widget.winfo_reqheight()
        # print('req w h', req_w, req_h)
        # print('.........................')

        # print('winfo xy', e.widget.winfo_x(), e.widget.winfo_y())
        # print('.........................')


        obj_ids = []
        if hasattr(widget, 'find_closest'):
            """
            unclear why, but the board seems to not recognize being offset,
            and appears to expect absolute screen coordinates that are offset
            by its position relative to the window...
            or, maybe it's the function being used...
            """
            if widget == self.play_board:
                x_b = x - self.play_board.winfo_x()
                y_b = y - self.play_board.winfo_y()
                obj_ids = self.play_board.find_closest(x_b, y_b)
        obj_tags = ()
        if hasattr(widget, 'gettags'):
            obj_tags = widget.gettags("current")

        print('obj_tag', obj_tags)
        print('items', obj_ids)

        id_ = None
        if obj_ids:
            id_ = obj_ids[0]
        tag = None
        if obj_tags:
            tag = obj_tags[0]

        color = self.fill[self.fill_count]

        if type(widget) is type(tk.Frame()):
            print('Frame')
            widget.configure(id_, bg=color)
        if type(widget) is type(tk.Canvas()):
            print('Canvas')
            if tag == 'cell':
                widget.itemconfigure(id_,  fill=color)
            else:
                widget.config(bg=color)
        if type(widget) is type(tk.Label()):
            print('Label')
            widget.configure(id_, bg=color)

        self.fill_count = (self.fill_count + 1) % len(self.fill)
        print()

if __name__ == '__main__':
    benchmarking = False

    # root_frame = tk()
    # sudoku_gui = CanvasGUI(root_frame, CELL_SIZE)  # .pack(side="top", fill="both", expand=True)
    # root_frame.mainloop()
    app = CanvasGUI()
    app.mainloop()

'''

# TODO create subclasses http://stackoverflow.com/questions/17056211/python-tkinter-option-menu

# todo change 50 board values ?

# todo broke scaling size with style
# todo font changes with cell size, but not with Sudoku board size

# todo taskbar icon not displaying

'''
