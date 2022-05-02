entering = 0
master_string = []
while entering < 9:
    matrix_input = raw_input("Enter the values of each row without spaces (empty = 0): ", )
    if len(matrix_input) != 9:
        print "Error!"

    string = []

    if len(matrix_input) == 9:
        for i in range(len(matrix_input)):
            if i == 0:
                #print "[%s," % matrix_input[i],
                string += matrix_input[i]
            if i == len(matrix_input) - 1:
                #print "%s]," % matrix_input[i],
                string += matrix_input[i]
            if i != 0 and i != len(matrix_input) - 1:
                #print "%s," % matrix_input[i],
                string += matrix_input[i]

        entering += 1

        mapped_string = map(int, string)
        master_string.append(mapped_string)

    if entering == 9:
        print master_string





