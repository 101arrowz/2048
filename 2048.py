#!/usr/bin/env python
from __future__ import print_function
import random, sys, os, json, time, math
os.chdir(os.path.abspath(os.path.dirname(__file__)))
sortCount = 0
score = 0
oldScore = 0
scoreUpd = 1
frameCount = []
if int(str(sys.version_info[0])+str(sys.version_info[1])) < 27:
    if (True if sys.platform == 'win32' else (os.system('python3 -c "" 2>&1'))):
        print("Please use Python 2.7 or later to run 2048!")
        sys.exit(1)
    else:
        os.system(" ".join(["python3 2048.py"]+sys.argv[1:]))
        sys.exit(0)
with open(os.devnull, 'w') as f:
    oldstdout = sys.stdout
    sys.stdout = f
    try:
        import pygame
    except ImportError:
        sys.stdout = oldstdout
        if sys.version_info[0] < 3:
            if (True if sys.platform == 'win32' else (os.system('python3 -c "" > /dev/null 2>&1'))):
                pass
            else:
                os.system(" ".join(["python3 2048.py"]+sys.argv[1:]))
                sys.exit(0)
        if sys.platform == "darwin" and sys.version_info[0] < 3:
            ver = int(os.popen('defaults read loginwindow SystemVersionStampAsString').read().split('.')[1])
            if ver >= 14:
                print()
                print("As of May 2019, macOS Mojave 10.14 and up do not support pygame on Python 2 due to an issue with the new Dark/Light mode settings. Therefore, you must install Python 3 to run 2048.\n")
                print("Please download your preferred version of Python 3 from https://www.python.org/downloads/\n")
                print("It may be easier to install Python 3.6.8 by running the following command from Terminal:\n")
                print("curl -o ~/Downloads/python-3.6.8.pkg https://www.python.org/ftp/python/3.6.8/python-3.6.8-macosx10."+('6' if ver <= 6 else '9')+".pkg && sudo installer -pkg ~/Downloads/python-3.6.8.pkg -target / && mv ~/Downloads/python-3.6.8.pkg ~/.Trash\n")
                print("Once you have done that, run the following command in Terminal:\n")
                print("curl https://bootstrap.pypa.io/get-pip.py | sudo -H python3 && sudo -H pip3 install pygame\n")
                print("After that, you should be able to play 2048!")
                print()
            else:
                print()
                print("You are likely using the python installation that comes bundled with macOS.")
                print("To use 2048, please run the following command in Terminal:\n")
                print("curl https://bootstrap.pypa.io/get-pip.py | sudo -H python && sudo -H pip install pygame\n")
                print("Don't worry if it throws an EnvironmentError.")
                print("If you don't mind the hassle, it is recommended to install Python 3 instead of doing the above. Do `python3 2048.py` once you have.")
                print()
        elif "linux" in sys.platform or sys.platform == "darwin":
            print()
            print("Please install pygame to run 2048 with the command:\n")
            print("curl https://bootstrap.pypa.io/get-pip.py | sudo -H python"+("3" if sys.version_info[0] == 3 else "")+" && sudo -H pip"+("3" if sys.version_info[0] == 3 else "")+" install pygame")
            print()
        elif sys.platform == "win32":
            print()
            print("Please install pygame to run 2048 with the command:\n")
            print("pip install pygame\n")
            print("If necessary, install pip by running the python script at https://bootstrap.pypa.io/get-pip.py")
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
        sys.exit(1)
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
    colors = {0:(205,192,180),1:(221,210,199),2:(238,228,218),4:(237,224,200),8:(242, 177, 121),16:(245, 149, 99),32:(246, 124, 95),64:(246, 94, 59),128:(237, 207, 114),256:(237, 204, 97),512:(237, 200, 80),1024:(237, 197, 63),2048:(237, 194, 46)}
    def __init__(self, value=0):
        self.oldValue = value
        self.value = value
        self.linkCount = 0
        self.new = 0
        self.merged = False
        self.color = (205,192,180)
        self.textColor = (119, 110, 101)
    def getColor(self):
        if self.value in Tile.colors or self.value > 2048:
            self.color = Tile.colors[self.value] if self.value in Tile.colors else (60, 58, 50)
        else:
            for p in range(11):
                if 2**p <= self.value < 2**(p+1):
                    break
            self.color = tuple(int(((self.value-2**p)*Tile.colors[2**p][n]+(2**(p+1)-self.value)*Tile.colors[2**(p+1)][n])/float(2**p)) for n in range(3))
        return self.color
    def getTextColor(self):
        if self.value < 8:
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
    global objects, frameCount, score, oldScore, scoreUpd
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
        if scoreUpd:
            scoreUpd -= 1
        else:
            oldScore = score
        return
        # TODO: reset as if framecount is empty again
    if frameCount:
        tr = lambda alpha, rgb, bg=(205, 192, 180): tuple((int((1-alpha)*(bg[n])+alpha*rgb[n]) for n in range(3)))
        scoreFont = pygame.font.Font(os.path.join(".2048data", "ClearSans-Regular.ttf"), int(size/2.0))
        scoreMult = frameCount[-1]
        screen.blit(scoreFont.render("Score: "+str(int(score-scoreMult*(score-oldScore))), True, (119, 110, 101)), (int(w/2.0)-int(size*(len(str(score))+7)/8.0), int(h-w)-int(w/4.0)+1.2*size))
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
def newTile(difficulty=2):
    choices = []
    for row in objects:
        for tile in row:
            if tile.value == 0:
                choices.append(tile)
    try:
        if random.random() < (0.4+(len(choices)*0.04) if difficulty == 1 else 1):
            tile = random.choice(choices)
            tile.value = random.choice(9*[2]+[4]+(9*[3]+[6] if difficulty == 3 else []))
            tile.new = 2
    except:
        return False
    return True
