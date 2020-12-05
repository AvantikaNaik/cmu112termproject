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
import math

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

def distance(x1, y1, x2, y2):
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5 
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
    keyRow = random.randint(3,app.rows-1)
    keyCol = random.randint(3,app.cols-1)
    currentlyPlacedItems = app.currentClues
    currentlyPlacedItems.append(app.bonusItem)
    for (item, row, col) in currentlyPlacedItems:
        if keyRow == row and keyCol == col:
            keyRow = random.randint(3, app.rows -1)
    app.keyLocation = (keyRow, keyCol)

# https://mat.uab.cat/~alseda/MasterOpt/AStar-Algorithm.pdf
def astar(app, startval, endval):
    # Init start and end nodes, and lists
    start = Node(None, startval)
    end = Node(None, endval)
    
    openList = []
    closedList = set()

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
        closedList.add(current)
        # if you're at end, return path (backtrackingly)
        if current == end:
            path = []
            tempcurrent = current
            while tempcurrent != None:
                path.append(tempcurrent.position)
                tempcurrent = tempcurrent.parent
            return path[::-1]

        children = []
        # children are adjacent nodes
        for (drow, dcol) in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            row = current.position[0] + drow
            col = current.position[1] + dcol
            if 0 <= row < app.rows and 0 <= col < app.cols and ghostCanMove(app, drow, dcol, row, col) : 
                new_node = Node(current, (row,col))
                children.append(new_node)

        # Thanks to TA Elena H for helping me debug this part! 
        for child in children:
            if child not in closedList:
                child.distance = current.distance + 1
                child.heuristic = ((child.position[0] - end.position[0]) ** 2) + ((child.position[1] - end.position[1]) ** 2)
                child.cost = child.distance + child.heuristic  
            if child not in openList:                    
                openList.append(child)

def ghostCanMove(app, drow, dcol, row, col):
    if drow == 0:
        if dcol == 1 and not app.gridBlocks[row][col].leftLine:
            return True
        elif dcol == -1 and not app.gridBlocks[row][col].rightLine:
            return True
    if dcol == 0:
        if drow == 1 and not app.gridBlocks[row][col].topLine:
            return True
        elif drow == -1 and not app.gridBlocks[row][col].bottomLine:
            return True
    return False

def moveGhost(app):
    gRow, gCol = getCell(app, app.ghostX, app.ghostY)
    pRow, pCol = getCell(app, app.playerX, app.playerY)
    start = (gRow, gCol)
    end = (pRow, pCol)
    app.path = astar(app, start, end)
    if len(app.path) > 1:
        row, col = app.path[1]
        (x0, y0, x1, y1) = getCellBounds(app, row, col)
        app.targetX = (x0 + x1) //2
        app.targetY = (y0 + y1)//2

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

    def __hash__(self):
        return hash((self.parent, self.position, self.distance, self.heuristic, self.cost))
########################################################
# App stuff
########################################################

