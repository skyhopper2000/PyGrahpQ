from pyGraphQ import *

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
                assert 0.048 < app.dt < 0.052
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
        assert t1.font.name == 'Arial'
        assert t1.font.point_size == 12

    def testRender(self):
        t1 = TextBox(self.app, 200, 200, 100, 24, 'foobar', typeFace= 'Times New Roman', size = 24, color = (0, 0, 255), italic = True)
        print(t1.hitBox.prettyMask())
        assert t1.hitBox.prettyMask() == """0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000111110000000000000000000000011110000000000000000000000000000000000000
0000000000000000000000000000001111111000000000000000000000111110000000000000000000000000000000000000
0000000000000000000000000000001110111000000000000000000000001110000000000000000000000000000000000000
0000000000000000000000000000011100000000000000000000000000001110000000000000000000000000000000000000
0000000000000000000000000000111100000000000000000000000000011100000000000000000000000000000000000000
0000000000000000000000000011111000000000000000000000000000011100000000000000000000000000000000000000
0000000000000000000000000011111110001111110000001111110000011111111000001111111101111101110000000000
0000000000000000000000000000111000011111111000011111111000011111111100011111111001111011110000000000
0000000000000000000000000001110000111100111000111100111000111100011100111100111000111111110000000000
0000000000000000000000000001110001111000011101111000011100111000011101111000111000111110000000000000
0000000000000000000000000001110001110000111101110000111100111000011101110000111000111100000000000000
0000000000000000000000000001110011110000111011110000111001110000111001110001110000111000000000000000
0000000000000000000000000011100011100000111011100000111001110000111011100001110001111000000000000000
0000000000000000000000000011100011100001111011100001111001110001111011100011110001110000000000000000
0000000000000000000000000011100011100011110011100011110011100001110011100111111001110000000000000000
0000000000000000000000000011100001111111100001111111100011101111100011111111111011100000000000000000
0000000000000000000000000111000001111111000001111111000011111111000001111111110011100000000000000000
0000000000000000000000000111000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000110000000000000000000000000000000000000000000000000000000000000000000000000
"""
        
