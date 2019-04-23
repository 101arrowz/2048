#!/usr/bin/env python
from __future__ import print_function
import random, sys, os, pickle, time, math
sortCount = 0
frameCount = []
if int(str(sys.version_info[0])+str(sys.version_info[1])) < 27:
    if os.system("python3 2048.py > "+os.devnull+" 2>&1"):
        print("Please use Python 2.7 or later to run 2048!")
        sys.exit(1)
    else:
        sys.exit(0)
with open(os.devnull, 'w') as f:
    oldstdout = sys.stdout
    sys.stdout = f
    try:
        import pygame
    except ImportError:
        sys.stdout = oldstdout
        if sys.version_info[0] < 3:
            if os.system(" ".join(["python3 2048.py"]+sys.argv[1:])+" > "+os.devnull+" 2>&1"):
                pass
            else:
                sys.exit(0)
        if sys.platform == "darwin" and sys.version_info[0] < 3:
            print()
            print("You are likely using the python installation that comes bundled with macOS.")
            print("To use 2048, please run the following command in Terminal:\n")
            print("sudo -H pip2 install pygame\n")
            print("Don't worry if it throws an EnvironmentError.")
            print("If you don't mind the hassle, it is recommended to install Python 3 instead of doing the above. Do `python3 2048.py` once you have.")
            print()
        elif "linux" in sys.platform or sys.platform == "darwin":
            print()
            print("Please install pygame to run 2048 with the command:\n")
            print("pip install pygame\n")
            print("If you have both Python 2 and 3 installed, this script will default to Python 3, so use pip3 instead of pip.")
            print()
        elif sys.platform == "win32":
            print()
            print("Please install pygame to run 2048 with the command:\n")
            print("pip install pygame\n")
            print()
        else:
            print()
            print("Please use pip to install pygame!")
            print()
        sys.exit(1)
    sys.stdout = oldstdout
if not os.path.exists(os.path.join(".2048data", "ClearSans-Regular.ttf")):
    os.system("mkdir .2048data > "+os.devnull+" 2>&1")
    if sys.platform == "win32":
        os.system("attrib +h .2048data")
    print("Attempting to download font... Either this is the first run or the game directory was not found.")
    if os.system("ping "+("-n" if sys.platform == "win32" else "-c")+" 1 github.com > "+os.devnull+" 2>&1"):
        print("Either GitHub is down (unlikely) or you are not connected to the internet. Connect to the internet next time to download the font. You will not need internet connectivity after that. Exiting...")
        sys.exit()
    else:
        os.system(("powershell.exe (new-object System.Net.WebClient).DownloadFile('https://raw.githubusercontent.com/101arrowz/2048/master/.2048data/ClearSans-Regular.ttf','"+os.path.join('.', '.2048data', 'ClearSans-Regular.ttf')+"')" if sys.platform == "win32" else "curl -L -o "+os.path.join(".2048data", "ClearSans-Regular.ttf")+" 'https://raw.githubusercontent.com/101arrowz/2048/master/.2048data/ClearSans-Regular.ttf'")+" > "+os.devnull+" 2>&1")
    print("Font successfully downloaded!")
# ROUNDED RECTANGLE CODE https://www.pygame.org/project-AAfilledRoundedRect-2349-.html

def AAfilledRoundedRect(surface,color,rect,radius=0.4):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = pygame.Rect(rect)
    color        = pygame.Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = pygame.Surface(rect.size,pygame.SRCALPHA)

    circle       = pygame.Surface([min(rect.size)*3]*2,pygame.SRCALPHA)
    pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)

# END ROUNDED RECTANGLE CODE

class Tile:
    def __init__(self, value=0):
        self.oldValue = value
        self.value = value
        self.linkCount = 0
        self.new = 0
        self.merged = False
        self.color = (205,192,180)
        self.textColor = (119, 110, 101)
    def getColor(self):
        if self.value == 0:
            self.color = (205,192,180)
        elif self.value == 2:
            self.color = (238,228,218)
        elif self.value == 4:
            self.color = (237,224,200)
        elif self.value == 8:
            self.color = (242, 177, 121)
        elif self.value == 16:
            self.color = (245, 149, 99)
        elif self.value == 32:
            self.color = (246, 124, 95)
        elif self.value == 64:
            self.color = (246, 94, 59)
        elif self.value == 128:
            self.color = (237, 207, 114)
        elif self.value == 256:
            self.color = (237, 204, 97)
        elif self.value == 512:
            self.color = (237, 200, 80)
        elif self.value == 1024:
            self.color = (237, 197, 63)
        elif self.value == 2048:
            self.color = (237, 194, 46)
        else:
            self.color = (60, 58, 50)
        return self.color
    def getTextColor(self):
        if self.value in [0, 2, 4]:
            self.textColor = (119, 110, 101)
        else:
            self.textColor = (249, 246, 242)
        return self.textColor
    def setDiff(self, coords):
        try:
            self.diff = (coords[0]-self.coords[0], coords[1]-self.coords[1])
            self.coords = coords
        except:
            self.coords = coords
            self.diff = (0, 0)
