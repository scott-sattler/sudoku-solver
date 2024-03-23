def matrix_01():
    test_matrix = [[5, 0, 2, 0, 9, 0, 7, 8, 6],
                   [9, 0, 3, 0, 6, 0, 5, 0, 0],
                   [6, 7, 1, 8, 0, 0, 3, 2, 9],
                   [0, 0, 0, 7, 5, 1, 9, 0, 0],
                   [8, 9, 0, 4, 0, 2, 0, 6, 7],
                   [0, 0, 4, 6, 8, 9, 0, 0, 0],
                   [4, 2, 7, 0, 0, 8, 6, 9, 3],
                   [0, 0, 9, 0, 7, 0, 8, 0, 2],
                   [3, 5, 8, 0, 2, 0, 4, 0, 1]]
    return test_matrix


def strip_print(board):
    # ''.join(['  '.join(map(str, row)) + '\n' for row in board])
    out = list()
    for row in board:
        row_str = '  '.join(map(str, row)) + '\n'
        out.append(row_str)
    return ''.join(out)


def pretty_print(board):
    # using "│ ─ ┼"

    out = list()
    for i in range(9):
        for j in range(9):
            next_value = f'{board[i][j]}'
            if j > 0:
                next_value = ' ' + next_value
            if j < 8:
                next_value += ' '
            if 8 > j > 0 and j % 3 == 2:
                next_value += f'{chr(9474)}'  # │
            out.append(next_value)
        out.append('\n')

        # bottom square separator
        if i < 8 and i % 3 == 2:
            line = list()
            for k in range((9 * 3) - 4):
                if 18 > k > 0 and k % 8 == 0:
                    line.append(chr(9532) + chr(9472) * 2)  # ┼ ─
                else:
                    line.append(chr(9472))  # ─
            line.append('\n')
            out.append(''.join(line))

    return ''.join(out)


if __name__ == '__main__':
    print(strip_print(matrix_01()))
    print(pretty_print(matrix_01()))