def appStarted(app):
    app.journalVisible = False
    app.journalEntry = False

    app.text0=["Click to start typing...", app.width//2, app.height//4]
    app.text1= ["Click to start typing...", app.width//2, app.height//2]
    app.text2= ["Click to start typing...", app.width//2, 3 * app.height//4]
    app.journal = [app.text0, app.text1 ,app.text2]
    app.currentText = -1

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
    app.ghostX  = app.width - app.margin * 2
    app.ghostY  = app.height - app.margin * 2
    app.targetX = app.width - 30
    app.targetY = app.height - 30
    app.pathVal = 0

    app.titleScreen = True
    app.helpScreen = False
    app.gameOver = False
    app.totalPoints = 0
    app.time = 0 

    app.t0 = 0

    app.gotKey= False
    app.keyToastShowing = False
    app.keyToastTimer = 0

    app.lightDistance = 1
    app.win = False

    app.clues = ["handprint", "ectoplasm", "freezing temps", "blood splatter",\
                "writing", "water"]
    chooseClues(app)
    app.currentClues = [app.firstClue, app.secondClue, app.thirdClue]
    app.foundFirstClue = False
    app.foundSecondClue = False
    app.foundThirdClue = False
    app.clue1Timer = 0
    app.clue1ToastShowing = False
    app.clue2Timer = 0
    app.clue2ToastShowing = False
    app.clue3Timer = 0
    app.clue3ToastShowing = False

    app.bonus = ["crucifix", "battery", "snack"]
    chooseBonus(app)
    app.bonusToastTimer = 0
    app.bonusToastShowing = False
    app.hasCrucifix = False
    app.usedCrucifix = False
    app.crucifixTimer = 0
    app.crucifixToastShowing = False


    app.keyLocation = (0, 0)
    spawnKey(app)
    makeMaze(app, app.rows, app.cols)

def isDead(app):
    if app.hasCrucifix and distance(app.playerX, app.playerY, app.ghostX, app.ghostY) < 20: 
        app.hasCrucifix = False
        app.usedCrucifix = True 
        if app.playerY > app.height//2:
            ghostRow = random.randint(5, 9)
        else: ghostRow = random.randint(1,5)
        if app.playerX > app.width//2:
            ghostCol = random.randint(1,5)
        else: ghostCol = random.randint(5,9)
        (x0, y0, x1, y1) = getCellBounds(app, ghostRow, ghostCol)
        app.ghostX = (x0+x1)//2
        app.ghostY = (y0+y1)//2
        return False
    if distance(app.playerX, app.playerY, app.ghostX, app.ghostY) < 20:
        return True 
    return False 

def gotKey(app):
    keyRow, keyCol = app.keyLocation
    (x0, y0, x1, y1) = getCellBounds(app, keyRow, keyCol)
    if (x0 < app.playerX < x1) and (y0 < app.playerY < y1):
        return True
    return False

def gotBonus(app):
    pRow, pCol = getCell(app, app.playerX, app.playerY)
    if pRow == app.bonusItem[1] and pCol == app.bonusItem[2]:
        return True 
    return False

def gotClue(app):
    pRow, pCol = getCell(app, app.playerX, app.playerY)
    for i in range(len(app.currentClues)):
        (item, row, col) = app.currentClues[i]
        if row == pRow and col == pCol:
            if i == 0:
                app.foundFirstClue = True
                app.currentClues[i] = (item, -20, -20)
            elif i == 1:
                app.foundSecondClue = True
                app.currentClues[i] = (item, -20, -20)
            elif i == 2:
                app.foundThirdClue = True 
                app.currentClues[i] = (item, -20, -20)

def checkForWin(app):
    row, col = getCell(app, app.playerX, app.playerY)
    if app.gotKey and (row, col) == (app.rows - 1, app.cols - 1):
        if not app.win:
            app.totalPoints += 1000
        return True
    return False

def chooseBonus(app):
    bonusNum = random.randint(0, len(app.bonus) - 1)
    item = app.bonus[bonusNum]
    bonusRow = random.randint(2, app.rows -1)
    bonusCol = random.randint(2, app.cols -1)
    for (clue, row, col) in app.currentClues:
        if bonusRow == row and bonusCol == col:
            bonusRow = random.randint(2, app.rows -1)
    app.bonusItem = (item, bonusRow, bonusCol)

def chooseClues(app):
    (clue0, clue1, clue2) = tuple(random.sample(app.clues,3))
    (row1, row2, row3) = tuple(random.sample(list(range(app.rows)), 3))
    (col1, col2, col3) = tuple(random.sample(list(range(app.cols)), 3))
    app.firstClue = (clue0, row1, col1)
    app.secondClue = (clue1,row2,col2)
    app.thirdClue = (clue2, row3, col3)


def playerLegal(app, oldRow, oldCol):
    newRow, newCol = getCell(app, app.playerX, app.playerY)
    if (app.playerX - 10 < app.margin or app.playerX + 10 > app.width - app.margin
        or app.playerY - 10 < app.margin or app.playerY + 10 > app.height - app.margin):
        return False
    elif not isLegal(app, oldRow, oldCol, newRow, newCol) :
        return False

    return True

def ghostMove(app):
    if distance(app.targetX, app.targetY, app.ghostX, app.ghostY) > 7:
        if app.targetX > app.ghostX:
            app.ghostX += 5
        else: app.ghostX -= 5
        if app.targetY > app.ghostY:
            app.ghostY += 5
        else: app.ghostY -= 5
        
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

########################################################
# timerFired, keyPressed, mousePressed
########################################################

def timerFired(app):
    app.time += 1
    gotClue(app)
    if app.foundFirstClue:
        app.clue1Timer += 1
        app.clue1ToastShowing = True
        app.firstClue = (app.firstClue[0], -20, -20)
    if app.clue1Timer > 10:
        app.clue1ToastShowing = False
        app.foundFirstClue = False
    if app.foundSecondClue:
        app.clue2Timer += 1
        app.clue2ToastShowing = True
        app.secondClue = (app.secondClue[0], -20, -20)
    if app.clue2Timer > 10:
        app.clue2ToastShowing = False
        app.foundSecondClue = False
    if app.foundThirdClue:
        app.clue3Timer += 1
        app.clue3ToastShowing = True
        app.thirdClue = (app.thirdClue[0], -20, -20)
    if app.clue3Timer > 10:
        app.clue3ToastShowing = False
        app.foundThirdClue = False
    if checkForWin(app):
        app.win = True
    if gotBonus(app):
        app.foundBonus = True
        app.bonusToastShowing = True
        item = app.bonusItem[0]
        app.bonusItem = (item, -20, -20)
        if item == "snack":
            app.playerSpeed = 10 
        elif item == "battery": 
            app.lightDistance = 2
        elif item == "crucifix":
            app.hasCrucifix = True 
    if app.bonusToastShowing:
        app.bonusToastTimer += 1
        if app.bonusToastTimer > 7:
            app.bonusToastShowing = False
    if app.crucifixTimer > 7:
        app.crucifixToastShowing = False
    if app.usedCrucifix and app.crucifixTimer < 7:
        app.crucifixTimer += 1
        app.crucifixToastShowing = True
    if gotKey(app):
        app.gotKey = True
        app.keyLocation = (-20, -20)
        app.keyToastShowing = True
        if app.keyToastShowing:
            app.totalPoints += 10
    if app.keyToastShowing:
        app.keyToastTimer += 1
        if app.keyToastTimer > 7:
            app.keyToastShowing = False
    if isDead(app):
        app.gameOver = True 
    if not app.titleScreen and not app.helpScreen and (app.time % 5 == 0) :
        moveGhost(app)
    app.t0 += 1
    if app.t0 > 15:
        app.titleScreen = False
    if not app.gameOver and not app.win:
        app.totalPoints += 0.5
        ghostMove(app)

def keyPressed(app, event):
    if app.titleScreen:
        return 
    if not app.journalVisible:
        ghostMove(app)
        if event.key == "r":
            appStarted(app)
        if event.key == "h":
            app.helpScreen = not app.helpScreen
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
        if (app.journal[app.currentText])[0] == "Click to start typing...":
            (app.journal[app.currentText])[0] = ""
        if event.key == "Enter" or event.key == "Escape":
            app.journalEntry = not app.journalEntry
            app.currentText = -1
        if event.key == "Backspace":
            endVal = len((app.journal[app.currentText])[0])
            if endVal != 0:
                (app.journal[app.currentText])[0] = ((app.journal[app.currentText])[0])[:endVal-1]
            else:
                (app.journal[app.currentText])[0] = ""
        elif event.key == "Space":
            (app.journal[app.currentText])[0] += " "
        elif event.key in {"Up", "Down", "Left","Right"}:
            (app.journal[app.currentText])[0] += "" 
        elif event.key not in {"Backspace", "Enter", "Escape"}:
            (app.journal[app.currentText])[0] += event.key


def mousePressed(app, event):
    if app.journalVisible:
        for i in range(len(app.journal)):
            (text, textX, textY) = app.journal[i]
            horizontal = app.width-100
            if abs(textX - event.x) <= horizontal and abs(textY - event.y) <= 40:
                app.currentText = i
                app.journalEntry = True
            else: app.currentText

########################################################
# Draw Functions
########################################################

def drawTextBoxText(app, canvas):
    for i in range(len(app.journal)):
        (text, x, y) = app.journal[i]
        if i == app.currentText:
            fill="brown"
        else: fill="tan"
        canvas.create_rectangle(50, y-20, app.width-50, y +20, fill=fill)
        canvas.create_text(x, y, text=text)

def drawJournalScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "saddle brown")
    canvas.create_rectangle(app.width//4, 10, 3 * app.width//4, 50, fill = "yellow")
    canvas.create_text(app.width//2, 30, text="My Journal Entries") 

def drawKey(app, canvas):
    (x0, y0, x1, y1) = getCellBounds(app, app.keyLocation[0], app.keyLocation[1])
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_oval(midX - 10, midY+7, midX+10, midY+27, fill = "gold")
    canvas.create_rectangle(midX-3,y0 + 7 ,midX+3, midY+10, width=0, fill="gold")
    canvas.create_rectangle(midX, y0+10, midX + 22, y0 + 15, width=0, fill="gold")
    canvas.create_rectangle(midX, y0+25, midX + 15, y0 + 30, width=0, fill="gold")

def drawPlayer(app, canvas):
    canvas.create_oval(app.playerX - 10, app.playerY - 10, app.playerX + 10, app.playerY + 10, fill="blue")

def drawGhost(app, canvas):
    canvas.create_oval(app.ghostX - 10, app.ghostY - 10, app.ghostX + 10, app.ghostY + 10, fill="red")

def drawTitle(app, canvas):
    canvas.create_rectangle(0, 0, app.height, app.width, fill = "black")
    canvas.create_text(app.width//2, app.height//4, text="Phasmophobia112", fill="red", font="Gothic 60 bold")
    canvas.create_text(app.width//2, 2 * app.height//5, text="press r to reset", fill="red", font="Gothic 40 bold")
    canvas.create_text(app.width//2, 3 * app.height//5, text="press h for help", fill="red", font="Gothic 40 bold")
    canvas.create_text(app.width//2, 4 * app.height//5, text="Will you make it out alive?", fill="red", font="Gothic 40 bold")
    drawTitleGhost(app, canvas, 100, 400)
    drawTitleGhost(app, canvas, app.width - 100, 400)

def drawTitleGhost(app, canvas, x, y):
    canvas.create_oval(x - 60, y - 60, x + 60, y + 60, fill="red")
    canvas.create_rectangle(x - 60, y, x + 60, y + 100, fill="red", width=0)
    canvas.create_polygon(x-20, y + 100, x, y + 140, x + 20, y + 100, fill="red", width=0 )
    canvas.create_polygon(x-60, y + 100, x-50, y + 140, x - 20, y + 100, fill="red", width=0 )
    canvas.create_polygon(x+20, y + 100, x+50, y + 140, x + 60, y + 100, fill="red", width=0 )
    canvas.create_oval(x-40, y+10, x-20, y-10, fill="black")
    canvas.create_oval(x+20, y+10, x+40, y-10, fill="black")

def drawHelpScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.height, app.width, fill = "black")
    canvas.create_text(app.width//2, app.height//8, text="Goal:Find the key", fill="red", font="Gothic 40 bold")
    canvas.create_text(app.width//2, 2 * app.height//8, text="Once you find the key, the bottom right corner (door) opens.", fill="red", font="Gothic 15")
    canvas.create_text(app.width//2, 3 * app.height//8, text="As you try to escape, a ghost is trying to find you.", fill="red", font="Gothic 15")
    canvas.create_text(app.width//2, 4 * app.height//8, text="If it gets you, it's game over. Press r to reset if that happens.", fill="red", font="Gothic 15")
    canvas.create_text(app.width//2, 5 * app.height//8, text="While traversing the maze, you might come across clues.", fill="red", font="Gothic 15")
    canvas.create_text(app.width//2, 6 * app.height//8, text="Record the clues in your journal to get bonus points and powerups.", fill="red", font="Gothic 15")
    canvas.create_text(app.width//2, 7 * app.height//8, text="If you shout for help, you might get a clue.", fill="red", font="Gothic 15")

def drawBonus(app, canvas):
    (item, row, col) = app.bonusItem
    (x0, y0, x1, y1) = getCellBounds(app, row, col)
    if item == "crucifix":
        drawCrucifix(app, canvas, x0, y0, x1, y1)
    elif item == "battery":
        drawBattery(app, canvas, x0, y0, x1, y1)
    else:
        drawSnack(app, canvas, x0, y0, x1, y1)

def drawCrucifix(app, canvas, x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_rectangle(midX-3, y0+10, midX+3, y1-10, width=0, fill="brown")
    canvas.create_rectangle(x0+20, y0+25, x1-20, y0+29, width=0, fill="brown")

def drawBattery(app, canvas, x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_rectangle(midX-25, midY - 10 , midX + 25, midY + 10, fill="green" )
    canvas.create_rectangle(midX+25, midY -5, midX+30, midY + 5, width=0, fill="gray")

def drawSnack(app, canvas, x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_oval(midX-15, midY-10, midX+15, midY+10, width=0, fill="orange")
    canvas.create_oval(midX-15, midY-10, midX+15, midY+5, width=0, fill="deep pink")
    canvas.create_oval(midX-10, midY-5, midX+10, midY+2, width=0, fill="black")

def drawClues(app, canvas):
    for (clue, row, col) in [app.firstClue, app.secondClue, app.thirdClue]:
        (x0, y0, x1, y1) = getCellBounds(app, row, col)
        if clue == "water":
            drawWater(app, canvas,x0, y0, x1, y1)
        elif clue == "blood splatter":
            drawBloodSplatter(app, canvas,x0, y0, x1, y1)
        elif clue == "ectoplasm":
            drawEctoplasm(app, canvas,x0, y0, x1, y1)
        elif clue == "freezing temps":
            drawFreezingTemps(app, canvas,x0, y0, x1, y1)
        elif clue == "writing":
            drawWriting(app, canvas,x0, y0, x1, y1)
        else:
            drawHandprint(app, canvas,x0, y0, x1, y1)

def drawHandprint(app, canvas,x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_oval(midX - 10, midY-12, midX+10, midY+12, width=0, fill="gray")
    canvas.create_oval(midX-20, midY+3, midX-14, midY,width=0, fill="gray" )
    canvas.create_oval(midX-12, midY-33, midX-9, midY-15, width=0, fill="gray")
    canvas.create_oval(midX-6, midY-33, midX-3, midY-18, width=0, fill="gray")
    canvas.create_oval(midX, midY-33, midX+3, midY-18, width=0, fill="gray")
    canvas.create_oval(midX+6, midY-30, midX+9, midY-16, width=0, fill="gray")

def drawWriting(app, canvas,x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_oval(midX - 20, midY-20, midX+20, midY+20, width=5, outline="white")
    y3 = round(20 * math.sin(144))
    y4 = round(20 * math.sin(306))
    x3 = round(20 * math.cos(162))
    x4 = round(20 * math.cos(18))
    canvas.create_line(midX, midY-20, midX-x4, midY-y4, width=3, fill="white")
    canvas.create_line(midX, midY-20, midX+x4, midY-y4, width=3, fill="white")
    canvas.create_line(midX+x4, midY+y3, midX-x4, midY-y4, width=3, fill="white")
    canvas.create_line(midX-x4, midY+y3, midX+x4, midY-y4, width=3, fill="white")
    canvas.create_line(midX-x4, midY+y3, midX+x4, midY+y3, width=3, fill="white")

def drawFreezingTemps(app, canvas,x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_oval(midX - 10, midY+7, midX+10, midY+27, fill = "gray")
    canvas.create_rectangle(midX-3,y0 + 15 ,midX+3, midY+10, width=0, fill="gray")
    canvas.create_oval(midX - 5, midY+12, midX+5, midY+22, fill = "red")
    canvas.create_rectangle(midX-1,midY,midX+1, midY+12, width=0, fill="red")
    
def drawBloodSplatter(app, canvas,x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_oval(midX-10, midY-10, midX+10, midY+10, width=0, fill="red3")
    canvas.create_oval(midX-25, midY-15, midX-10, midY, width=0, fill="red3")
    canvas.create_oval(midX-20, midY+15, midX, midY+20, width=0, fill="red3")

def drawEctoplasm(app, canvas,x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_oval(midX-10, midY-10, midX+10, midY+10, width=0, fill="lime")
    canvas.create_oval(midX-20, midY-8, midX+5, midY+5, width=0, fill="lime")
    canvas.create_oval(midX-8, midY+4, midX-2, midY+10, width=0, fill="lime")
    canvas.create_oval(midX+8, midY+5, midX+18, midY+10, width=0, fill="lime")

def drawWater(app, canvas,x0, y0, x1, y1):
    midX, midY = (x0+x1)//2, (y0+y1)//2
    canvas.create_oval(midX-10, midY-7, midX+10, midY+17, fill="deep sky blue")
    x = 10 * math.cos(math.pi/4) 
    y = 10 * math.sin(math.pi/4)
    canvas.create_polygon(midX-x-3, midY+2, midX+x+3, midY+2, midX, midY-15, width=0, fill="deep sky blue")

def drawGameOver(app, canvas):
    canvas.create_rectangle(0, 0, app.height, app.width, fill = "black")
    canvas.create_text(app.width//2, app.height//4, text="YOU DIED",fill="red", font="Gothic 60 bold")
    text = f'Total Score:{round(app.totalPoints)}'
    canvas.create_text(app.width//2, app.height//2, text=text, fill="red", font="Gothic 40 bold")
    canvas.create_text(app.width//2, 3*app.height//4, text="Press r to reset", fill="red", font="Gothic 40 bold")

def drawToastMessage(app, canvas, item):
    if item == "key":    
        text = f'{item} found. Now you can escape'
    elif item == "used":
        text = 'Crucifix used. Ghost scared away'
    elif item in {"crucifix", "snack", "battery"}:
        text = f'{item} found. Bonus applied'
    else: 
        text = f"{item} discovered. Mark it in your journal for points"

    if app.playerY < app.height//2:
        canvas.create_rectangle(0, 7 * app.height//8, app.width, app.height, fill="red")
        canvas.create_text(app.width//2, 15 * app.height//16, text=text, fill="black", font="Gothic 15 bold" )
    else: 
        canvas.create_rectangle(0, 0, app.width, app.height//8, fill="red")
        canvas.create_text(app.width//2, app.height//16, text=text, fill="black", font="Gothic 15 bold" )

def drawDoor(app, canvas):
    (x0, y0, x1, y1) = getCellBounds(app, app.rows - 1, app.cols - 1)
    canvas.create_rectangle(x0 + 20, y0+5, x1 - 20, y1-5, fill="brown")
    canvas.create_rectangle(x0 + 25, y0+10, x1 - 25, (y0 + y1)//2 - 8, fill="sienna4")
    canvas.create_oval(x1- 35, (y0 + y1)//2 - 5, x1 - 25,  (y0 + y1)//2 + 5, fill="gold")

def drawWinScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.height, app.width, fill = "black")
    canvas.create_text(app.width//2, app.height//4, text="YOU ESCAPED...FOR NOW",fill="red", font="Gothic 40 bold")
    text = f'Total Score:{round(app.totalPoints)}'
    canvas.create_text(app.width//2, app.height//2, text=text, fill="red", font="Gothic 40 bold")
    canvas.create_text(app.width//2, 3*app.height//4, text="Press r to play again", fill="red", font="Gothic 40 bold")

def drawFogOfWar(app, canvas):
    (pRow, pCol) = getCell(app, app.playerX, app.playerY)
    for row in range(app.rows):
        for col in range(app.cols):
            if not ((abs(row - pRow) <= app.lightDistance) and \
                (abs(col - pCol) <= app.lightDistance)):
                (x0, y0, x1, y1) = getCellBounds(app, row, col)
                canvas.create_rectangle(x0, y0, x1, y1, width=0, fill="gray8")


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
    drawBonus(app, canvas)
    drawClues(app, canvas)
    if app.gotKey:
        drawDoor(app, canvas)
    #drawFogOfWar(app, canvas)
    if app.keyToastShowing:
        drawToastMessage(app, canvas, "key")
    if app.bonusToastShowing:
        drawToastMessage(app, canvas, app.bonusItem[0])
    if app.crucifixToastShowing:
        drawToastMessage(app, canvas, "used")
    if app.clue1ToastShowing:
        drawToastMessage(app, canvas, app.currentClues[0][0])
    if app.clue2ToastShowing:
        drawToastMessage(app, canvas, app.currentClues[1][0])
    if app.clue3ToastShowing:
        drawToastMessage(app, canvas, app.currentClues[2][0])
    if app.journalVisible:
        drawJournalScreen(app, canvas)
        drawTextBoxText(app, canvas)
    if app.titleScreen:
        drawTitle(app, canvas)
    if app.helpScreen:
        drawHelpScreen(app, canvas)
    if app.gameOver:
        drawGameOver(app, canvas)
    if app.win:
        drawWinScreen(app, canvas)

runApp(width=800, height=800)

if __name__ == '__main__':
    main()