def updateDisplay(screen, square=False, frame=0):
    global objects, frameCount
    w, h = pygame.display.get_surface().get_size()
    size = int(w/10)
    boardw = boardh = int(w*3/4)
    padl = padb = int(w*1/8)
    if square:
        padb += int(size/2)
    else:
        padb += int(size*0.8)
    padr = int(padl+size/2)
    padt = h-padb-boardh
    if square:
        padb += int(size*0.48)
    font = pygame.font.Font(os.path.join(".2048data", "ClearSans-Regular.ttf"), size)
    screen.fill((250,248,239))
    border = 32
    curve = lambda x, n=1: ((math.cos(x*3.1416*n)-1)/2.0)*-1 if x < 1/float(n) else 1
    if frame:
        frameCountTMP = list(range(frame))
        frameCount = []
        for x in frameCountTMP:
            frameCount.append(curve(x/float(frame)))
        # Add properties to each tile
        for xval in enumerate(range(padl, w-padr+1, int((w-padr-padl)/3))):
            for yval in enumerate(range(padt, h-padb+1, int((h-padt-padb)/3))):
                tile = objects[yval[0]][xval[0]]
                tile.setDiff((xval[1], yval[1]))
                if tile.new:
                    tile.new -= 1
                if tile.linkCount:
                    tile.linkCount -= 1
        return
        # TODO: reset as if framecount is empty again
    if frameCount:
        for xval in enumerate(range(padl, w-padr+1, int((w-padr-padl)/3))):
            for yval in enumerate(range(padt, h-padb+1, int((h-padt-padb)/3))):
                pygame.draw.rect(screen, (187,173,160), (xval[1]-int((w-padr-padl)/6)+int(size/4), yval[1]-int((h-padt-padb)/6)+int(size/2), int((w-padr-padl)/3), int((h-padt-padb)/3)))
                AAfilledRoundedRect(screen, (205, 192, 180), (xval[1]-int((w-padr-padl)/6)+int(size/4)+int(border/4), yval[1]-int((h-padt-padb)/6)+int(size/2)+int(border/4), int((w-padr-padl)/3)-int(border/2), int((h-padt-padb)/3)-int(border/2)), 0.1)
        for xval in enumerate(range(padl, w-padr+1, int((w-padr-padl)/3))):
            for yval in enumerate(range(padt, h-padb+1, int((h-padt-padb)/3))):
                tile = objects[yval[0]][xval[0]]
                tile.merged = False
                mult = frameCount[-1]
                if len(frameCount) < 2:
                    tile.linkCount = 0
                if tile.linkCount:
                    tile.value = int(tile.value/2.0)
                    ltile = tile.link
                    ltile.diff = (tile.coords[0]-ltile.oldCoords[0], tile.coords[1]-ltile.oldCoords[1])
                    offset = (int(ltile.diff[0]*mult), int(ltile.diff[1]*mult))
                    AAfilledRoundedRect(screen, tile.getColor(), (xval[1]-int((w-padr-padl)/6)+int(size/4)+int(border/4)-offset[0], yval[1]-int((h-padt-padb)/6)+int(size/2)+int(border/4)-offset[1], int((w-padr-padl)/3)-int(border/2), int((h-padt-padb)/3)-int(border/2)), 0.1)
                    if len(str(tile.value)) < 4:
                        screen.blit(font.render(str(tile.value) if tile.value != 0 else "", True, tile.getTextColor()), (xval[1]-int(((len(str(tile.value))-1.0)/3.0)*size)-offset[0], yval[1]-int(size/4.0)-offset[1]))
                    else:
                        smallFontSize = int(size*3.0/len(str(tile.value)))
                        smallFont = pygame.font.Font(os.path.join(".2048data", "ClearSans-Regular.ttf"), smallFontSize)
                        screen.blit(smallFont.render(str(tile.value) if tile.value != 0 else "", True, tile.getTextColor()), (xval[1]-int(((len(str(tile.value))-1)*(0.273 if square else 0.285))*smallFontSize)-offset[0], yval[1]-offset[1]))
                if tile.new:
                    color = tile.getColor()
                    textColor = tile.getTextColor()
                    fadespeed = 0.3
                    tr = lambda alpha, rgb: tuple((int((1-alpha)*((205, 192, 180)[n])+alpha*rgb[n]) for n in range(3)))
                    mult = (10*fadespeed)**(-10*fadespeed*mult)
