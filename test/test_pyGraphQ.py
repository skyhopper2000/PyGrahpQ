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
        assert t1.hitBox.box == [(225, 223), (226, 211), (226, 220), (226, 221), (226, 222), 
                                 (226, 223), (227, 211), (227, 216), (227, 217), (227, 218), 
                                 (227, 219), (227, 220), (227, 221), (228, 210), (228, 211), 
                                 (228, 212), (228, 213), (228, 214), (228, 215), (228, 216), 
                                 (228, 217), (228, 218), (229, 209), (229, 210), (229, 211), 
                                 (229, 212), (229, 213), (229, 214), (230, 207), (230, 208), 
                                 (230, 209), (230, 210), (230, 211), (231, 206), (231, 207), 
                                 (231, 211), (232, 206), (233, 205), (233, 215), (233, 216), 
                                 (233, 217), (233, 218), (233, 219), (233, 220), (234, 205), 
                                 (234, 214), (234, 215), (234, 216), (234, 217), (234, 218), 
                                 (234, 219), (234, 220), (234, 221), (235, 205), (235, 206), 
                                 (235, 207), (235, 213), (235, 214), (235, 221), (236, 212), 
                                 (236, 213), (236, 221), (237, 211), (237, 212), (237, 221), 
                                 (238, 211), (238, 220), (238, 221), (239, 211), (239, 219), 
                                 (239, 220), (240, 211), (240, 212), (240, 217), (240, 218), 
                                 (240, 219), (241, 212), (241, 213), (241, 214), (241, 215), 
                                 (241, 216), (241, 217), (241, 218), (242, 213), (242, 214), 
                                 (242, 215), (242, 216), (245, 215), (245, 216), (245, 217), 
                                 (245, 218), (245, 219), (245, 220), (246, 214), (246, 215), 
                                 (246, 216), (246, 217), (246, 218), (246, 219), (246, 220), 
                                 (246, 221), (247, 213), (247, 214), (247, 221), (248, 212), 
                                 (248, 213), (248, 221), (249, 211), (249, 212), (249, 221), 
                                 (250, 211), (250, 220), (250, 221), (251, 211), (251, 219), 
                                 (251, 220), (252, 211), (252, 212), (252, 217), (252, 218), 
                                 (252, 219), (253, 212), (253, 213), (253, 214), (253, 215), 
                                 (253, 216), (253, 217), (253, 218), (254, 213), (254, 214), 
                                 (254, 215), (254, 216), (257, 218), (257, 219), (257, 220), 
                                 (258, 215), (258, 216), (258, 217), (258, 218), (258, 219), 
                                 (258, 220), (258, 221), (259, 206), (259, 211), (259, 212), 
                                 (259, 213), (259, 214), (259, 215), (259, 216), (259, 221), 
                                 (260, 206), (260, 208), (260, 209), (260, 210), (260, 211), 
                                 (260, 212), (260, 213), (260, 221), (261, 205), (261, 206), 
                                 (261, 207), (261, 208), (261, 209), (261, 212), (261, 221), 
                                 (262, 205), (262, 211), (262, 220), (263, 211), (263, 219), 
                                 (263, 220), (264, 211), (264, 218), (264, 219), (265, 211), 
                                 (265, 212), (265, 213), (265, 214), (265, 215), (265, 216), 
                                 (265, 217), (265, 218), (266, 212), (266, 213), (266, 214), 
                                 (266, 215), (266, 216), (269, 216), (269, 217), (269, 218), 
                                 (269, 219), (269, 220), (269, 221), (270, 214), (270, 215), 
                                 (270, 216), (270, 217), (270, 218), (270, 220), (270, 221), 
                                 (271, 213), (271, 214), (271, 221), (272, 212), (272, 213), 
                                 (273, 211), (273, 212), (273, 220), (274, 211), (274, 219), 
                                 (275, 211), (275, 218), (275, 219), (275, 220), (275, 221), 
                                 (276, 212), (276, 213), (276, 214), (276, 215), (276, 216), 
                                 (276, 217), (276, 218), (276, 219), (276, 220), (276, 221), 
                                 (277, 211), (277, 212), (277, 213), (277, 214), (277, 215), 
                                 (277, 216), (278, 211), (278, 212), (278, 213), (281, 212), 
                                 (281, 219), (281, 220), (281, 221), (282, 212), (282, 215), 
                                 (282, 216), (282, 217), (282, 218), (282, 219), (282, 220), 
                                 (283, 211), (283, 212), (283, 213), (283, 214), (283, 215), 
                                 (283, 216), (283, 217), (284, 211), (284, 212), (284, 213), 
                                 (284, 215), (285, 214), (286, 213), (287, 212), (288, 211), 
                                 (288, 212), (288, 213), (289, 211), (289, 212)]
        
