from unittest import TestCase
import tkinter
from pixel_gui import CanvasGUI
import test_cases




'''
todo:
    boundary testing
    
    ...
    actual testing...
    
'''

tc = test_cases.TestMatrices()


class TryTesting(TestCase):

    def test_01(self):
        fn = CanvasGUI._s_rule_check
        board = [[1 for col in range(9)] for row in range(9)]
        board[0][0] = 2
        # print(board)
        result = fn(board, 0, 0)
        self.assertTrue(result)

    def test_01(self):
        fn = CanvasGUI._s_rule_check
        board = [[1 for col in range(9)] for row in range(9)]
        board[0][0] = 2
        # print(board)
        result = fn(board, 0, 0)
        self.assertTrue(result)

    def test_square_on_01_test(self):
        fn = CanvasGUI._s_rule_check
        board = tc.matrix_01()
        for i in range(9):
            for j in range(9):
                if board[i][j]:
                    result = fn(board, i, j)
                    # print(i, j, result)
                    # print(pretty_print(board))
                    self.assertTrue(result)

    def test_vert_hor_on_01_test(self):
        fn = CanvasGUI._hv_rule_check
        board = tc.matrix_01()
        for i in range(9):
            for j in range(9):
                if board[i][j]:
                    result = fn(board, i, j)
                    # print(i, j, result)
                    # print(pretty_print(board))
                    self.assertTrue(result)

    def test_square_0_7(self):
        fn = CanvasGUI._s_rule_check
        board = tc.matrix_01()
        i, j = 0, 7
        result = fn(board, i, j)
        # print(i, j, result)
        # print(pretty_print(board))
        self.assertTrue(result)
