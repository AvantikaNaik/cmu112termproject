#######################################################
# Avantika Naik
# Phasmophobia112
# Started: Nov 19th 
# Ended:
#######################################################
from cmu_112_graphics import *
import random
import time
from dataclasses import make_dataclass
from random import shuffle, randrange

#######################################################
# 15-112 Functions
#######################################################

# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
# Gets row and col based on x, y coords
def getCell(app, x, y):
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth  = gridWidth / app.cols
    cellHeight = gridHeight / app.rows

    # Note: we have to use int() here and not just // because
    # row and col cannot be floats and if any of x, y, app.margin,
    # cellWidth or cellHeight are floats, // would still produce floats.
    row = int((y - app.margin) / cellHeight)
    col = int((x - app.margin) / cellWidth)
    return (row, col)



# Returns bounds to make a grid given row, col
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
def getCellBounds(app, row, col):
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + col * cellWidth
    x1 = app.margin + (col+1) * cellWidth
    y0 = app.margin + row * cellHeight
    y1 = app.margin + (row+1) * cellHeight
    return (x0, y0, x1, y1)

# Makes a 2-d list
# https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html
def make2dList(rows, cols):
    return [ ([False] * cols) for row in range(rows) ]

########################################################
# Helper Functions
########################################################

# Makes maze recursively with backtracking
# https://medium.com/swlh/fun-with-python-1-maze-generator-931639b4fb7e
# For idea on how to make the maze - Prim's Algo
# https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#mazeSolving
# Used this to reverse engineer the maze as well

def makeMaze(app, width, height):
    visitedBlocks = [[False] * width + [True] for _ in range(height)] + [[1] * (width +1)]

    def backtrackThrough(app, row, col):
        visitedBlocks[col][row] = True
        directions = [(row + 1, col), (row - 1,col), (row, col -1), (row, col + 1)]
        random.shuffle(directions)
        for (newRow, newCol) in directions:
            if not visitedBlocks[newCol][newRow]:
                if newRow == row:
                    app.gridBlocks[max(newCol, col)][row].topLine = False
                    app.gridBlocks[min(newCol, col)][row].bottomLine = False
                if newCol == col:
                    app.gridBlocks[col][max(newRow, row)].leftLine = False
                    app.gridBlocks[col][min(newRow, row)].rightLine = False
                backtrackThrough(app, newRow, newCol)

    row = random.randint(0, app.rows - 1) 
    col = random.randint(0, app.cols - 1)
    backtrackThrough(app,row ,col)

def spawnKey(app):
    row = random.randint(2,app.rows-1)
    col = random.randint(2,app.cols-1)
    app.keyLocation = (row, col)

# https://mat.uab.cat/~alseda/MasterOpt/AStar-Algorithm.pdf
def astar(app, startval, endval):
    # Init start and end nodes, and lists
    start = Node(None, startval)
    end = Node(None, endval)
    
    openList = []
    closedList = []

    openList.append(start)

    # Loop until you find end
    while len(openList) > 0:
        current = openList[0]
        bestNode = 0
        for i in range(len(openList)):
            if current.cost > openList[i].cost:
                current = openList[i]
                bestNode = i

        openList.pop(bestNode)
        closedList.append(current)
        # if you're at end, return path (backtrackingly)
        if current == end:
            path = []
            tempcurrent = current
            while tempcurrent != None:
                path.append(tempcurrent.position)
                tempcurrent = tempcurrent.parent
            return path[::-1]

        children = []
        print("here")
        # children are adjacent nodes
        for (drow, dcol) in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            row = current.position[0] + drow
            col = current.position[1] + dcol
            if 0 <= row < app.rows and 0 <= col < app.cols and ghostCanMove(app, drow, dcol, row, col) : 
                new_node = Node(current, (row,col))
                children.append(new_node)

        for child in children:
            for closedChild in closedList:
                if child != closedChild:
                    child.distance = current.distance + 1
                    child.heuristic = ((child.position[0] - end.position[0]) ** 2) + ((child.position[1] - end.position[1]) ** 2)
                    child.cost = child.distance + child.heuristic

                    for openNode in openList:
                        if child == openNode and child.distance > openNode.distance:
                            continue
                    openList.append(child)

