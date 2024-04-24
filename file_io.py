import logging
import os
import random as r


class FileIO:
    """ non-data line prefix '_' """
    DATA_FILE_NAME = '17puz49158.txt'
    SAVE_FILE_NAME = 'sudoku_save'
    BOARD_DATA_SENTINEL_VALUE = 'board_data:'
    CLUE_17_SENTINEL_VALUE = '_17_clue_set: '

    def __init__(self, local_save_path='./', save_file_name=SAVE_FILE_NAME):
        self.save_path = local_save_path
        self.save_file_name = save_file_name + '.txt'
        if local_save_path == './':
            self.save_path = os.path.abspath(self.save_file_name)
        if not os.path.isfile(self.save_path):
            self.create_file()

        """ Pyinstaller unpacks .exe into TEMP directory _MEIPASS """
        rel_path = os.path.join(os.path.dirname(__file__), self.DATA_FILE_NAME)
        self.data_path_17_hints = os.path.abspath(rel_path)

        # logger = logging.getLogger(__name__)
        logging.getLogger()
        logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG)
        # logger.debug .info .warning .error

    def create_file(self):
        try:
            f = open(self.save_path, 'x')
            f.write(self.CLUE_17_SENTINEL_VALUE + '\n\n')
            f.close()
            logging.info(f'file creation successful:\n\t{self.save_path}')
        except (IOError,):
            logging.warning(f'file creation failure:\n\t{self.save_path}')

    def read_and_load_2d_board_from_17_hints_data_file(self):
        """ returns a random board from 17 clue data file """
        board_save_data = str()
        random_int = r.randint(0, 49158 - 1)
        try:
            with open(self.data_path_17_hints, 'r') as f:
                for i, line in enumerate(f):
                    if i == random_int:
                        board_save_data = line.rstrip("\n\r")
                        break
            logging.info(f'17 clue data read successful:\n\t{board_save_data}')
        except (IOError,) as e:
            logging.exception('save read failure', stack_info=True)
            return False
        return self.convert_str_lines_to_2d_board(board_save_data)

    @staticmethod
    # todo: merge with saved board loader, or into parent function
    def convert_str_lines_to_2d_board(str_data: str) -> list[list[int]]:
        """ converts from string format to array format """
        reconstructed = list()
        j = 0
        row = list()
        for char in str_data:
            if not char.isdigit():
                char = 0
            char = int(char)
            row.append(char)
            j += 1
            if not j < 9:
                reconstructed.append(row)
                row = list()
                j = 0
        return reconstructed

    ###########################################################################
    # save/load fns

    def write_3d_board_to_save_file(self, board_data):
        try:
            with open(self.save_path, 'a') as f:
                encoded = self.BOARD_DATA_SENTINEL_VALUE + '\n'
                encoded = encoded + self.convert_3d_board_to_str(board_data)
                for line in encoded.split('\n'):
                    line = line + '\n'
                    f.write(line)
                f.write('\n')
                f.close()
            logging.info(f'write successful:\n\t{self.save_path}\n\t{encoded}')
        except (IOError,) as e:
            logging.exception('write failure', stack_info=True)
            return False
        return True

    def read_all_saved_3d_boards_from_save_file(self):
        """ reads str format and returns converted 3d note format """
        b_d_s_v = self.BOARD_DATA_SENTINEL_VALUE
        all_boards: list[list[str]] = list()
        try:
            with open(self.save_path, 'r') as f:
                lines = f.readlines()
                board_data = list()
                next_board = False
                for line in lines:
                    stripped_suffix = line.rstrip("\n\r")
                    if stripped_suffix == '':
                        continue
                    elif b_d_s_v in stripped_suffix:
                        next_board = True
                    elif next_board:
                        board_data.append(stripped_suffix)

                    if len(board_data) > 10:
                        all_boards.append(board_data)
                        board_data = list()
                        next_board = False

            if len(all_boards) < 1:
                return False
            logging.info('save read successful')
        except (IOError,) as e:
            logging.exception('save read failure', stack_info=True)
            return False
        return all_boards

    @staticmethod
    def convert_3d_board_to_str(board: list[list[list[int]]]) -> str:
        """
            converts from 3d CellData matrix format to string format
            board_str
            note_str_1
            note_str_2
            ...
            note_str_9
            locked_state
        """
        n, m = len(board), len(board[0])

        locked_state = list()
        for i in range(n):
            for j in range(m):
                char = str(board[i][j][-1])
                locked_state.append(char)
        locked_state = ''.join(locked_state)

        board_str = list()
        for i in range(n):
            for j in range(m):
                char = str(board[i][j][0])
                if char == '0':
                    char = '.'
                board_str.append(char)
        board_str = ''.join(board_str)

        # zero-indexed
        notes_strs = [list() for _ in range(1, 10)]
        for i in range(n):
            for j in range(m):
                notes = board[i][j][:]  # todo
                for k in range(1, 10):
                    note = str(notes[k])
                    if note == '0':
                        note = '.'
                    notes_strs[k - 1].append(note)

        notes_strs = '\n'.join([''.join(note_str) for note_str in notes_strs])

        return board_str + '\n' + notes_strs + '\n' + locked_state

    @staticmethod
    def convert_str_lines_to_3d_saved_board_state(str_line_data: list[str]) \
            -> tuple[list[list[list[int]]], list[list[int]]]:
        """
            returns list of tuples:
                3d board of form: (i, j) <- [val, note_1, note_2 ... note_9]
                2d board of form: (i, j) <- lock state
        """
        board_val_data = str_line_data[0]
        note_val_data = str_line_data[1:-1]
        locked_state_data = str_line_data[-1]
        reconstructed_board_with_notes = list()
        locked_state_board = list()

        # board value reconstruction
        i = j = 0
        row = list()
        for char in board_val_data:
            if char == '.':
                char = 0
            row.append([int(char)])
            j += 1
            if j > 8:
                j = 0
                i += 1
                reconstructed_board_with_notes.append(row)
                row = list()

        # note reconstruction
        i = j = 0
        for x in range(len(note_val_data[0])):
            cell_notes = list()
            for k in range(9):
                char = note_val_data[k][x]
                if char == '.':
                    char = 0
                char = int(char)
                cell_notes.append(char)
            val = reconstructed_board_with_notes[i][j]
            reconstructed_board_with_notes[i][j] = val + cell_notes
            j += 1
            if j > 8:
                j = 0
                i += 1

        # locked state reconstruction
        i = j = 0
        row = list()
        for char in locked_state_data:
            row.append(int(char))
            j += 1
            if j > 8:
                j = 0
                i += 1
                locked_state_board.append(row)
                row = list()

        return reconstructed_board_with_notes, locked_state_board

    ###########################################################################

    @staticmethod
    # used for logging generated boards
    def board_without_notes_to_str(board: list[list[int]]) -> str:
        """ converts from array format to string format """
        n, m = len(board), len(board[0])
        to_str = list()
        for i in range(n):
            for j in range(m):
                char = str(board[i][j])
                if char == '0':
                    char = '.'
                to_str.append(char)
        to_str = ''.join(to_str)
        return to_str


if __name__ == '__main__':
    import utilities as u
    test_data = [
        [1, 0, 0, 2, 0, 0, 3, 0, 0],
        [2, 0, 0, 3, 0, 0, 4, 0, 0],
        [3, 0, 0, 4, 0, 0, 5, 0, 0],
        [4, 0, 0, 5, 0, 0, 6, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 0, 0, 4, 0, 0, 5],
        [0, 0, 4, 0, 0, 5, 0, 0, 6],
        [0, 0, 5, 0, 0, 6, 0, 0, 7],
        [0, 0, 6, 0, 0, 7, 0, 0, 8],
    ]
    io = FileIO()
    # io.write_to_save_file(test_data)
    # data = io.read_from_save_file()
    data = io.read_and_load_2d_board_from_17_hints_data_file()
    io.write_3d_board_to_save_file(data)
    test_convert = io.read_and_load_all_boards_from_save_file()
    # print(io._board_to_str(test_convert))
    # print(u.strip_for_print(test_convert))
