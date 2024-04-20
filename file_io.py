import logging
import os
import random as r


class FileIO:
    """ non-data line prefix '_' """
    DATA_FILE_NAME = '17puz49158.txt'

    def __init__(self, local_save_path='./', save_file_name='sudoku_save'):
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
            # f.write('_17_hint_set: \n')  # todo: fully implement
            f.close()
            logging.info(f'file creation successful:\n\t{self.save_path}')
        except (Exception,):
            logging.warning(f'file creation failure:\n\t{self.save_path}')

    def write_board_to_save_file(self, board_data):
        try:
            with open(self.save_path, 'a') as f:
                encoded = self.convert_to_formatted_str(board_data)
                line = encoded + '\n'
                f.write(line)
                f.close()
                logging.info(f'write successful:\n\t{self.save_path}\n\t{encoded}')
        except (Exception,) as e:
            logging.exception('write failure', stack_info=True)
            return False
        return True

    def read_and_load_all_boards_from_save_file(self):
        """ returns a list of boards """
        all_data = list()
        try:
            with open(self.save_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line and line[0] == '_':
                        continue
                    stripped_suffix = line.rstrip("\n\r")
                    decoded = self.convert_from_formatted_str(stripped_suffix)
                    all_data.append(decoded)
                logging.info('save read successful')
        except (Exception,) as e:
            logging.exception('save read failure', stack_info=True)
            return False
        return all_data

    def read_and_load_board_from_17_hints_data_file(self):
        """ returns a list of boards """
        board_save_data = str()
        random_int = r.randint(1, 49158 + 1)
        try:
            with open(self.data_path_17_hints, 'r') as f:
                for i, line in enumerate(f):
                    if i == random_int:
                        board_save_data = line.rstrip("\n\r")
                        break
            logging.info(f'17 clue data read successful:\n\t{board_save_data}')
        except (Exception,) as e:
            logging.exception('save read failure', stack_info=True)
            return False
        return self.convert_from_formatted_str(board_save_data)

    def convert_to_formatted_str(self, board_to_convert):
        return self.board_to_str(board_to_convert)

    def convert_from_formatted_str(self, save_data):
        return self.str_to_board(save_data)

    @staticmethod
    def board_to_str(board):
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

    @staticmethod
    def str_to_board(str_data) -> list[list[int]]:
        """ converts from string format to array format """
        n = m = 9  # assumes 9 by 9

        reconstructed = list()
        j = 0
        row = list()
        for char in str_data:
            if not char.isdigit():
                char = 0
            char = int(char)
            row.append(char)
            j += 1
            if not j < n:
                reconstructed.append(row)
                row = list()
                j = 0

        return reconstructed


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
    data = io.read_and_load_board_from_17_hints_data_file()
    io.write_board_to_save_file(data)
    test_convert = io.read_and_load_all_boards_from_save_file()
    # print(io._board_to_str(test_convert))
    # print(u.strip_for_print(test_convert))