def merge(dtile, stile):
    global score, scoreUpd, oldScore
    if (dtile.value == stile.value != 0) and (dtile.merged == stile.merged == False):
        dtile.merged = True
        stile.oldValue = stile.value
        stile.value = 0
        dtile.oldValue = dtile.value
        dtile.value *= 2
        if not scoreUpd:
            scoreUpd = 1
            oldScore = score
        score += dtile.value
        dtile.link = stile
        dtile.linkCount = 2
        stile.oldCoords = stile.coords
    if (stile.value != dtile.value == 0):
        dtile.value = stile.value
        stile.value = 0
def doMerges(key, difficulty=2):
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
        if newTile(difficulty=difficulty):
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


def startGame(FPS=60, text=False, difficulty=2, width=400, square=False, load=None):
    global objects, score
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
                with open(os.path.join(".2048data", "game.2048"), 'w') as f:
                    f.write(json.dumps([[[tile.value for tile in row] for row in objects], score], indent=4))
                break
            elif e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_w, pygame.K_q] and (pygame.key.get_mods() & (pygame.KMOD_META if sys.platform == "darwin" else pygame.KMOD_CTRL)):
                    playing = False
                    with open(os.path.join(".2048data", "game.2048"), 'w') as f:
                        f.write(json.dumps([[[tile.value for tile in row] for row in objects], score], indent=4))
                    break
                cont = doMerges(e.key, difficulty= difficulty)
                if cont:
                    if cont in ["nokey", "illegal"]:
                        printout = False
                    else:
                        printout = True
                    if checkGO():
                        playing = False
                        printout = False
                        updateDisplay(d, square=square, frame=int(FPS/8.0))
                        for frame in range(int(FPS/8.0)):
                            updateDisplay(d, square=square)
                        GOfont = pygame.font.Font(os.path.join(".2048data", "ClearSans-Regular.ttf"), int(width/12.0))
                        d.blit(GOfont.render("Game Over!", True, (119, 110, 101)), (int(width/2.0)-2.6*int(width/12.0), int(height-width)-int(width/3.0)))
                        with open(os.path.join(".2048data", "game.2048"), 'w') as f:
                            f.write(json.dumps([]))
                        for frame in range(5*FPS):
                            pygame.display.update()
                            clock.tick(FPS)
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif e.type ==  pygame.KEYDOWN:
                                    if e.key in [pygame.K_w, pygame.K_q] and (pygame.key.get_mods() & (pygame.KMOD_META if sys.platform == "darwin" else pygame.KMOD_CTRL)):
                                        pygame.quit()
                                        sys.exit()
                else:
                    playing = False
                    printout = False
                    break
        if printout:
            if text:
                os.system("cls" if sys.platform == "win32" else "clear")
                print(returnFormattedObjects(reset=True, spacing=2))
            updateDisplay(d, square=square, frame=int(FPS/8.0))
        updateDisplay(d, square=square)
    pygame.quit()
