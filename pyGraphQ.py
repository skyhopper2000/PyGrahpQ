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
                 background : pygame.typing.ColorLike = (255 , 255, 255)
                 ) -> None: 

        """
        Initializes an app object which acts as the base for a pygame applet. Does not run the app.
        :param icon: a pygame surface object that represents the window. Defaults to pygame icon.
        :param name: a string which is the title of the window. Defaults to 'Canvas'
        :param screenWidth: the pixel width of the window. Defaults to 400
        :param screenHeight: the pixel height of the window. Defaults to 400
        :param fps: Used to determine how frequently the game update. Defaults to 30
        :param background: set the background color of the app. Defaults to white. See pygame for ColorLike options.
        """
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

    def start(self) -> None:
        """
        Initiates the pygame environment. Introduces runtime variables.
        clock: type pygame.time.Clock() - the native time keeper for the app
        dt: type float - the difference in time between steps measured every step in seconds
        tnaught: type float - internal used to calculate dt
        running: determines if the App is running. Setting to false quits the app.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.rect.width, self.rect.height))
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
    
    def redrawAll(self) -> None:
        "Draws all objects in app.group to the screen in the order they were added to app.group"
        pygame.draw.rect(self.screen, self.background, self.rect) # draw Background
        for obj in self.group:
            obj.draw()

    def step(self) -> None:
        "Updates the state of the app by 1 frame. To change, use @app.on('step')"
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

    def addGroup(self, name : str, objects : list) -> None:
        "Adds a new group to app.groups, assigned as 'name' : [objects]"
        self.groups.setdefault(name, pygame.sprite.Group())
        for obj in objects:
            if obj not in self.group:
                self.group.add(obj)
        self.groups[name].add(objects)
    
    def on(self, event : str) -> function:
        """Decorator: register a function to fire when `event` occurs."""
        def decorator(func):
            self.eventHandlers.setdefault(event, []).append(func) # Gives function a callable key
            return func  # return unchanged so it's still normally callable
        return decorator
    
    def fire(self, event : str, *args, **kwargs) -> None:
        """Call this internally when the event happens."""
        for handler in self.eventHandlers.get(event, []):
            handler(*args, **kwargs) # Calls any function that hes the given 'event' key

class HitBox:

    def __init__(self, app : App, surface : pygame.Surface, origin : pygame.typing.Point):
         self.app = app
         mask = pygame.mask.from_surface(surface)
         maskRect = mask.get_rect()
         self.box = []
         for x in range(maskRect.width):
             for y in range(maskRect.height):
                 if mask.get_at((x, y)) == 1:
                     x0, y0 = origin
                     self.box.append(((x0 + x), (y0 + y)))

    def hitPoint(self, point : pygame.typing.Point) -> bool:
        return (point in self.box)

class Item(pygame.sprite.Sprite):
    def __init__(self, app : App, x : int, y : int, width : int, height : int, fill : pygame.typing.ColorLike):
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

        self.rotation = 0

        self.surface = self.handleRotation()
        self.surfaceRect = self.surface.get_rect()
        self.hitBox = HitBox(self.app, self.surface, (self.x, self.y))

        app.group.add(self)

    def changeRotation(self, degrees : int):
        rotation = (self.rotation + degrees) % 360
        self.rotation = rotation
        
    def handleRotation(self) -> pygame.Surface:
        screenSurface = pygame.Surface((self.rect.width, self.rect.height), flags = pygame.SRCALPHA)
        self.render(screenSurface, (0, 0))
        screenSurface = pygame.transform.rotate(screenSurface, self.rotation)
        return screenSurface

    def update(self, *args, **kwargs):
        self.surface = self.handleRotation()
        screenSurfaceRect = self.surface.get_rect()
        correctedLeft = self.rect.centerx - (0.5*(screenSurfaceRect.width))
        correctedTop = self.rect.centery - (0.5*(screenSurfaceRect.height))
        self.surfaceRect = pygame.Rect(correctedLeft, correctedTop, screenSurfaceRect.width, screenSurfaceRect.height)
        self.hitBox = HitBox(self.app, self.surface, (self.surfaceRect.left, self.surfaceRect.top))

    def render(self, surface : pygame.Surface, destination : pygame.typing.Point):
        """
        Method which should render the Item to the given surface, at the given coordinates
        """
    
    def draw(self):
        """
        Abstract method that all children classes should have,
        should draw item to surface
        """
        pass

class Graphic(Item):

    def __init__(self, app : App, x : int, y : int, width : int, height : int,
                 sprite : pygame.Surface):
        """
        An base level implementation of Item for image-like visuals
        :param sprite: the sprite to be displayed
        """
        super().__init__(app, x, y, width, height, (0,0,0))
        if sprite.get_rect() != self.rect:
            self.sprite = pygame.transform.scale(sprite, (width, height))
        else:
            self.sprite = sprite

    def update(self, *args, **kwargs):
        super().update()

    def render(self, surface : pygame.Surface, destination : pygame.typing.Point) -> None:
            top, left = destination
            alignedRect = pygame.Rect(top, left, self.width, self.height)
            surface.blit(self.sprite, alignedRect)

    def draw(self):
        self.app.screen.blit(self.surface, (self.surfaceRect.left, self.surfaceRect.top))

class Timer(Item):
    def __init__(self, app: App, x : int, y : int, width : int, height : int,
                 initialValue : float, font : pygame.Font, color : pygame.typing.ColorLike = (0, 0, 0)):
        """
        Creates a model object which represents a timer.
        """
        super().__init__(app, x, y, width, height, color)
        self.time = initialValue
        self.font = font
        self.color = color
        self.paused = True
    
    def update(self, *args, **kwargs) -> None:
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
    
    def draw(self) -> None:
        #pygame.draw.rect(surface, (0,0,0), self.rect)
        text = self.font.render(self.getPrettyTime(), True, self.color)
        textRect = text.get_rect(center = self.rect.center)
        self.app.screen.blit(text, textRect)
        

class TextBox(Item):

    def __init__(self, app: App, x : int, y : int, width : int, height : int,
                 text : str, font : pygame.Font = DEFAULT_FONT,
                 align : str = "left-top", padding : int = 20, spacing : float = 1.15) -> None:

        """
        Creates a text box object. Text generates within the box in a wrapping pattern based on parameters.
        :param text: sets the text to be displayed in the object. May be a string of any length.
        :param font: the font which the text will be displayed in. Defaults to Lucida Console 16.
        :param align: see further documentation. Defaults to "left-top".
        :param padding: the pixel distance from the boundary rect to the text. Defaults to 20
        :param spacing: as in any word processor, the line spacing. Must be between 1 and 3 inclusive. Defaults to 1.15
        """
        
        

        self.text = text
        self.font = font
        self.visible = True
        self.align = "left-top"
        self.padding = padding
        
        self.validAligns = ['left-top', 'center-top', 'right-top',
                            'left-middle', 'center-middle', 'right-middle',
                            'left-bottom', 'center-bottom', 'right-bottom']
        
        self.horizontalAlignDict = {'left' : 'renderingRect.left + self.padding',
                                    'center' : 'renderingRect.centerx - (0.5 * lineSurface.get_width())',
                                    'right' : 'renderingRect.right - lineSurface.get_width()'}
        
        self.verticalAlignDict = {'top' : 'renderingRect.top',
                                  'middle' : 'renderingRect.centery - (0.5 * totalHeight)',
                                  'bottom' : 'renderingRect.bottom - totalHeight'}
        
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
            self.align = 'left-top'

        super().__init__(app, x, y, width, height, (0, 0, 0))
    
    def getValidAligns(self) -> list:
        "Returns a list of valid alignments for the TextBox object"
        for alignment in self.validAligns:
            print(alignment)
        return self.validAligns

    def render(self, surface, destination):
        "Renders the text to the surface."
        renderingRect = pygame.Rect(destination, (self.rect.width, self.rect.height))
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
            surface.blit(lineSurface, (lineX, lineY))
            lineY += lineSpacing

    def draw(self) -> None:
        screenSurface = self.handleRotation()
        screenSurfaceRect = screenSurface.get_rect()
        correctedLeft = self.rect.centerx - (0.5*(screenSurfaceRect.width))
        correctedTop = self.rect.centery - (0.5*(screenSurfaceRect.height))
        self.app.screen.blit(screenSurface, (correctedLeft, correctedTop))
            
    
    def update(self):
        "No update on step"
        pass

    def setText(self, newText : str):
        "Method for resetting the string after initialization"
        self.text = newText
        self.update()
    
    def setAlign(self, align : str):
        "Method for resetting alignment"
        if align in self.validAligns:
            self.align = align
        else:
            print('Not a valid align, try .getValidAligns() to get a list of valid aligns.')
            print('Defaulted to left-top')
            self.align = 'left-top'


class Rectangle(Item):

    def __init__(self,
                 app : App, x : int, y : int, width : int, height : int,
                 fill : pygame.typing.ColorLike = (0, 0, 0)) -> None:
        """
        Class for drawing rectangles with straight edges.
        :param fill: The color in which the rectangle is drawn. Defaults to black.
        """
        super().__init__(app, x, y, width, height, fill)
    
    def update(self) -> None:
        "No update on step"
        super().update()
        
    def render(self, surface : pygame.Surface, destination : pygame.typing.Point) -> None:
        top, left = destination
        alignedRect = pygame.Rect(top, left, self.width, self.height)
        pygame.draw.rect(surface, self.fill, alignedRect)

    def draw(self) -> None:
        "Renders the rectangle to its assigned app screen"
        self.app.screen.blit(self.surface, (self.surfaceRect.left, self.surfaceRect.top))
    
    def reColor(self, fill : pygame.typing.ColorLike = (0, 0, 0)) -> None:
        "Set rectangle to a different color"
        self.fill = fill

class Circle(Item):

    def __init__(self,
                 app : App, centerX : int, centerY : int, radius : int,
                 fill : pygame.typing.ColorLike = (0, 0, 0)):
        """
        Class for circles centered on a point.
        :param centerX: the centermost x position of the circle
        :param centerY: the centermost y position of the circle
        :param radius: the pixel radius of the circle to be drawn
        :param fill: The color in which the circle is drawn. Defaults to black.
        """
        top = centerY - radius
        left = centerX - radius
        width = 2 * radius
        height = width
        self.radius = radius
        super().__init__(app, top, left, width, height, fill)
        
    
    def update(self):
        "No update on step"
        super().update()

    def render(self, surface : pygame.Surface, destination : pygame.typing.Point) -> None:
        left, top = destination
        centerX = left + self.radius
        centerY = top + self.radius
        pygame.draw.circle(surface, self.fill, (centerX, centerY), self.radius)
    
    def draw(self):
        "Renders the circle to its assigned app screen"
        self.app.screen.blit(self.surface, (self.surfaceRect.left, self.surfaceRect.top))
    
    def reColor(self, fill : pygame.typing.ColorLike = (0, 0, 0)):
        "Set Circle to a different color"
        self.fill = fill


class Ellipse(Item):

    def __init__(self,
                 app : App, x : int, y : int, width : int, height : int,
                 fill : pygame.typing.ColorLike = (0, 0, 0)):

        """
        Class for drawing ellipse defined by a rectangular bounding box.
        :param fill: The color in which the rectangle is drawn. Defaults to black.
        """
        super().__init__(app, x, y, width, height, fill)
    
    def update(self, *args, **kwargs):

        super().update()

    def render(self, surface, destination):
        top, left = destination
        alignedRect = pygame.Rect(top, left, self.width, self.height)
        pygame.draw.ellipse(surface, self.fill, alignedRect)
        
    def draw(self):
        "Renders the ellipse to its assigned app screen"
        self.app.screen.blit(self.surface, (self.surfaceRect.left, self.surfaceRect.top))
    
    def reColor(self, fill : pygame.typing.ColorLike = (0, 0, 0)):
        "Set this ellipse to a different color"
        self.fill = fill

class Line(Item):

    def __init__(self,
                 app : App, x1 : int, y1 : int, x2 : int, y2 : int,
                 width : int = 1, color : pygame.typing.ColorLike = (0, 0, 0)):

        """
        Defines a line based on two points.
        :param x1: first point's x
        :param y1: first point's y
        :param x2: second point's x
        :param y2: second point's y
        :param width: pixel width of the line between the two points. Defaults to 1
        :param color: color of the line. Defaults to black
        """

        rectWidth = abs(x1 - x2) + width
        rectHeight = abs(y1 - y2) + width

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
        self.startPoint = (x1, y1) # local information
        self.endPoint = (x2, y2) # local information
        
        self.width = width
        
        boundingRect = pygame.Rect((x1, y1), (rectWidth, rectHeight))
        super().__init__(app, boundingRect.left, boundingRect.top, boundingRect.width, boundingRect.height, color)

        
    
    def update(self):
        
        super().update()

    def render(self, surface, destination):
        destX, destY = destination
        endPointX = destX + abs(self.x1 - self.x2)
        endPointY = destY + abs(self.y1 - self.y2)
        pygame.draw.line(surface, self.fill, (destX, destY), (endPointX, endPointY), width = self.width)
    
    def draw(self):
        "Renders the line on its assigned app screen"
        self.app.screen.blit(self.surface, (self.surfaceRect.left, self.surfaceRect.top))
    
    def reColor(self, fill : pygame.typing.ColorLike = (0, 0, 0)):
        "Sets the color of line"
        self.fill = fill

class RoundRectangle(Rectangle):

    def __init__(self,
                 app : App, x : int, y : int, width : int, height : int,
                 fill : pygame.typing.ColorLike = (0, 0, 0), roundness : int = 0,
                 r1 : int = 0, r2 : int = 0, r3 : int = 0, r4 : int = 0):
        
        """
        A class for drawing rects with rounded corners

        r1-------------------r2
        |                     |
        r3-------------------r4

        All roundness arguments are 0 (no curve) by default.
        Range is [0, min(height, width) / 2].
        """
        
        super().__init__(app, x, y, width, height, fill)

        self.roundness = roundness

        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4

        
    def render(self, surface : pygame.Surface, destination : pygame.typing.Point) -> None:
        top, left = destination
        alignedRect = pygame.Rect(top, left, self.width, self.height)
        pygame.draw.rect(surface, self.fill, alignedRect,
                         border_radius = self.roundness, border_top_left_radius = self.r1,
                         border_top_right_radius = self.r2, border_bottom_left_radius = self.r3,
                         border_bottom_right_radius = self.r4)
        
class Button:

    def _init_button(self, hoverColor : pygame.typing.ColorLike, pressedColor : pygame.typing.ColorLike):
        self.hoverColor = hoverColor
        self.pressedColor = pressedColor
        self.releasedColor = getattr(self, 'fill')
        self.isPressed = False
        self.whenClickedFunc = []

    def update(self):
        "Sets the state of the button based on the mouse's position."
        super().update()
        if self.hitBox.hitPoint((self.app.mouseX, self.app.mouseY)):
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
