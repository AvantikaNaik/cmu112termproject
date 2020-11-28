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
    visitedBlocks = [[False] * width + [True] for i in range(height)] + [[1] * (width +1)]
    print(visitedBlocks)

def backtrackThrough(app, row, col, grid):
    visitedBlocks[row][col] = True
    directions = [(row + 1, col), (row - 1,col), (row, col -1), (row, col + 1)]
    random.shuffle(directions)
    for (newRow, newCol) in directions:
        if not visitedBlocks[newRow][newCol]:
            if newRow == row:
                app.gridCells[max(newCol, col)][row].topLine = False
                app.gridCells[min(newCol, col)][row].topLine = False
            if newCol == col:
                

def spawnKey(app):
    row = random.randint(0,app.rows-1)
    col = random.randint(0,app.cols-1)
    app.keyLocation = (row, col)

########################################################
# Data Classes and Normal Classes
########################################################
GridBlock = make_dataclass('GridBlock', ['topLine', 'bottomLine', 'leftLine',\
            'rightLine', "row", "col"])

########################################################
# App stuff
########################################################

def appStarted(app):
    app.journalVisible = False
    app.journalEntry = False

    app.clues = []
    app.text1= "Start typing..."

    app.rows = 10
    app.cols = 10
    app.margin = 20

    app.gridBlocks = make2dList(app.rows, app.cols)
    for row in range(app.rows):
        for col in range(app.cols):
            newBlock = GridBlock(topLine=True, bottomLine=True, leftLine=True,\
                        rightLine=True, row=row, col=col)
            app.gridBlocks[row][col] = newBlock
            
    app.playerX = app.margin * 2
    app.playerY = app.margin * 2

    app.keyLocation = (0, 0)
    spawnKey(app)
    makeMaze(app, app.rows, app.cols)

def timerFired(app):
    pass

def playerLegal(app):
    if (app.playerX - 10 < app.margin or app.playerX + 10 > app.width - app.margin
        or app.playerY - 10 < app.margin or app.playerY + 10 > app.height - app.margin):
        print("hello")
        return False
    return True

def keyPressed(app, event):
    app.playerSpeed = 5
    if event.key == "Up":
        app.playerY -= app.playerSpeed
        if not playerLegal(app):
            app.playerY += app.playerSpeed
    elif event.key == "Down":
        app.playerY += app.playerSpeed
        if not playerLegal(app):
            app.playerY -= app.playerSpeed
    elif event.key == "Left":
        app.playerX -= app.playerSpeed
        if not playerLegal(app):
            app.playerX += app.playerSpeed
    elif event.key == "Right":
        app.playerX += app.playerSpeed
        if not playerLegal(app):
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
    print(event.x, event.y)
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
    canvas.create_oval(app.playerX - 10, app.playerY - 10, app.playerX + 10, app.playerY + 10, fill="yellow")

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
    if app.journalVisible:
        drawJournalScreen(app, canvas)
    if app.journalEntry:
        drawTextBoxText(app, canvas)


runApp(width=800, height=800)

if __name__ == '__main__':
    main()