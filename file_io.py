import logging
import os
import random as r


class FileIO:
    """ non-data line prefix '_' """
    DATA_FILE_NAME = '17puz49158.txt'
    SAVE_FILE_NAME = 'sudoku_save_data'
    BOARD_DATA_SENTINEL_VALUE = 'board_data_'  # eg board_data_slot_*
    CLUE_17_SENTINEL_NAME = '_17_clue_index:'
    CLUE_17_SENTINEL_VALUE = '49157'  # 49158 - 1

    """    
    save file data format:
        _17_clue_index: inclusive upper bound of implicit data structure
        newline
        board_data_slot_1
        board data (empty board data if none)
        newline
        board_data_slot_2
        board data (empty board data if none)
        newline
        board_data_slot_3
        board data (empty board data if none)
        newline
    """

    def __init__(self, local_save_path='./', save_file_name=SAVE_FILE_NAME):
        self.save_path = local_save_path
        self.save_file_name = save_file_name + '.txt'
        if local_save_path == './':
            self.save_path = os.path.abspath(self.save_file_name)
        if not os.path.isfile(self.save_path):
            self.create_file()

        """ Pyinstaller unpacks .exe into TEMP directory _MEIPASS """
        rel_path = os.path.join(os.path.dirname(__file__), self.DATA_FILE_NAME)
        self.data_path_17_clue = os.path.abspath(rel_path)

        # logger = logging.getLogger(__name__)
        logging.getLogger()
        logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG)
        # logger.debug .info .warning .error

    def create_file(self):
        """ to simplify other operations, a valid file format is initialized """
        c_17_name = self.CLUE_17_SENTINEL_NAME
        c_17_value = self.CLUE_17_SENTINEL_VALUE
        try:
            f = open(self.save_path, 'x')
            f.write(f'{c_17_name} {c_17_value}\n\n')
            for i in range(1, 4):
                f.write(self._empty_save_slot_string(i))
            f.close()
            logging.info(f'file creation successful:\n\t{self.save_path}')
        except (IOError,):
            logging.warning(f'file creation failure:\n\t{self.save_path}')

    def _empty_save_slot_string(self, slot_number):
        b_d_s_v = self.BOARD_DATA_SENTINEL_VALUE
        empty_board_state_string = [f'{b_d_s_v}slot_{slot_number}:\n']
        for _ in range(10):
            line = ''.join(['.' for _ in range(81)] + ['\n'])
            empty_board_state_string.append(line)
        empty_board_state_string.append(''.join(['0' for _ in range(81)] + ['\n']))
        empty_board_state_string = ''.join(empty_board_state_string + ['\n'])
        return empty_board_state_string

    def _slot_sentinel_line(self, slot_number):
        """
            text file slot number is one-indexed
            reason for using text file is relative accessibility
        """
        return f'{self.BOARD_DATA_SENTINEL_VALUE}slot_{slot_number + 1}:\n'

    ###########################################################################
    # 17 clue fns

    def read_17_clue_upper_bound(self):
        """ inclusive upper boundary """
        try:
            with open(self.save_path, 'r') as f:
                line = f.readline()
                index = line.split()[-1]
            logging.info(f'17 clue index read successful:\n\t{index}')
        except (IOError,) as e:
            logging.exception('17 clue index read failure', stack_info=True)
            return False
        return int(index)

    def write_17_clue_upper_bound(self, new_index):
        if new_index == -1:
            new_index = 49157
        try:
            with open(self.save_path, 'r+') as f:
                f.seek(len(self.CLUE_17_SENTINEL_NAME) + 1)
                f.write(f'{new_index:05}')
            logging.info(f'17 clue index write successful:\n\t{new_index}')
        except (IOError,) as e:
            logging.exception('17 clue index write failure', stack_info=True)
            return False
        return True

    def load_2d_board_from_17_clue_data_file(self):
        """
            returns a random board from 17 clue data file
            implements ~ fisher-yates
            note: not easily done in place, if possible
        """
        random_board = str()
        upper_index_inclusive = self.read_17_clue_upper_bound()
        random_int = r.randint(0, upper_index_inclusive)
        try:
            with open(self.data_path_17_clue, 'r') as f:
                lines = f.readlines()
            lines[random_int], lines[upper_index_inclusive] = lines[upper_index_inclusive], lines[random_int]
            with open(self.data_path_17_clue, 'w') as f:
                f.writelines(lines)
            logging.info(f'17 clue data read/write successful:\n\t{random_board}')
        except (IOError,) as e:
            logging.exception('17 clue data read/write failure', stack_info=True)
            return False
        random_board = lines[upper_index_inclusive].rstrip("\n\r")
        self.write_17_clue_upper_bound(upper_index_inclusive - 1)
        return self.convert_str_lines_to_2d_board(random_board)

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


    def _reset_17_clue_data_file(self):
        c_17_name = self.CLUE_17_SENTINEL_NAME
        c_17_value = self.CLUE_17_SENTINEL_VALUE
        try:
            with open(self.data_path_17_clue, 'r') as f:
                data_17_clue = f.readlines()
            data_17_clue.sort()
            with open(self.data_path_17_clue, 'w') as f:
                f.writelines(data_17_clue)

            with open(self.save_path, 'r') as f:
                data_save = f.readlines()
            data_save[0] = f'{c_17_name} {c_17_value}\n'
            with open(self.save_path, 'w') as f:
                f.writelines(data_save)

            logging.info(f'17 clue reset successful:\n\t{self.save_path}')
        except (IOError,):
            logging.warning(f'17 clue reset failure:\n\t{self.save_path}')

    def _validate_17_clue_data_file(self):
        with open(self.data_path_17_clue, 'r') as f:
            data_lines = f.readlines()
        data_lines.sort()
        path = self.data_path_17_clue[:-3] + 'bak'
        with open(path, 'r') as f:
            reference_lines = f.readlines()

        if len(data_lines) != len(reference_lines):
            return False

        if data_lines != reference_lines:
            for i in range(len(data_lines)):
                if data_lines[i] != reference_lines[i]:
                    print(f'line {i}\n', data_lines[i], reference_lines[i])
            return False
        else:
            return True

    ###########################################################################
    # save/load fns

    def update_save_file(self, board_data, slot_number):
        """ rewrite entire file with new board """
        try:
            with open(self.save_path, 'r+') as f:
                all_lines = f.read()

                all_lines = all_lines.split('\n\n')
                all_lines.pop() if len(all_lines) > 4 else ...  # carriage compensation

                encoded = self._slot_sentinel_line(slot_number)
                encoded += self.convert_3d_board_to_str(board_data)
                start_i = 0
                for segment in all_lines:
                    if self.BOARD_DATA_SENTINEL_VALUE in segment:
                        break
                    start_i += 1
                all_lines[start_i + slot_number] = encoded

                f.seek(0)
                for line in all_lines:
                    f.write(line)
                    f.write('\n\n')
            logging.info(f'write successful:\n\t{self.save_path}\n\t{encoded}')
        except (IOError,) as e:
            logging.exception('write failure', stack_info=True)
            return False
        return True

    # todo: deprecated
    def write_3d_board_to_save_file(self, board_data, slot_number):
        try:
            with open(self.save_path, 'a') as f:
                encoded = self._slot_sentinel_line(slot_number)
                encoded += self.convert_3d_board_to_str(board_data)
                for line in encoded.split('\n'):
                    line = line + '\n'
                    f.write(line)
                f.write('\n')
            logging.info(f'write successful:\n\t{self.save_path}\n\t{encoded}')
        except (IOError,) as e:
            logging.exception('write failure', stack_info=True)
            return False
        return True

    def read_all_saved_3d_boards_from_save_file(self):
        """ reads str format and returns converted 3d note format """
        try:
            with open(self.save_path, 'r') as f:
                all_lines = f.read()
            all_lines = all_lines.split('\n\n')
            all_boards = list()
            for segment in all_lines:
                if self.BOARD_DATA_SENTINEL_VALUE in segment:
                    all_boards.append(segment)
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

    def convert_str_lines_to_3d_saved_board_state(self, str_line_data: str) \
            -> tuple[list[list[list[int]]], list[list[int]]]:
        """
            handles data with sentinel prefix

            returns list of tuples:
                3d board of form: (i, j) <- [val, note_1, note_2 ... note_9]
                2d board of form: (i, j) <- lock state
        """
        str_line_data_as_list = str_line_data.split('\n')
        if self.BOARD_DATA_SENTINEL_VALUE in str_line_data_as_list[0]:
            str_line_data_as_list.pop(0)
        board_val_data = str_line_data_as_list[0]
        note_val_data = str_line_data_as_list[1:-1]
        locked_state_data = str_line_data_as_list[-1]
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
    # test_i = io.read_17_clue_upper_bound()
    # print(test_i)
    # test_board = io.read_and_load_2d_board_from_17_clue_data_file()
    # print(test_board)

    # for i in range(10):
    #     test_board = io.load_2d_board_from_17_clue_data_file()

    io._reset_17_clue_data_file()
    print(io._validate_17_clue_data_file())


