from src.pygraphq.pyGraphQ import *
import os

class TestApp:


    def testInit(self):
        app = App()
        assert app.running == False
        assert app.eventHandlers == {}
        del app

        app = App(name = 'foo', screenWidth = 600, screenHeight = 1, background=(0, 0, 255), fps = 20)
        assert app.running == False
        assert app.name == 'foo'
        assert app.background == (0, 0, 255)
        assert app.fps == 20
        del app

    def testStart(self):
        app = App(name = 'foo', screenWidth = 600, screenHeight = 2, background=(0, 0, 255), fps = 30)

        @app.on('step')
        def onStep(app : App):
            assert app.running == True
            assert app.screen.width == 600
            assert app.screen.height == 2
            app.redrawAll()
            assert app.screen.get_at((0, 0)) == pygame.Color(0, 0, 255)
            app.running = False

        app.start()

    def testFPS(self):
        app = App(fps = 20)

        app.stepsToDown = 2

        @app.on('step')
        def onStep(app : App):
                
            if app.stepsToDown <= 0:
                assert 0.045 <= app.dt <= 0.055
                app.stop()

            app.stepsToDown -= 1

        app.start()

class TestRectangle:

    def setup_method(self, method):
        self.app = App()

    def teardown_method(self, method):
        self.app.stop()
        del self.app

    def testInit(self):
        r1 = Rectangle(self.app, 0, 0, 200, 200)
        assert r1.rect.left == 0
        assert r1.rect.top == 0
        assert r1.rect.center == (100, 100)

    def testVisual(self):
        r1 = Rectangle(self.app, 0, 0, 200, 200, fill = (0, 255, 0))
        self.app.steps = 0

        @self.app.on('step')
        def onStep(appItself : App):
            if appItself.steps > 0:
                assert appItself.screen.get_at((0, 0)) == pygame.Color(0, 255, 0)
                assert appItself.screen.get_at((300, 100)) == pygame.Color(255, 255, 255)
                assert appItself.screen.get_at((199, 100)) == pygame.Color(0, 255, 0)
                assert appItself.screen.get_at((200, 100)) == pygame.Color(255, 255, 255)
                appItself.stop()
            appItself.steps += 1

        self.app.start()

    def testCollision(self):
        r1 = Rectangle(self.app, 0, 0, 200, 200, fill = (0, 255, 0))
        self.app.steps = 0
        
        @self.app.on('step')
        def onStep(appItself : App):
            if appItself.steps > 0:
                assert appItself.group.sprites()[0].hitBox.hitPoint((0, 0)) == True #collision with top-left of rect
                assert appItself.group.sprites()[0].hitBox.hitPoint((300, 100)) == False #no collision in upper-right quadrant
                assert appItself.group.sprites()[0].hitBox.hitPoint((199, 100)) == True #collision with right edge of rect
                assert appItself.group.sprites()[0].hitBox.hitPoint((200, 100)) == False #no collision just off right edge of rect
                appItself.stop()
            self.app.steps += 1
        
        self.app.start()

class TestTextBox:

    def setup_method(self, method):
        pygame.font.init()
        self.app = App()
    
    def teardown_method(self, method):
        self.app.stop()
        del self.app

    def testInit(self):
        t1 = TextBox(self.app, 0, 0, 200, 200, 'foobar')
        assert t1.rect.left == 0
        assert t1.rect.top == 0
        assert t1.rect.center == (100, 100)
        assert t1.font.name == 'DejaVu Sans'
        assert t1.font.point_size == 12

    def testCallGetTypeFace(self, mocker):
        
        mockedOut = mocker.patch("src.pygraphq.pyGraphQ.pygame.font.match_font")
        mockedOut.return_value = os.path.join("fonts", "YoungSerif-Regular.ttf")

        t1 = TextBox(self.app, 0, 0, 200, 200, 'foo', typeFace = 'Young Serif')

        mockedOut.assert_called_once_with('Young Serif', False, False)

    def testOutGetTypeFace(self):
        t1 = TextBox(self.app, 0, 0, 200, 200, 'foo', typeFace = 'Liberation Sans')

        assert t1.font.name == 'Liberation Sans'
