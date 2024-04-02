def pretty_print(matrix):
    SIZE = len(matrix[0])

    for row in range(SIZE):
        if row % 3 == 0:
            print('\n', "-------------------------------------", end=' ')  # todo hardcoded
        print()
        for column in range(SIZE):
            if column % 3 == 0:
                print("|", "", end=' ')
            if matrix[row][column] != 0:
                print(matrix[row][column], "", end=' ')
            else:
                print(" ", "", end=' ')
        print("|", "", end=' ')
    print('\n', "-------------------------------------", end=' ')  # todo hardcoded
    return ""