def ghostCanMove(app, drow, dcol, row, col):
    if drow == 0:
        if dcol == 1 and not app.gridBlocks[row][col].leftLine:
            return True
        elif dcol == -1 and not app.gridBlocks[row][col].rightLine:
            return True
    elif dcol == 0:
        if drow == 1 and not app.gridBlocks[row][col].bottomLine:
            return True
        elif drow == -1 and not app.gridBlocks[row][col].topLine:
            return True
    return False

def moveGhost(app):
    print("entered")
    gRow, gCol = getCell(app, app.ghostX, app.ghostY)
    pRow, pCol = getCell(app, app.playerX, app.playerY)
    start = (gRow, gCol)
    end = (pRow, pCol)
    print("start:", start, "end", end)
    print("star")
    path = astar(app, start, end)
    print("path:", path)
    #(app.ghostX, app.ghostY) = path[1]

########################################################
# Data Classes and Normal Classes
########################################################
GridBlock = make_dataclass('GridBlock', ['topLine', 'bottomLine', 'leftLine',\
            'rightLine', "row", "col"])

# Part of a* algo 
class Node():
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position

        self.distance = 0
        self.heuristic = 0
        self.cost = 0

    def __eq__(self, other):
        return (isinstance(other, Node) and self.position == other.position)

    def __repr__(self):
        return f"Node at {self.position} with f={self.cost}"

########################################################
# App stuff
########################################################

def appStarted(app):
    app.journalVisible = False
    app.journalEntry = False

    app.clues = []
    app.text1= "Start typing..."

    app.rows = 5
    app.cols = 5
    app.margin = 20

    app.gridBlocks = make2dList(app.rows, app.cols)
    for row in range(app.rows):
        for col in range(app.cols):
            newBlock = GridBlock(topLine=True, bottomLine=True, leftLine=True,\
                        rightLine=True, row=row, col=col)
            app.gridBlocks[row][col] = newBlock
            
    app.playerX = app.margin * 2
    app.playerY = app.margin * 2
    app.ghostX  = app.width - app.margin * 2
    app.ghostY  = app.height - app.margin * 2

    app.keyLocation = (0, 0)
    #spawnKey(app)
    makeMaze(app, app.rows, app.cols)

def timerFired(app):
    #ghostMove(app)
    pass

def playerLegal(app, oldRow, oldCol):
    newRow, newCol = getCell(app, app.playerX, app.playerY)
    if (app.playerX - 10 < app.margin or app.playerX + 10 > app.width - app.margin
        or app.playerY - 10 < app.margin or app.playerY + 10 > app.height - app.margin):
        print("hello")
        return False
    elif not isLegal(app, oldRow, oldCol, newRow, newCol) :
        print("elsecase")
        return False

    return True

def ghostMove(app):
    oldRow, oldCol = getCell(app, app.ghostX, app.ghostY)
    ghostSpeed = 5
    if app.playerX > app.ghostX:
        app.ghostX += ghostSpeed
        newRow, newCol = getCell(app, app.ghostX, app.ghostY)
        if not isLegal(app, oldRow, oldCol, newRow, newCol):
            app.ghostX -= ghostSpeed
    else:
        app.ghostX -= ghostSpeed
        newRow, newCol = getCell(app, app.ghostX, app.ghostY)
        if not isLegal(app, oldRow, oldCol, newRow, newCol):
            app.ghostX += ghostSpeed
    if app.playerY > app.ghostY:
        app.ghostY += ghostSpeed
        newRow, newCol = getCell(app, app.ghostX, app.ghostY)
        if not isLegal(app, oldRow, oldCol, newRow, newCol):
            app.ghostX -= ghostSpeed
    else:
        newRow, newCol = getCell(app, app.ghostX, app.ghostY)
        app.ghostY -= ghostSpeed
        if not isLegal(app, oldRow, oldCol, newRow, newCol):
            app.ghostX += ghostSpeed
        
