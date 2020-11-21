from cmu_112_graphics import *
import random
import time
import dataclasses

#######################################################
# 15-112 Functions
#######################################################

# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
# Gets row and col based on x, y coords
def getCell(app, x, y):
    row = (y - app.dy - app.margin) // app.cellSize 
    col = (x - app.dx - app.margin) // app.cellSize 
    return (int(row), int(col))

# Returns bounds to make a grid given row, col
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#exampleGrids
def getCellBounds(app, row, col):
    cellWidth = 100
    cellHeight = 100
    x0 = app.margin + (col * app.cellSize) + app.dx
    x1 = app.margin + ((col + 1) * app.cellSize) + app.dx
    y0 = app.margin + (row * app.cellSize) + app.dy
    y1 = app.margin + ((row + 1)* app.cellSize) + app.dy
    return (x0, y0, x1, y1)

# Makes a 2-d list
# https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html
def make2dList(rows, cols):
    return [ ([False] * cols) for row in range(rows) ]

########################################################
# Helper Functions
########################################################

# Makes maze recursively with backtracking
def makeMaze(app, height, width):
    visitedBlocks = make2dlist(width)


########################################################
# Data Classes
########################################################



########################################################
# App stuff
########################################################

def appStarted(app):
    app.journalVisible = False
    app.journalEntry = False

    app.clues = []
    app.text1= "Start typing..."

def timerFired(app):
    pass

def keyPressed(app, event):
    if event.key == "j" and not app.journalEntry:
        app.journalVisible = not app.journalVisible
    if app.journalEntry:
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


def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.height, app.width, fill = "blue")
    if app.journalVisible:
        drawJournalScreen(app, canvas)
    if app.journalEntry:
        drawTextBoxText(app, canvas)


runApp(width=800, height=800)

if __name__ == '__main__':
    main()