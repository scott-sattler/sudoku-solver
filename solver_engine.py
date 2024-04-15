""" doc """

'''
naive search:
    check each j vertical
    check each i horizontal
    check each ij local square
slight optimization:
    start with all possible values
    remove values found in naive search
independent solution:
    create a valid set for every row, column, and square
fully optimized:
    Exact Cover; Dancing Links (DLX); Algorithm X

'''

# todo: search in columns and pick most constrained cells
# todo: both optimal and looks way cooler

class NeedsName:
    """ create a valid set for every row, column, and square """
    def __init__(self):
        self.valid = set()


class ListNode:
    def __init__(self, val, prv=None, nxt=None):
        self.val = val
        self.prv = prv
        self.nxt = nxt


class SolverEngine:
    def __init__(self, board=None):
        self.dhead = ListNode(None)

    def find_empty(self, board) -> tuple[int, int]:
        # return self._find_empty(board)
        return self._find_empty_greedy(board)

    def hv_rule_check(self, board, i, j) -> bool:
        """ checks (i, j) row and colum for board[i][j] value"""
        return self._hv_rule_check(board, i, j)

    def s_rule_check(self, board, i, j) -> bool:
        """ checks the local 9 square grid for board[i][j] value """
        return self._s_rule_check(board, i, j)

    # todo: refactor
    def validate_board(self, board_data):
        for i in range(len(board_data)):
            for j in range(len(board_data)):
                if not self.hv_rule_check(board_data, i, j):
                    return False
                if not self.s_rule_check(board_data, i, j):
                    return False
        if not self._find_empty(board_data):
            return True
        return False

    def solve_board(self, board_data):
        return self._solve_board(board_data)



    ###########################################################################


    def _solve_board(self, board_data):
        from copy import deepcopy

        # seed agenda
        agenda = [board_data]
        last_board = deepcopy(board_data)
        while agenda:
            curr_board = agenda.pop()
            next_empty = self.find_empty(curr_board)

            if not next_empty:
                break

            i, j = next_empty
            for val in range(9, 0, -1):  # preserves dfs ascending search
                curr_board[i][j] = val
                rule_h_v = self.hv_rule_check(curr_board, i, j)
                rule_s = self.s_rule_check(curr_board, i, j)
                if rule_h_v and rule_s:
                    agenda.append(deepcopy(curr_board))

                    next_limited_update = list()
                    for i_u in range(9):
                        for j_u in range(9):
                            val = curr_board[i_u][j_u]
                            if val != last_board[i_u][j_u]:
                                next_limited_update.append((i_u, j_u, val))
                    sent = yield next_limited_update
                    if sent == 'stop':
                        break
                    last_board = deepcopy(curr_board)


    @staticmethod
    def _find_empty_greedy(board) -> tuple[int, int] | None:
        """
            primary motivation: looks way cooler ;-)

            assumes most constrained cell is optimal
            creates a grid of possible moves for each cell

            note: very inefficient
        """

        choices = list(range(1, 10))
        possible_moves = [
            [[] for _ in range(len(board))] for _ in range(len(board))
        ]

        # find row moves
        row_moves = list(range(9))
        for i in range(len(board)):
            row_moves[i] = [val for val in choices if val not in board[i]]

        # find column moves
        col_moves = list(range(9))
        for j in range(len(board)):
            # find invalid column moves
            col_nums = []
            for i in range(len(board)):
                if board[i][j] > 0:
                    col_nums.append(board[i][j])
            col_moves[j] = [val for val in choices if val not in col_nums]

        # find square moves
        sqr_moves = [[list(range(1, 10)) for _ in range(3)] for _ in range(3)]
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    continue
                s_i = i // 3
                s_j = (j // 3) % 3
                if board[i][j] not in sqr_moves[s_i][s_j]:
                    return None
                sqr_moves[s_i][s_j].remove(board[i][j])

        # find intersection of vertical, horizontal, and square
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    sqr_i = i // 3
                    sqr_j = (j // 3) % 3
                    all_moves = (set(row_moves[i]) &
                                 set(col_moves[j]) &
                                 set(sqr_moves[sqr_i][sqr_j]))
                    all_moves = list(all_moves)
                    all_moves.sort()
                    possible_moves[i][j] = all_moves

        # find the most constrained cell
        min_cell = ([0] * 10, None)
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] != 0:
                    continue
                if len(possible_moves[i][j]) < len(min_cell[0]):
                    min_cell = (possible_moves[i][j], (i, j))

        return min_cell[1]  # [0], min_cell[1][1]  # todo

    # correctness/naive/brute force implementation
    @staticmethod
    def _hv_find(board, i, j, value) -> bool:
        """ checks board (i, j) row and colum for value"""

        board_val = value

        for var_ij in range(len(board)):
            if value or (i, var_ij) != (i, j):
                if board[i][var_ij] == board_val:
                    return True
            if (var_ij, j) != (i, j) and board[var_ij][j] == board_val:
                return False
        return True

    @staticmethod
    def _find_empty(board) -> tuple[int, int] | bool:
        """ finds the first empty from (0, 0) """
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0:
                    return i, j
        return False

    # correctness/naive/brute force implementation
    @staticmethod
    def _hv_rule_check(board, i, j) -> bool:
        """ checks (i, j) row and colum for board[i][j] value"""
        board_val = board[i][j]
        for var_ij in range(len(board)):
            if (i, var_ij) != (i, j) and board[i][var_ij] == board_val:
                return False
            if (var_ij, j) != (i, j) and board[var_ij][j] == board_val:
                return False
        return True

    # correctness/naive/brute force implementation
    @staticmethod
    def _s_rule_check(board, i, j) -> bool:
        """ checks the local 9 square grid for board[i][j] value """
        # get top left corner of each 3x3 square
        i_0 = i - (i % 3)
        j_0 = j - (j % 3)
        board_val = board[i][j]
        for k in range(3):
            for l in range(3):
                if (i, j) == (k + i_0, l + j_0):
                    continue
                sqr_board_val = board[k + i_0][l + j_0]
                if sqr_board_val == board_val:
                    return False
        return True
