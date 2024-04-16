import logging
from class_cell_data import CellData
import tkinter as tk
from pixel_gui import PixelGUI
import matrix_library
from solver_engine import SolverEngine
from random_generator import RandomBoard
from file_io import FileIO


# print('''
# todo:
#     solver was mostly to look cool, but is a bit slow on fixed 17 boards
#     consider precomputing valid moves (would preserve coolness of current solution)
#     ...
#     ! address 40 clue min edge case
#     consider adding valid transformations (for previously selected boards?)
#     ...
#     implement previously randomly selected record (currently in logs)
#     some sort of save system... scores, etc. ?
#     ...
#     optimize random generation; probably require redesign using dancing links
#     ...
#     asyncio/multiprocessing/multithreading for board generation?
#     spawn multiple threads for multiple boards? worse min, better worst case
#     ...
#     consider picking random cells and filling them
#     ...
#     review and resolve existing todos
#     matrix creator via input? eg 123456789<enter>2345...
#     ...
#     optimization fun (temporal constraints tho :( ):
#         to (more) optimally reduce density:
#         transform matrix into undirected graph
#         give each node
#             decrement method
#                 decrement count of adjacent nodes (including diagonal?)
#             references to diagonal neighbors (dijkstra's update analogue)
#         heapify single pass array of nodes (binary heap implementation)
#         using this priority queue, pop, decrement (need update?), validate
#
# todo (old):
#     taskbar icon not displaying
#     consider subclasses
#     http://stackoverflow.com/questions/17056211/python-tkinter-option-menu
#
# build commands:
#     pyinstaller --onefile --noconsole --name=sudoku --add-data="17puz49158.txt;." --icon='.\sudoku.ico' main.py
#     pyinstaller --onefile --name='sudoku_console' --add-data="17puz49158.txt;." --icon='.\sudoku.ico' main.py
#
# ''')