def addArgs():
    import argparse
    global objects, score
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        pygame.init()
        dpinfo = pygame.display.Info()
        pygame.quit()
        w = dpinfo.current_w
        h = dpinfo.current_h
    except:
        w = 1280
        h = 720
    parser = argparse.ArgumentParser(description='Play 2048!')
    maxw = int(min([w, h*2/3.0])*11/12.0)
    try:
        with open(os.path.join(".2048data", "settings.2048"), 'r') as f:
            argsFromFile = json.loads(f.read())
    except:
        argsFromFile = {'FPS': 60, 'width': int(maxw*2/3.0), 'difficulty': 2, 'load': None, 'text': False, 'square': False, 'newgame': False, 'reset': False, 'store': False}
    def openableFile(s):
        if not os.path.isfile(s):
            raise argparse.ArgumentTypeError("invalid filepath")
        if not os.access(s, os.R_OK):
            raise argparse.ArgumentTypeError("cannot read from file. Do you have sufficient permissions?")
        try:
            with open(s) as f:
                if s[-5:] == '.2048':
                    load = json.loads(f.read())
                    retobj = [[Tile(value=val) for val in row] for row in load[0]]
                    score = load[1]
                    return [retobj, score]
                else:
                    retobj = []
                    sumval = 0
                    lines = f.readlines()[:4]
                    if len(lines) != 4:
                        raise argparse.ArgumentTypeError("invalid formatting of text file (less than four lines)")
                    for line in lines:
                        if len(line.split(" ")) != 4:
                            raise argparse.ArgumentTypeError("invalid formatting of text file (wrong number of tiles or spaces)")
                        try:
                            tmplist = []
                            for val in line.split(" "):
                                val = int(val)
                                tmplist.append(Tile(value=val))
                                sumval += max((0, 2*val-3.4))
                            retobj.append(tmplist)
                        except ValueError:
                            raise argparse.ArgumentTypeError("invalid formatting of text file (not all tiles are numbers or there are extraneous spaces)")
                return [retobj, int(sumval-sumval%2)]
        except Exception as e:
            if isinstance(e, argparse.ArgumentTypeError):
                raise e
            else:
                raise argparse.ArgumentTypeError("there was a problem opening the file. See the error below:\n\n{0}\n\nIf you cannot fix this error, contact the developers on GitHub.".format(str(e).split('\n')[-1]))               
    parser.add_argument('-FPS', '-f', metavar="FRAMERATE", type=int,
                       help='Framerate at which the game runs. Default is '+str(argsFromFile["FPS"])+'.')
    parser.add_argument('-width', '-w', metavar="PIXELS", type=int,
                       help='width of window in pixels (height is dependent upon width). Default is '+str(argsFromFile["width"])+'.')
    parser.add_argument('-difficulty', '-d', metavar="LEVEL", type=int, choices=(1,2,3),
                       help='Difficulty level. Default is '+str(argsFromFile["difficulty"])+'. At level 1, tiles will spawn less frequently depending on the number of tiles already on the board. At level 2, normal 2048. At level 3, tiles with values that are multiples of 3 can spawn as well.')
    parser.add_argument('-load', '-l', metavar='FILE', type=openableFile, 
                       help='Load a game. Must be either a .2048 gamefile found in the ".2048data" directory or a text file with four lines, each containing four values separated by spaces. For empty spaces, write 0. WARNING: THIS WILL OVERWRITE YOUR SAVED GAME! It is stored in "'+os.path.join(os.getcwd(), '.2048data', 'game.2048')+'", so copy it out of there if you want to keep your save!')
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
    parser.add_argument('--update', action='store_true',
                       help='Update 2048 and exit. The feature will get the latest file from GitHub regardless of whether it has changed, so this may not necessarily do anything.')
    args = vars(parser.parse_args())
    if args['update']:
        UPDATEURL = 'https://raw.githubusercontent.com/101arrowz/2048/master/2048.py'
        if os.system("ping "+("-n" if sys.platform == "win32" else "-c")+" 1 github.com > "+os.devnull+" 2>&1"):
            print("Either GitHub is down (unlikely) or you are not connected to the internet. Connect to the internet next time to download the font. You will not need internet connectivity after that. Exiting...")
            sys.exit(1)
        else:
            if os.system(("powershell.exe (new-object System.Net.WebClient).DownloadFile('{}','"+os.path.join('.', '2048.py')+"')" if sys.platform == "win32" else "curl -L -o "+os.path.join(".", "2048.py")+" '{}'").format(UPDATEURL)+" > "+os.devnull+" 2>&1"):
                print("Update successful!")
                sys.exit(0)
            else:
                print("Update failed for an unknown reason. Contact the developers if the issue persists.")
    if args["reset"]:
        args["reset"] = False
        os.system(("del " if sys.platform == "win32" else "rm ")+os.path.join(".2048data", "settings.2048")+" > "+os.devnull+" 2>&1")
        argsFromFile = {'FPS': 60, 'width': int(maxw*2/3.0), 'difficulty': 2, 'text': False, 'square': False, 'newgame': False, 'reset': False, 'store': False}
    if args == {'FPS': None, 'width': None, 'difficulty': None, 'load': None, 'text': False, 'square': False, 'newgame': False, 'reset': False, 'store': False}:
        args = argsFromFile
    if args["FPS"] == None:
        args["FPS"] = argsFromFile["FPS"]
    if args["width"] == None:
        args["width"] = argsFromFile["width"]
    if args["difficulty"] == None:
        args["difficulty"] = argsFromFile["difficulty"]
    if args["newgame"]:
        with open(os.path.join(".2048data", "game.2048"), 'w') as f:
            f.write(json.dumps([[[tile.value for tile in row] for row in objects], score], indent=4))
    if args["width"] > maxw:
        args["width"] = maxw
    try:
        if args["load"]:
            load = args["load"][0]
            score = args["load"][1]
        else:
            load = None
    except KeyError:
        load = None
    args["load"] = None
    if args["store"]:
        args["store"] = False
        with open(os.path.join(".2048data", "settings.2048"), 'w') as f:
            f.write(json.dumps(args, indent=4, sort_keys=True))
    if load == None:
        args["load"] = loadGame()
    else:
        args["load"] = load
    del args["newgame"]
    del args["store"]
    del args["reset"]
    return args
def loadGame():
    global score
    try:
        with open(os.path.join(".2048data", "game.2048"), 'r') as f:
            load = json.loads(f.read())
            game = [[Tile(value=val) for val in row] for row in load[0]]
            score = load[1]
            if [[tile.__dict__["value"] for tile in row] for row in game] == [[0 for i1 in range(4)] for i2 in range(4)]:
                random.choice(random.choice(game)).value = 2
    except:
        global objects
        game=objects
    return game
if __name__ == "__main__":
    startGame(**addArgs())