##                    textmult = max([((mult+0.414)**2)-1, 0])
                    AAfilledRoundedRect(screen, tr(mult, color), (xval[1]-int((w-padr-padl)/6)+int(size/4)+int(border/4), yval[1]-int((h-padt-padb)/6)+int(size/2)+int(border/4), int((w-padr-padl)/3)-int(border/2), int((h-padt-padb)/3)-int(border/2)), 0.1)
                    screen.blit(font.render(str(tile.value), True, tr(mult, textColor)), (xval[1]-int(((len(str(tile.value))-1.0)/3.0)*size), yval[1]-int(size/4.0)))
                    continue
                offset = (int(tile.diff[0]*mult), int(tile.diff[1]*mult))
                if tile.value:
                    AAfilledRoundedRect(screen, tile.getColor(), (xval[1]-int((w-padr-padl)/6)+int(size/4)+int(border/4)-offset[0], yval[1]-int((h-padt-padb)/6)+int(size/2)+int(border/4)-offset[1], int((w-padr-padl)/3)-int(border/2), int((h-padt-padb)/3)-int(border/2)), 0.1)
                if len(str(tile.value)) < 4:
                    screen.blit(font.render(str(tile.value) if tile.value != 0 else "", True, tile.getTextColor()), (xval[1]-int(((len(str(tile.value))-1.0)/3.0)*size)-offset[0], yval[1]-int(size/4.0)-offset[1]))
                else:
                    smallFontSize = int(size*3.0/len(str(tile.value)))
                    smallFont = pygame.font.Font(os.path.join(".2048data", "ClearSans-Regular.ttf"), smallFontSize)
                    screen.blit(smallFont.render(str(tile.value) if tile.value != 0 else "", True, tile.getTextColor()), (xval[1]-int(((len(str(tile.value))-1)*(0.273 if square else 0.285))*smallFontSize)-offset[0], yval[1]-offset[1]))
                if tile.linkCount:
                    tile.value = int(tile.value*2.0)
        pygame.display.update()
        frameCount.pop(-1)
def itemSort(item):
    global sortCount
    sortCount += 1
    if item.value == 0:
        return sortCount + 4
    else:
        return sortCount
def returnFormattedObjects(skipzeros=True, reset=False, spacing=3):
    global objects
    returnstr = ""
    for row in objects:
        for tile in row:
            if skipzeros and not tile.value:
                returnstr += " "+("  "*spacing)
            else:
                returnstr += str(tile.value)+(" "*(max([(2*spacing)-len(str(tile.value))+1, 1])))
            if reset:
                tile.merged = False
        returnstr += "\n"*spacing
    return returnstr
def itemSortRev(item):
    global sortCount
    sortCount += 1
    if item.value == 0:
        return sortCount - 4
    else:
        return sortCount
def newTile(easy=False):
    choices = []
    for row in objects:
        for tile in row:
            if tile.value == 0:
                choices.append(tile)
    try:
        if random.random() < (0.4+(len(choices)*0.04) if easy else 1):
            tile = random.choice(choices)
            tile.value = random.choice([2 for x in range(9)]+[4])
            tile.new = 2
    except:
        return False
    return True
def merge(dtile, stile):
    if (dtile.value == stile.value != 0) and (dtile.merged == stile.merged == False):
        dtile.merged = Tile(value=stile.value)
        stile.oldValue = stile.value
        stile.value = 0
        dtile.oldValue = dtile.value
        dtile.value *= 2
        dtile.link = stile
        dtile.linkCount = 2
        stile.oldCoords = stile.coords
    if (stile.value != dtile.value == 0):
        dtile.value = stile.value
        stile.value = 0
