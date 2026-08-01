from pyGraphQ import *

class TestApp:


    def testInit(self):
        app = App()
        assert app.running == False
        assert app.eventHandlers == {}
        del app

        app = App(name = 'foo', screenWidth = 600, screenHeight = 1, background=(0, 0, 255))
        assert app.running == False
        assert app.name == 'foo'
        assert app.background == (0, 0, 255)
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

class TestRectangle:

    def setup_method(self, method):
        app = App(fps = 1)

    def teardown_method(self, method):
        app.quit()
        del app

    def testInit(self):
        r1 = Rectangle(app, 0, 0, 200, 200)
        assert r1.rect.left == 0
        assert r1.rect.top == 0
        assert r1.rect.center == (100, 100)
        app.start()

        
        
        