class SudokuApp:
    board_width = 9
    board_height = 9

    easy_clue_size = 34
    medium_clue_size = 28

    # # logger = logging.getLogger(__name__)
    # logging.basicConfig(filename='main_log.log', encoding='utf-8', level=logging.DEBUG)
    # logging.getLogger()

    def __init__(self):
        logging.getLogger()
        logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG)

        self.gui = PixelGUI(self.easy_clue_size, self.medium_clue_size)
        self.se = SolverEngine()
        self.rg = RandomBoard(self.board_width, self.board_height)
        self.io = FileIO()

        # order dependent
        self.gui.initialize_title()
        self.gui.initialize_play_board()
        self.gui.initialize_control_board()
        self.gui.initialize_board_selector_menu()
        self.gui.initialize_num_selector_popup()
        self.bindings()
        self.gui.update_entire_board(self.gui.welcome_message, state_change=False)
        # self.gui.initialize_notes_panel()

    def bindings(self):
        # todo: hold and drag Tkinter bug; have to code workaround or ignore
        # self.gui.bind("<Button-1>", self.event_handler)
        self.gui.bind("<ButtonRelease-1>", self.event_handler)
        # self.gui.bind("<Button-2>", self.event_handler)
        # self.gui.bind("<Button-3>", self.event_handler)
        self.gui.bind("<ButtonRelease-3>", self.event_handler)
        self.gui.bind("<c>", lambda e: self.gui.toggle_color())

        # todo: consolidate into shder fn
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
        s_b_m_c = self.gui.select_board_menu_container
        c_p_c = self.gui.control_panel_container
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
            print(f"{'has_lock ':.<30} {self.gui.has_lock}")
            print(f"{'selected_cell ':.<30} {self.gui.selected_cell}")
            print(f"{'board_state_change ':.<30} {self.gui.board_state_change}")
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
            '<Alt-l>': lambda e: invert_color(self.gui.has_lock),
            '<Alt-c>': lambda e: self.debugging_tools_change_obj_color(e, False),
            '<Alt-b>': lambda e: print(u.strip_for_print([[cell.value for cell in row] for row in self.gui.board_gui_data])),  # noqa
        }
        for k, v in key_map.items():
            self.gui.bind(k, v)


    def event_handler(self, e):
        """  """
        """ employs an application state pattern """
        """ motivation: organizational and clarity """
        empty_board = self.gui.empty_board_button
        easy_board = self.gui.easy_board_button
        hard_board = self.gui.hard_board_button
        random_easy = self.gui.random_easy_board_button
        random_medium = self.gui.random_medium_board_button
        random_17 = self.gui.random_pick_17_board_button
        boards = [empty_board, easy_board, hard_board, random_easy, random_medium, random_17]


        def convert_board():
            """ convert to array of int arrays """
            return [[cell.value for cell in row] for row in self.gui.board_gui_data]

        def board_input(event):
            if not self.gui.board_loaded:
                return

            board = event.widget  # play board OR num selector
            x = event.x_root - board.winfo_rootx()  # todo: is this e.x?
            y = event.y_root - board.winfo_rooty()  # todo: is this e.y?
            cb = self.gui.play_board
            cbw = cb.winfo_reqwidth()
            cbh = cb.winfo_reqwidth()
            offset = self.gui.offset / (self.gui.BOARD_SIZE - 1)  # canvas lines/cells offset

            # if the mouse event occurred within the event's board
            if (cbw - offset) > x > offset and (cbh - offset) > y > offset:
                obj_ids = board.find_closest(x, y)
                id_ = obj_ids[0]

                # if board cell was selected
                if board.gettags(id_)[0] == 'cell':
                    i, j = self.gui.board_index_lookup.get(id_)
                    if self.gui.board_gui_data[i][j].locked:
                        # ignore locked (loaded board) cells
                        reset_ui_state()
                    elif e.num == 3 and not self.gui.selected_cell:
                        # delete cell entry on right click
                        self.gui.limited_update([(i, j, 0)])
                        canvas_id = self.gui.board_gui_data[i][j].canvas_id
                        self.gui.play_board.itemconfigure(canvas_id, fill='#ffffff')
                    elif not self.gui.selected_cell:
                        # record cell and spawn number selector popup
                        self.gui.selected_cell = self.gui.board_index_lookup.get(id_)
                        self.gui.spawn_num_selector(event)
                        self.gui.has_lock = self.gui.play_board
                        # self.gui.verify_button['state'] = tk.DISABLED
                        # self.gui.solve_button['state'] = tk.DISABLED
                    else:
                        reset_ui_state()

                # if the num selector was selected
                elif board.gettags(id_)[0] == 'num':
                    val = self.gui.num_selector_lookup.get(id_)
                    i, j = self.gui.selected_cell
                    pb_obj_id = self.gui.board_gui_data[i][j].canvas_id

                    self.gui.limited_update([(i, j, val), ])
                    reset_ui_state()

                    color = self.gui.fill[val - 1] if self.gui.cell_colors else '#ffffff'
                    cb.itemconfigure(pb_obj_id, fill=color)
                    # self.gui.fill_count = (self.gui.fill_count + 1) % len(self.gui.fill)

        # todo: refactor further ?; kept from old design
        # todo: refactor matrix import into main
        def board_selector(event):
            from testing.test_cases import TestMatrices

            board = TestMatrices().matrix_00()
            if event.widget == self.gui.easy_board_button:
                board = TestMatrices().matrix_01()
            elif event.widget == self.gui.hard_board_button:
                board = TestMatrices().matrix_11()  # hard
            elif event.widget == self.gui.random_easy_board_button:
                board = self.rg.generate_board(self.easy_clue_size, sec=3)
                str_b = self.io._board_to_str(board)
                logging.info(f'{self.medium_clue_size} clue generated:\n\t{str_b}')
            elif event.widget == self.gui.random_medium_board_button:
                board = self.rg.generate_board(self.medium_clue_size, sec=3)
                str_b = self.io._board_to_str(board)
                logging.info(f'{self.medium_clue_size} clue generated:\n\t{str_b}')
            elif event.widget == self.gui.random_pick_17_board_button:
                # board = matrix_library.steering_wheel_classic
                board = self.io.read_and_load_board_from_17_hints_data_file()

            self.gui.update_entire_board(board)
            self.gui.lock_and_shade_cells(board)

        def solve_board():
            board_data = convert_board()
            generator_solver = self.se.solve_board(board_data)

            for next_limited_update in generator_solver:
                if self.gui.abort:
                    # generator_solver.send('stop')
                    self.gui.abort = False
                    break

                if not next_limited_update:
                    break
                self.gui.limited_update(next_limited_update)
                self.gui.update()

            self.gui.solve_button.config(text='SOLVE')
            self.gui.solve_button['state'] = tk.DISABLED
            # self.gui.select_button['state'] = tk.NORMAL

        # todo: keep validation result until board state changes
        # todo: probably refactor (eg board_state_change confusing)
        def click_solve():
            if self.gui.solve_button['state'] == tk.DISABLED:
                return
            if self.gui.solve_button.cget('text') == 'SOLVE':
                self.gui.select_board_menu_container.place_forget()
                self.gui.solve_button.config(text='ABORT?')
                self.gui.verify_button['state'] = tk.DISABLED
                self.gui.select_button['state'] = tk.DISABLED
                solve_board()
                self.gui.select_button['state'] = tk.NORMAL
                self.gui.verify_button['state'] = tk.NORMAL
                self.gui.board_loaded = False
                verify()
                self.gui.board_state_change = False
            else:  # solve_button.cget('text') == 'ABORT?'
                self.gui.abort = True
                self.gui.verify_button['state'] = tk.DISABLED

        def verify():

            from solver_engine import SolverEngine  # todo:
            se = SolverEngine()  # todo:

            if se.validate_board(convert_board()):
                self.gui.title_label.config(
                    text='VALIDATED!',
                    width=len(self.gui.title_text))
                # self.gui.verify_button['state'] = tk.DISABLED
                self.gui.title_label.config(bg='#53ec53')
                self.gui.solve_button['state'] = tk.DISABLED
            else:
                self.gui.title_label.config(
                    text='invalid :(',
                    width=len(self.gui.title_text))
                self.gui.title_label.config(bg='#ec5353')
            self.gui.verify_button['state'] = tk.DISABLED

        def reset_ui_state():
            self.gui.select_board_menu_container.place_forget()
            self.gui.num_selector_popup.place_forget()
            self.gui.selected_cell = None
            self.gui.has_lock = None

        if e.num == 2:
            self.debugging_tools_change_obj_color(e)
            return

        # clears, on any input, valid/invalid results
        if self.gui.title_label.cget('text') != self.gui.title_text:
            self.gui.title_label.config(text=self.gui.title_text, bg='#ffffff')

        if e.widget in [self.gui.play_board, self.gui.num_selector_popup]:
            # todo: handling same types of things in different places
            # todo: handling same types of things in different places

            """ handles board user entry """
            # ~ self.gui.select_board_menu_container.winfo_viewable():
            if self.gui.has_lock in [None, self.gui.play_board]:
                board_input(e)
            else:
                reset_ui_state()  # todo: review

        elif e.widget == self.gui.select_button:
            """ spawns difficulty menu after clicking 'select' """
            if self.gui.select_button['state'] == tk.DISABLED:
                return

            # does not have lock
            if self.gui.has_lock != self.gui.select_board_menu_container:
                # other has lock
                if self.gui.has_lock is not None:
                    reset_ui_state()
                """ place() doesn't work without arguments ??? """
                """ even if place(*args) is called at creation """
                p_rows = 4
                self.gui.select_board_menu_container.place(
                    relx=.5, rely=.5, width=400, height=60*p_rows, anchor=tk.CENTER)
                self.gui.has_lock = self.gui.select_board_menu_container
            # ~ self.gui.select_board_menu_container.winfo_viewable():
            elif self.gui.select_board_menu_container == self.gui.has_lock:
                reset_ui_state()
        elif e.widget in boards:
            board_selector(e)
            self.gui.solve_button['state'] = tk.NORMAL
            self.gui.verify_button['state'] = tk.NORMAL
            self.gui.board_loaded = True
            reset_ui_state()

        elif e.widget == self.gui.solve_button:
            if self.gui.has_lock:
                return
            click_solve()
        elif e.widget == self.gui.verify_button:
            if not self.gui.board_loaded or self.gui.has_lock:
                return
            if self.gui.verify_button['state'] == tk.NORMAL:
                verify()

        # todo: this was created as a sentinel for the title, but is misused in the click_solve() code...
        if self.gui.board_state_change:
            """ restores title to original state on any user input """
            self.gui.title_label.config(text=self.gui.title_text, bg='#ffffff')
            self.gui.board_state_change = False

            self.gui.verify_button['state'] = tk.NORMAL

        self.gui.update()


    def run(self):
        self.gui.mainloop()


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
        widget = self.gui.winfo_containing(e.x_root, e.y_root)
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
            if widget == self.gui.play_board:
                x_b = x - self.gui.play_board.winfo_x()
                y_b = y - self.gui.play_board.winfo_y()
                obj_ids = self.gui.play_board.find_closest(x_b, y_b)
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

        color = self.gui.fill[self.gui.fill_count]

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

        self.gui.fill_count = (self.gui.fill_count + 1) % len(self.gui.fill)
        print()


if __name__ == '__main__':
    BOARD_SIZE = 9
    CELL_SIZE = 50  # cell size: minimum > 25... probably

    app = SudokuApp()
    app.run()