def doMerges(key, easy=False):
    global objects
    objectsoriginal = [[Tile(value=tile.value) for tile in row] for row in objects]
    if key in [pygame.K_RIGHT, pygame.K_d, "right"]:
        objectscopy = []
        for row in objects:
            row.sort(key=itemSortRev)
            merge(row[-1], row[-2])
            row.sort(key=itemSortRev)
            merge(row[-2], row[-3])
            row.sort(key=itemSortRev)
            merge(row[-3], row[-4])
            row.sort(key=itemSortRev)
            objectscopy.append(row)
        objects = objectscopy
    elif key in [pygame.K_LEFT, pygame.K_a, "left"]:
        objectscopy = []
        for row in objects:
            row.sort(key=itemSort)
            merge(row[0], row[1])
            row.sort(key=itemSort)
            merge(row[1], row[2])
            row.sort(key=itemSort)
            merge(row[2], row[3])
            row.sort(key=itemSort)
            objectscopy.append(row)
        objects = objectscopy
    elif key in [pygame.K_UP, pygame.K_w, "up"]:
        rows = []
        [rows.append([column[i] for column in objects]) for i in range(4)]
        for row in rows:
            row.sort(key=itemSort)
            merge(row[0], row[1])
            row.sort(key=itemSort)
            merge(row[1], row[2])
            row.sort(key=itemSort)
            merge(row[2], row[3])
            row.sort(key=itemSort)
        objects = [([row[i] for row in rows]) for i in range(4)]
    elif key in [pygame.K_DOWN, pygame.K_s, "down"]:
        rows = []
        [rows.append([column[i] for column in objects]) for i in range(4)]
        for row in rows:
            row.sort(key=itemSortRev)
            merge(row[-1], row[-2])
            row.sort(key=itemSortRev)
            merge(row[-2], row[-3])
            row.sort(key=itemSortRev)
            merge(row[-3], row[-4])
            row.sort(key=itemSortRev)
        objects = [([row[i] for row in rows]) for i in range(4)]
    else:
        return "nokey"
    if [[tile.value for tile in row] for row in objects] != [[tile.value for tile in row] for row in objectsoriginal]:
        if newTile(easy=easy):
            return True
        else:
            return False
    else:
        return "illegal"
def checkGO():
    global objects
    for row in enumerate(objects):
        for tile in enumerate(row[1]):
            value = tile[1].value
            if value == 0:
                return False
            coords = (row[0], tile[0])
            try:
                if objects[coords[0]-1][coords[1]].value == value and coords[0] > 0:
                    return False
            except:
                pass
            try:
                if objects[coords[0]+1][coords[1]].value == value:
                    return False
            except:
                pass
            try:
                if objects[coords[0]][coords[1]-1].value == value and coords[1] > 0:
                    return False
            except:
                pass
            try:
                if objects[coords[0]][coords[1]+1].value == value:
                    return False
            except:
                pass
    return True

objects = [[Tile() for i1 in range(4)] for i2 in range(4)]
random.choice(random.choice(objects)).value = 2


def startGame(FPS=60, text=False, easy=False, width=400, square=False, load=None):
    global objects
    if load:
        objects = load
    playing = True
    height = int(width*1.5)
    pygame.init()
    d = pygame.display.set_mode((width, height))
    pygame.display.set_caption('2048')
    clock = pygame.time.Clock()
    updateDisplay(d, square=square, frame=1)
    if text:
        os.system("clear")
        print(returnFormattedObjects(spacing=2))
    while playing:
        printout = False
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                playing = False
                with open(os.path.join(".2048data", "game.2048"), 'wb') as f:
                    pickle.dump(objects, f)
            if e.type == pygame.KEYDOWN:
                cont = doMerges(e.key, easy=easy)
                if cont:
                    if cont in ["nokey", "illegal"]:
                        printout = False
                    else:
                        printout = True
                    if checkGO():
                        playing = False
                        printout = False
                        updateDisplay(d, square=square, frame=int(FPS/6))
                        for frame in range(int(FPS/6)):
                            updateDisplay(d, square=square)
                        GOfont = pygame.font.Font(os.path.join(".2048data", "ClearSans-Regular.ttf"), int(width/12.0))
                        d.blit(GOfont.render("Game Over!", True, (119, 110, 101)), (int(width/2.0)-2.6*int(width/12.0), int(height-width)-int(width/4.0)))
                        with open(os.path.join(".2048data", "game.2048"), 'wb') as f:
                            pickle.dump([], f)
                        for frame in range(5*FPS):
                            pygame.display.update()
                            clock.tick(FPS)
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                else:
                    playing = False
                    printout = False
        if printout:
            if text:
                os.system("cls" if sys.platform == "win32" else "clear")
                print(returnFormattedObjects(reset=True, spacing=2))
            updateDisplay(d, square=square, frame=int(FPS/8))
        updateDisplay(d, square=square)
    pygame.quit()
