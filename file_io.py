import logging
import os


class FileIO:
    def __init__(self, local_path='./', file_name='sudoku_save'):
        self.path = local_path
        self.file_name = file_name + '.txt'

        if self.path == './':
            self.path = os.path.abspath(self.file_name)
        if not os.path.isfile(self.path):
            self.create_file()

        logger = logging.getLogger(__name__)
        logging.basicConfig(filename='io_log.log', encoding='utf-8', level=logging.DEBUG)
        # logger.debug .info .warning .error

    def create_file(self):
        try:
            f = open(self.path, 'x')
            f.close()
            logging.info(f'file creation successful:\n\t{self.path}')
        except (Exception,):
            logging.warning(f'file creation failure:\n\t{self.path}')

    def write_to_file(self, write_data):
        try:
            with open(self.path, 'a') as f:
                encoded = self.board_to_str(write_data) + '\n'
                f.write(encoded)
                f.close()
                logging.info(f'write successful:\n\t{self.path}\n\t{encoded}')
        except (Exception,) as e:
            logging.exception('write failure', stack_info=True)
            return False
        return True

    def read_from_file(self):
        """ returns a list of boards """
        all_data = list()
        try:
            with open(self.path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    decoded = self.str_to_board(line)
                    all_data.append(decoded)
                logging.info('read successful')
        except (Exception,) as e:
            logging.exception('read failure', stack_info=True)
            return False
        return all_data


    @staticmethod
    def board_to_str(board):
        n, m = len(board), len(board[0])
        to_str = [f'({n}, {m})']
        for i in range(n):
            for j in range(m):
                to_str.append(str(board[i][j]))
        to_str = ' '.join(to_str)
        return to_str

    @staticmethod
    def str_to_board(str_data) -> list[list[int]]:
        end = str_data.index(')')
        n, m = map(int, str_data[1:end].split(','))

        str_data = str_data[7:]
        reconstructed = list()
        i = 0
        while i < len(str_data):
            j, row = 0, list()
            while i < len(str_data) and j < m:
                if str_data[i].isdigit():
                    row.append(int(str_data[i]))
                    j += 1
                i += 1
            if i < len(str_data):
                reconstructed.append(row)
        return reconstructed




if __name__ == '__main__':
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
    io.write_to_file(test_data)
    data = io.read_from_file()
    print(data)

