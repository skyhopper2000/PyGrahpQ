import pygame

pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont('lucidaconsole', 16)

class App():
    def __init__(self, 
                 icon : pygame.Surface = None, 
                 name : str = 'Canvas', 
                 screenWidth : int = 400, 
                 screenHeight : int = 400,
                 fps : int = 30,
                 background : tuple[int, int, int] = (255 , 255, 255)
                 ): 
        self.icon = icon
        self.name = name

        # Alignment
        self.rect = pygame.Rect(0, 0, screenWidth, screenHeight)

        self.fps = fps
        self.background = background
        self.group = pygame.sprite.Group()
        self.groups = {'app' : self.group}

        self.mouseX = 0
        self.mouseY = 0
        self.mouseIsDown = False

        self.running = False
        self.eventHandlers = {} # a dictionary of 'eventName' to function

    def start(self):
        """
        Initiates the pygame environment. Introduces runtime variables.
        clock: type pygame.time.Clock() - the native time keeper for the app
        dt: type float - the difference in time between steps measured every step in seconds
        tnaught: type float - internal used to calculate dt
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.rect.width, self.rect.height), pygame.RESIZABLE)
        pygame.display.set_caption(self.name)
        if self.icon is not None:
            pygame.display.set_icon(self.icon)
        
        self.clock = pygame.time.Clock()
        self.dt = 0.0
        self.tnaught = self.clock.get_time()

        self.running = True
        
        while self.running:
            self.step()
        
        pygame.quit()
    
    def redrawAll(self):

        pygame.draw.rect(self.screen, self.background, self.rect) # draw Background
        for obj in self.group:
            obj.draw()

    def step(self):

        self.mouseX, self.mouseY = pygame.mouse.get_pos()
        self.dt = (self.clock.get_time() - self.tnaught) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouseIsDown = True
                    self.fire('mouseDown', self)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouseIsDown = False
                    self.fire('mouseUp', self)
        
        self.fire('step', self)

        self.group.update()

        self.redrawAll()

        self.clock.tick(30)

        pygame.display.flip()

    def addGroup(self, name : str, objects : list):
        self.groups.setdefault(name, pygame.sprite.Group())
        for obj in objects:
            if obj not in self.group:
                self.group.add(obj)
        self.groups[name].add(objects)
    
    def on(self, event : str):
        """Decorator: register a function to fire when `event` occurs."""
        def decorator(func):
            self.eventHandlers.setdefault(event, []).append(func) # Gives function a callable key
            return func  # return unchanged so it's still normally callable
        return decorator
    
    def fire(self, event : str, *args, **kwargs):
        """Call this internally when the event happens."""
        for handler in self.eventHandlers.get(event, []):
            handler(*args, **kwargs) # Calls any function that hes the given 'event' key


class Item(pygame.sprite.Sprite):
    def __init__(self, app : App, x : int, y : int, width : int, height : int, fill : tuple[int, int, int]):
        """
        Simple base class for visual objects,
        
        :param x: leftmost pixel
        :param y: rightmost pixel
        :param width: width (right from the x) of object in pixels
        :param height: height (down from the y) of the object in pixels
        """
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

        self.fill = fill

        self.app = app
        
        self.visible = True

        app.group.add(self)
    
    def draw(self):
        """
        Abstract mmethod that all children classes should have,
        should draw item to surface
        """
        pass

class Graphic(Item):

    def __init__(self, app : App, x : int, y : int, width : int, height : int,
                 sprite : pygame.Surface):
        """
        An base level implementation of Item for static visuals
        :param sprite: the sprite to be displayed
        """
        super().__init__(app, x, y, width, height, (0,0,0))
        if sprite.get_rect() != self.rect:
            self.sprite = pygame.transform.scale(sprite, (width, height))
        else:
            self.sprite = sprite

    def draw(self, surface : pygame.Surface):
        surface.blit(self.sprite, self.rect)

class Timer(Item):
    def __init__(self,x : int, y : int, width : int, height : int,
                 initialValue : float, font : pygame.Font, color : tuple[int, int, int] = (0, 0, 0)):
        """
        Creates a model object which represents a timer.
        """
        super().__init__(x, y, width, height)
        self.time = initialValue
        self.font = font
        self.color = color
        self.paused = True
    
    def update(self) -> None:
        if not self.paused:
            self.time -= self.app.dt
    
    def getTime(self) -> float:
        return self.time
    
    def pause(self) -> None:
        self.paused = True
    
    def unpause(self) -> None:
        self.paused = False
    
    def reset(self) -> None:
        self.time = 30.0

    def getPrettyTime(self) -> str:
        time = self.time
        time = round(time, 2)
        centiseconds = (time * 100) % 100
        seconds = time % 100
        csecString = str(round(centiseconds))
        if len(csecString) < 2:
            csecString = csecString + "0"
        outString = str(round(seconds)) + ":" + csecString
        return outString
    
    def draw(self, surface : pygame.Surface) -> None:
        #pygame.draw.rect(surface, (0,0,0), self.rect)
        text = self.font.render(self.getPrettyTime(), True, self.color)
        textRect = text.get_rect(center = self.rect.center)
        surface.blit(text, textRect)

class TextBox(Item):

    def __init__(self, app: App, x : int, y : int, width : int, height : int,
                 text : str, font : pygame.Font = DEFAULT_FONT,
                 align : str = "left-top", padding : int = 20, spacing : float = 1.15):
        
        super().__init__(app, x, y, width, height, (0, 0, 0))

        self.text = text
        self.font = font
        self.visible = True
        self.align = "left-top"
        self.padding = padding
        
        self.validAligns = ['left-top', 'center-top', 'right-top',
                            'left-middle', 'center-middle', 'right-middle',
                            'left-bottom', 'center-bottom', 'right-bottom']
        
        self.horizontalAlignDict = {'left' : 'self.rect.left + self.padding',
                                    'center' : 'self.rect.centerx - (0.5 * lineSurface.get_width())',
                                    'right' : 'self.rect.right - lineSurface.get_width()'}
        
        self.verticalAlignDict = {'top' : 'self.rect.top',
                                  'middle' : 'self.rect.centery - (0.5 * totalHeight)',
                                  'bottom' : 'self.rect.bottom - totalHeight'}
        
        if 1 <= spacing <= 3:
            self.spacing = spacing
        else:
            print('Spacing must be between 1 and 3 inclusive. Defaulted to 1.15.')
            self.spacing = 1.15
        
        if align in self.validAligns:
            self.align = align
        else:
            print('Not a valid align, try .getValidAligns() to get a list of valid aligns.')
            print('Defaulted to left-top')
    
    def getValidAligns(self) -> list:
        for alignment in self.validAligns:
            print(alignment)
        return self.validAligns

    def draw(self):
        padding = 20
        lineSpacing = self.font.point_size * self.spacing
        words = self.text.split(' ') # -> words is a sequential list of all words
        lines = []
        current_line = []
        
        for word in words:
            # -> current_line is the list of all words which do not exceed the rect size for the current line
            testLine = ' '.join(current_line + [word]) 
            # -> testLine is a string of all the words which so far have not exceeded the rect limits plus the next word
            testRect = self.font.render(testLine, True, (255, 255, 255))
            # -> testRect is a rect which represents the space a line would take up
            
            if testRect.get_width() <= self.rect.width - (padding * 2):
                current_line.append(word)
                # if it doesn't take up too much space, add the word to the line
            else:
                if current_line != []:
                    lines.append(' '.join(current_line))
                current_line = [word]
                # otherwise, add the current line without the test word to the list of lines and begin a new line on the test word
        
        if current_line != []:
            lines.append(' '.join(current_line))
        
        # Draw wrapped lines
        textAlignments = self.align.split('-')
        totalHeight = ((len(lines)) * lineSpacing)
        lineY = eval(self.verticalAlignDict[textAlignments[1]])
        for line in lines:
            lineSurface = self.font.render(line, True, (0, 0, 0))
            lineX = eval(self.horizontalAlignDict[textAlignments[0]])
            self.app.screen.blit(lineSurface, (lineX, lineY))
            lineY += lineSpacing
            
    
    def update(self):
        pass

    def setText(self, newText : str):
        self.text = newText
        self.update()
    
    def setAlign(self, align : str):
        if align in self.validAligns:
            self.align = align
        else:
            print('Not a valid align, try .getValidAligns() to get a list of valid aligns.')
            print('Defaulted to left-top')


class Rectangle(Item):

    def __init__(self,
                 app : App, x : int, y : int, width : int, height : int,
                 fill : tuple[int, int, int] = (0, 0, 0)):
        
        super().__init__(app, x, y, width, height, fill)
    
    def update(self):
        pass

    def draw(self):
        
        pygame.draw.rect(self.app.screen, self.fill, self.rect)
    
    def reColor(self, fill : tuple[int, int, int] = (0, 0, 0)):
        self.fill = fill

class Circle(Item):

    def __init__(self,
                 app : App, centerX : int, centerY : int, radius : int,
                 fill : tuple[int, int, int] = (0, 0, 0)):
        
        top = centerY - radius
        left = centerX - radius
        width = 2 * radius
        height = width
        super().__init__(app, top, left, width, height, fill)
        self.radius = radius
    
    def update(self):
        pass

    def draw(self):
        pygame.draw.circle(self.app.screen, self.fill, self.rect.center, self.radius)
    
    def reColor(self, fill : tuple[int, int, int] = (0, 0, 0)):
        self.fill = fill


class Ellipse(Item):

    def __init__(self,
                 app : App, x : int, y : int, width : int, height : int,
                 fill : tuple[int, int, int] = (0, 0, 0)):
        
        super().__init__(app, x, y, width, height, fill)
    
    def update(self):
        pass

    def draw(self):
        
        pygame.draw.ellipse(self.app.screen, self.fill, self.rect)
    
    def reColor(self, fill : tuple[int, int, int] = (0, 0, 0)):
        self.fill = fill

class Line(Item):

    def __init__(self,
                 app : App, x1 : int, y1 : int, x2 : int, y2 : int,
                 width : float = 1.0, color : tuple[int, int, int] = (0, 0, 0)):
        
        boundingRect = pygame.Rect((x1, y1), (x2, y2))
        super().__init__(app, boundingRect.left, boundingRect.top, boundingRect.width, boundingRect.height, color)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.startPoint = (x1, y1) # local information
        self.endPoint = (x2, y2) # local information

        self.width = width
    
    def update(self):
        pass

    def draw(self):
        
        pygame.draw.line(self.app.screen, self.fill, self.startPoint, self.endPoint, width = self.width)
    
    def reColor(self, fill : tuple[int, int, int] = (0, 0, 0)):
        self.fill = fill

class RoundRectangle(Rectangle):

    def __init__(self,
                 app : App, x : int, y : int, width : int, height : int,
                 fill : tuple[int, int, int] = (0, 0, 0), roundness : float = 0.0,
                 r1 : float = 0, r2 : float = 0, r3 : float = 0, r4 : float = 0):
        
        """
        A class for drawing rects with rounded corners

        r1-------------------r2
        |                     |
        r3-------------------r4

        All roundness arguments are 0 (no curve) by default.
        Range is [0, min(height, width) / 2].
        """
        
        super().__int__(app, x, y, width, height, fill)

        self.roundness = roundness

        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4

        
    def draw(self):
        
        pygame.draw.rect(self.app.screen, self.fill, self.rect,
                         border_radius = self.roundness, border_top_left_radius = self.r1,
                         border_top_right_radius = self.r2, border_bottom_left_radius = self.r3,
                         border_bottom_right_radius = self.r4)
        
class Button:

    def _init_button(self, hoverColor : tuple[int, int, int], pressedColor : tuple[int, int, int]):
        self.hoverColor = hoverColor
        self.pressedColor = pressedColor
        self.releasedColor = getattr(self, 'fill')
        self.isPressed = False
        self.whenClickedFunc = []

    def update(self):
        super().update()
        if self.rect.collidepoint((self.app.mouseX, self.app.mouseY)):
            if self.app.mouseIsDown:
                self.fill = self.pressedColor
                self.isPressed = True
            else:
                self.fill = self.hoverColor
                self.isPressed = False
        else:
            self.fill = self.releasedColor
            self.isPressed = False

    def onClicked(self):
        """Decorator: register a function to fire when `event` occurs."""
        def decorator(func):
            self.whenClickedFunc.append(func) # Gives function a callable key
            return func  # return unchanged so it's still normally callable
        return decorator
    
    def fireClick(self, *args, **kwargs):
        """Call this internally when the event happens."""
        for handler in self.whenClickedFunc:
            handler(*args, **kwargs) # Calls any function that hes the given 'event' key
    


def buttonOf(graphicsObject, hoverColor, pressedColor):

    "Dynamically creates a button out of any Item class object"

    cls = type(graphicsObject)
    if Button not in cls.__mro__:
        cls = type('Button' + cls.__name__, (Button, cls), {})
        graphicsObject.__class__ = cls
    graphicsObject._init_button(hoverColor, pressedColor)
    return graphicsObject