def addArgs():
    import argparse
    global objects
    try:
        if sys.platform == "darwin":
            parser = argparse.ArgumentParser(description='Play 2048!') #, prog='open 2048.app')
            resline = os.popen("system_profiler SPDisplaysDataType | grep Resolution | awk '/Resolution/{print $2, $3, $4}'").read().split("x")
            w = int(resline[0])
            h = int(resline[1])
        elif sys.platform == "win32":
            parser = argparse.ArgumentParser(description='Play 2048!') #, prog='start 2048.exe')
            reslines = [line for line in os.popen("wmic path Win32_VideoController get CurrentVerticalResolution,CurrentHorizontalResolution /format:value").read().split('\n') if line]
            w = int(reslines[0].split("=")[-1])
            h = int(reslines[1].split("=")[-1])
        elif "linux" in sys.platform.lower():
            parser = argparse.ArgumentParser(description='Play 2048!') #, prog='./2048')
            resline = os.popen("xdpyinfo | awk '/dimensions/{print $2}'").read().split('x')
            w = int(resline[0])
            h = int(resline[1])
        else:
            parser = argparse.ArgumentParser(description='Play 2048!')
            w = 400
            h = 600
    except:
        w = 400
        h = 600
    maxw = int(min([w, h*2/3.0])*11/12.0)
    try:
        with open(os.path.join(".2048data", "settings.2048"), 'rb') as f:
            argsFromFile = pickle.load(f)
    except:
        argsFromFile = {'FPS': 60, 'width': int(maxw*2/3.0), 'easy': False, 'text': False, 'square': False, 'newgame': False, 'reset': False, 'store': False}
    parser.add_argument('-FPS', metavar=""+str(argsFromFile["FPS"])+"", type=int,
                       help='Framerate at which the game runs')
    parser.add_argument('-width', metavar=""+str(argsFromFile["width"])+"", type=int,
                       help='width of window in pixels (height is dependent upon width)')
    parser.add_argument('--easy', action='store_true',
                       help='New tiles are less likely to spawn when the board is nearly full.')
    parser.add_argument('--text', action='store_true',
                       help='Text mode (will not disable graphics)')
    parser.add_argument('--square', action='store_true',
                       help='Perfectly square tiles')
    parser.add_argument('--newgame', action='store_true',
                       help='Completely reset board.')
    parser.add_argument('--reset', action='store_true',
                       help='Completely reset saved settings.')
    parser.add_argument('--store', action='store_true',
                       help='Save settings - next time you run this game, 2048 will use the settings you just provided.  Be warned - if you use this with --newgame, each time you reopen 2048, your game will reset!')
    args = vars(parser.parse_args())
    if args["reset"]:
        args["reset"] = False
        os.system(("del " if sys.platform == "win32" else "rm ")+os.path.join(".2048data", "settings.2048")+" > "+os.devnull+" 2>&1")
        argsFromFile = {'FPS': 60, 'width': int(maxw*2/3.0), 'easy': False, 'text': False, 'square': False, 'newgame': False, 'reset': False, 'store': False}
    if args == {'FPS': None, 'width': None, 'easy': False, 'text': False, 'square': False, 'newgame': False, 'reset': False, 'store': False}:
        args = argsFromFile
    if args["FPS"] == None:
        args["FPS"] = argsFromFile["FPS"]
    if args["width"] == None:
        args["width"] = argsFromFile["width"]
    if args["newgame"]:
        with open(os.path.join(".2048data", "game.2048"), 'wb') as f:
            pickle.dump(objects, f)
    if args["width"] > maxw:
        args["width"] = maxw
    if args["store"]:
        args["store"] = False
        with open(os.path.join(".2048data", "settings.2048"), 'wb') as f:
            pickle.dump(args, f)
    return args
def loadGame():
    global objects
    try:
        with open(os.path.join(".2048data", "game.2048"), 'rb') as f:
            game = pickle.load(f)
    except:
        with open(os.path.join(".2048data", "game.2048"), 'wb') as f:
            pickle.dump(objects, f)
        game=objects
    return game
if __name__ == "__main__":
    args = addArgs()
    game = loadGame()
    startGame(FPS=args["FPS"], text=args["text"], easy=args["easy"], width=args["width"], square=args["square"], load=game)
