import pygame

from random import choice

# Constants
RES = WIDTH, HEIGHT = 1352, 752
W = 25
COLS = WIDTH // W
ROWS = HEIGHT // W

# Colors
LIGHT_GREEN = pygame.Color('lightgreen')
GREEN = pygame.Color('green')
RED = pygame.Color('red')
PURPLE = pygame.Color('purple')
BLACK = pygame.Color('black')
YELLOW = pygame.Color('yellow')
BLUE = pygame.Color('blue')
GREY = pygame.Color('grey')
DARK_ORANGE = pygame.Color('darkorange')


pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock()


def getClickPos(pos):
    y, x = pos
    return y // W, x // W


def findIndex(x, y):
    return x + y * COLS


def checkCell(x, y):
    if x < 0 or x > COLS - 1 or y < 0 or y > ROWS - 1:
        return False
    return gridCells[findIndex(x, y)]


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bot': True, 'left': True}
        self.visitedFromGen = False

        # used for pathfinding
        self.start = False
        self.end = False
        self.queued = False
        self.visitedFromPathfinding = False
        self.neighbors = []
        self.prior = None

    def setNeighbors(self):
        y, x = self.y, self.x
        if y > 0:
            self.neighbors.append(gridCells[findIndex(x, y - 1)])
        if y < ROWS - 1:
            self.neighbors.append(gridCells[findIndex(x, y + 1)])
        if x > 0:
            self.neighbors.append(gridCells[findIndex(x - 1, y)])
        if x < COLS - 1:
            self.neighbors.append(gridCells[findIndex(x + 1, y)])

    def makeStart(self):
        self.start = True

    def makeEnd(self):
        self.end = True

    def drawCurrentCell(self):
        x = self.x * W
        y = self.y * W
        pygame.draw.rect(sc, PURPLE, (x + 2, y + 2, W - 2, W - 2))

    def draw(self):
        x = self.x * W
        y = self.y * W

        if self.visitedFromGen:
            pygame.draw.rect(sc, BLACK, (x, y, W, W))

        if self.queued:
            pygame.draw.rect(sc, BLUE, (x, y, W, W))

        if self.visitedFromPathfinding:
            pygame.draw.rect(sc, YELLOW, (x, y, W, W))

        if self in path:
            pygame.draw.rect(sc, GREY, (x, y, W, W))

        if self.start:
            pygame.draw.rect(sc, GREEN, (x, y, W, W))
        if self.end:
            pygame.draw.rect(sc, RED, (x, y, W, W))

        if self.walls['top']:
            pygame.draw.line(sc, DARK_ORANGE, (x, y), (x + W, y), 2)
        if self.walls['right']:
            pygame.draw.line(sc, DARK_ORANGE, (x + W, y), (x + W, y + W), 2)
        if self.walls['bot']:
            pygame.draw.line(sc, DARK_ORANGE, (x + W, y + W), (x, y + W), 2)
        if self.walls['left']:
            pygame.draw.line(sc, DARK_ORANGE, (x, y + W), (x, y), 2)

    def checkNeighbors(self):
        neighbors = []

        top = checkCell(self.x, self.y - 1)
        right = checkCell(self.x + 1, self.y)
        bot = checkCell(self.x, self.y + 1)
        left = checkCell(self.x - 1, self.y)

        if top and not top.visitedFromGen:
            neighbors.append(top)
        if right and not right.visitedFromGen:
            neighbors.append(right)
        if bot and not bot.visitedFromGen:
            neighbors.append(bot)
        if left and not left.visitedFromGen:
            neighbors.append(left)

        return choice(neighbors) if neighbors else False


def removeWalls(currentWall, nextWall):
    dx = currentWall.x - nextWall.x
    dy = currentWall.y - nextWall.y

    if dx == 1:
        currentWall.walls['left'] = False
        nextWall.walls['right'] = False
    elif dx == -1:
        currentWall.walls['right'] = False
        nextWall.walls['left'] = False

    if dy == 1:
        currentWall.walls['top'] = False
        nextWall.walls['bot'] = False
    elif dy == -1:
        currentWall.walls['bot'] = False
        nextWall.walls['top'] = False


def drawMaze():
    sc.fill(LIGHT_GREEN)
    for cell in gridCells:
        cell.draw()
    pygame.display.flip()


def draw_maze():
    currentCell.visitedFromGen = True
    if not done:
        currentCell.drawCurrentCell()

    pygame.display.flip()


gridCells = []
for row in range(ROWS):
    for col in range(COLS):
        gridCells.append(Cell(col, row))

currentCell = []
stack = []
queue = []
path = []

for i in range(len(gridCells)):
    gridCells[i].setNeighbors()

run = True
started = False
selectedPt = False
done = False
beginPathfinding = False
searching = True
startCell = None
endCell = None

start = []
end = []

while run:
    drawMaze()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        if started:
            continue

        if pygame.mouse.get_pressed()[0]:  # left click
            if not currentCell:
                pos = pygame.mouse.get_pos()
                row, col = getClickPos(pos)
                currentCell = gridCells[findIndex(row, col)]
                selectedPt = True
            elif done and not start:
                start = pygame.mouse.get_pos()
                row, col = getClickPos(start)

                startCell = gridCells[findIndex(row, col)]
                startCell.makeStart()
                startCell.visitedFromPathfinding = True
                print("starting cell placed")
                queue.append(startCell)

            elif done and not end and getClickPos(pygame.mouse.get_pos()) != getClickPos(start):
                end = pygame.mouse.get_pos()
                row, col = getClickPos(end)
                endCell = gridCells[findIndex(row, col)]
                endCell.makeEnd()
                print("target cell placed")
                beginPathfinding = True

    if not selectedPt:
        continue

    draw_maze()

    nextCell = currentCell.checkNeighbors()
    if nextCell:
        nextCell.visitedFromGen = True
        stack.append(currentCell)
        removeWalls(currentCell, nextCell)
        currentCell = nextCell
    elif stack:
        currentCell = stack.pop()
    elif beginPathfinding:

        if len(queue) > 0 and searching:
            currentCell = queue.pop(0)
            currentCell.visitedFromPathfinding = True
            if currentCell == endCell:
                searching = False
                print("target cell found")
                while currentCell.prior != startCell:
                    path.append(currentCell.prior)
                    currentCell = currentCell.prior
            else:

                for i in range(len(currentCell.neighbors)):

                    dx = currentCell.x - currentCell.neighbors[i].x
                    dy = currentCell.y - currentCell.neighbors[i].y

                    if not currentCell.neighbors[i].queued:
                        if dy == 1:
                            if not currentCell.walls['top']:
                                currentCell.neighbors[i].queued = True
                                currentCell.neighbors[i].prior = currentCell
                                queue.append(currentCell.neighbors[i])
                        elif dx == -1:
                            if not currentCell.walls['right']:
                                currentCell.neighbors[i].queued = True
                                currentCell.neighbors[i].prior = currentCell
                                queue.append(currentCell.neighbors[i])
                        elif dy == -1:
                            if not currentCell.walls['bot']:
                                currentCell.neighbors[i].queued = True
                                currentCell.neighbors[i].prior = currentCell
                                queue.append(currentCell.neighbors[i])
                        elif dx == 1:
                            if not currentCell.walls['left']:
                                currentCell.neighbors[i].queued = True
                                currentCell.neighbors[i].prior = currentCell
                                queue.append(currentCell.neighbors[i])
    else:
        done = True
        print("Done")
    # clock.tick(100)
