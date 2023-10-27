import sys
import copy
import time

boards = []
symbols = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
d = {}
dsets = {}
options = {}
symbol_set = ()

with open(sys.argv[1]) as f:
    for line in f:
        boards.append(line.strip())

def globalDictionary(board, size, height, width):
    dictionary = {}
    dsets[size] = set()
    for x in range(0, len(board)):
        blocks = set()
        rows = set()
        colomns = set()
        dictionary[x] = []
        start = int(x / size) * size
        for y in range(start, start + size):
            if (y != x):
                rows.add(y)
        colomn = int(x % size)
        for y in range(0, size):
            if (y * size + colomn != x):
                colomns.add(y * size + colomn)
        rowStart = int(int(x / size) / height) * height
        blockStart = int((x % size) / width) * width
        for y in range(blockStart, blockStart + width):
            for z in range(rowStart, rowStart + height):
                w = int(z * size + y)
                if (w != x):
                    blocks.add(w)
        dictionary[x] = (rows | colomns) | blocks
        rows.add(x)
        colomns.add(x)
        blocks.add(x)
        dsets[size].add(tuple(rows))
        dsets[size].add(tuple(colomns))
        dsets[size].add(tuple(blocks))
    return dictionary


def createOptions(board, size):
    for x in range(0, len(board)):
        options[x] = ""
        for y in symbol_set:
            options[x] = options[x] + str(y)
        for y in d[size][x]:
            if (board[y] in str(options[x])):
                z = options[x].index(board[y])
                options[x] = options[x][0:z] + options[x][z + 1:]
    return options


def printPuzzle(board, n, height, width):
    block1 = 0
    for x in range(0, n):
        line = ""
        if (block1 % height == 0):
            print("")
        block1 = block1 + 1
        block2 = 0
        for y in range(0, n):
            if (block2 % width == 0):
                line = line + "  "
            block2 = block2 + 1
            line = line + " " + board[x * n + y]
        print(line)


def getNext(board):
    for y in range(0, len(board)):
        if (board[y] == "."):
            return y


def getSorted(board, var, size, height, width):
    children = []
    for x in symbol_set:
        boo = True
        newState = board[0:var] + x + board[var + 1:]
        for y in d[size][var]:
            if (x == newState[y]):
                boo = False
        if (boo == True):
            children.append(newState)
    return children


def csp_backtracking(board, size, height, width):
    if ("." not in board):
        return board
    var = getNext(board)
    for newBoard in getSorted(board, var, size, height, width):
        result = csp_backtracking(newBoard, size, height, width)
        if (result is not None):
            return result
    return None


def constraintSatisfaction(board, size, constraints):
    for x in dsets[size]:
        for y in symbol_set:
            r = 0
            ro = 0
            for z in x:
                if (board[z] == str(y)):
                    r = 2
                    break
                if (r == 2):
                    break
                if ((y in constraints[z]) and (board[z] == ".")):
                    r = r + 1
                    ro = z
            if (r == 0):
                return None
            if (r == 1):
                board = board[0:ro] + str(y) + board[ro + 1:]
                constraints[ro] = str(y)
                temp = forwardLooking(board, size, ro, constraints)
                if (temp == None):
                    return None
                return constraintSatisfaction(temp[0], size, temp[1])
    return (board, constraints)


def getNextFL(board, constraints):
    minIndex = board.index(".")
    for x in range(0, len(board)):
        if ((len(constraints[x]) <= len(constraints[minIndex])) and board[x] == "."):
            minIndex = x
    return minIndex


def updateOnes(board, size, var, constraints):
    for x in d[size][var]:
        if ((len(constraints[x]) == 1) and (board[x] == ".")):
            board = board[0:x] + str(constraints[x]) + board[x + 1:]
            temp = forwardLooking(board, size, x, constraints)
            if (temp == None):
                return None
            board = temp[0]
            constraints = temp[1]
    return (board, constraints)


def forwardLooking(board, size, var, constraints):
    s = copy.copy(constraints)
    val = board[var]
    for x in d[size][var]:
        if (val in s[x]):
            z = s[x].index(val)
            s[x] = s[x][0:z] + s[x][z + 1:]
        if (len(s[x]) == 0 and board[x] == "."):
            return None
    return updateOnes(board, size, var, s)


def csp_backtrackingFL(board, size, height, width, constraints):
    if ("." not in board):
        return board
    var = getNextFL(board, constraints)
    choices = copy.copy(constraints[var])
    for newVal in choices:
        newBoard = board[0:var] + str(newVal) + board[var + 1:]
        x = forwardLooking(newBoard, size, var, constraints)
        if (x is not None):
            y = constraintSatisfaction(x[0], size, x[1])
            if (y is not None):
                result = csp_backtrackingFL(y[0], size, height, width, y[1])
                if (result is not None):
                    return result
    return None


for x in boards:
    n = int(len(x) ** 0.5)
    subblock_height = 0
    subblock_width = 0
    symbol_set = ()
    for y in range(1, int(n ** 0.5) + 1):
        if ((n / y) - int(n / y) == 0):
            subblock_width = int(n / y)
            subblock_height = y
    for y in range(0, n):
        symbol_set = symbol_set + tuple(symbols[y])
    if (n not in d.keys()):
        d[n] = globalDictionary(x, n, subblock_height, subblock_width)
    start = time.perf_counter()
    options = createOptions(x, n)
    tri = constraintSatisfaction(x, n, options)
    solved = csp_backtrackingFL(tri[0], n, subblock_height, subblock_width, tri[1])
    end = time.perf_counter()
    print(solved)
    print("")