def isLegal(app, oldRow, oldCol, newRow, newCol):
    if newRow == oldRow and newCol == oldCol:
        return True
    if newRow < oldRow and app.gridBlocks[newRow][newCol].bottomLine == False:
        return True
    if newRow > oldRow and app.gridBlocks[newRow][newCol].topLine == False:
        return True
    if newCol > oldCol and app.gridBlocks[newRow][newCol].leftLine == False:
        return True
    if newCol < oldCol and app.gridBlocks[newRow][newCol].rightLine == False:
        return True
    return False
        

def keyPressed(app, event):
    if event.key == "u":
        moveGhost(app)
    app.playerSpeed = 5
    oldRow, oldCol = getCell(app, app.playerX, app.playerY)
    if event.key == "Up" or event.key == "w":
        app.playerY -= app.playerSpeed
        if not playerLegal(app, oldRow, oldCol):
            app.playerY += app.playerSpeed
    elif event.key == "Down" or event.key == "s":
        app.playerY += app.playerSpeed
        if not playerLegal(app, oldRow, oldCol):
            app.playerY -= app.playerSpeed
    elif event.key == "Left" or event.key == "a":
        app.playerX -= app.playerSpeed
        if not playerLegal(app, oldRow, oldCol):
            app.playerX += app.playerSpeed
    elif event.key == "Right" or event.key == "d":
        app.playerX += app.playerSpeed
        if not playerLegal(app, oldRow, oldCol):
            app.playerX -= app.playerSpeed

    if event.key == "j" and not app.journalEntry:
        app.journalVisible = not app.journalVisible
    if app.journalEntry:
        if app.text1 == "Start typing...":
            app.text1 = ""
        if event.key == "Enter":
            app.journalEntry = not app.journalEntry
        if event.key == "Backspace":
            endVal = len(app.text1)
            if endVal != 0:
                app.text1 = app.text1[:endVal-1]
            else:
                app.text1 = ""
        elif event.key == "Space":
            app.text1 += " "
        elif event.key in ["Up", "Down", "Left","Right"]:
            app.text1 += "" 
        else:
            app.text1 += event.key


def mousePressed(app, event):
    if (app.journalVisible and (app.width//4) < event.x <= (3 * app.width//4) \
        and 10 < event.y < 50):
        print("enteredjournalmode")
        app.journalEntry = True

def drawTextBoxText(app, canvas):
    canvas.create_text(app.width//2, app.height//2, text = app.text1)

def drawJournalScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "brown")
    canvas.create_rectangle(app.width//4, 10, 3 * app.width//4, 50, fill = "yellow")
    canvas.create_text(app.width//2, 30, text="Add new journal entry") 

def drawKey(app, canvas):
    (x0, y0, x1, y1) = getCellBounds(app,app.keyLocation[0], app.keyLocation[1])
    canvas.create_oval(x0, y0, x1, y1, fill="yellow")

def drawPlayer(app, canvas):
    canvas.create_oval(app.playerX - 10, app.playerY - 10, app.playerX + 10, app.playerY + 10, fill="blue")

def drawGhost(app, canvas):
    canvas.create_oval(app.ghostX - 10, app.ghostY - 10, app.ghostX + 10, app.ghostY + 10, fill="red")

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.height, app.width, fill = "red")
    for row in range(app.rows):
        for col in range(app.cols):
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1, fill="black")
            block = app.gridBlocks[row][col]
            if block.topLine:
                canvas.create_line(x0, y0, x1, y0, width = 3, fill="white")
            if block.leftLine:
                canvas.create_line(x0, y0, x0, y1, width = 3, fill="white")
            if block.rightLine:
                canvas.create_line(x1, y0, x1, y1, width = 3, fill="white")
            if block.bottomLine:
                canvas.create_line(x0, y1, x1, y1, width = 3, fill="white")
    drawKey(app, canvas)
    drawPlayer(app, canvas)
    drawGhost(app, canvas)
    if app.journalVisible:
        drawJournalScreen(app, canvas)
    if app.journalEntry:
        drawTextBoxText(app, canvas)


runApp(width=800, height=800)

if __name__ == '__main__':
    main()