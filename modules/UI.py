class Widget :
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = [x, y, x+w, y+h]

    def removeOnArray(self, array):
        if self in array:
            print("True")

    def detect(self, x, y):
        return (self.x < x < self.x + self.w) and (self.y < y < self.y + self.h)


class Button(Widget) :
    """Boutton de sous-widget canvas"""
    def __init__(self, canvas, x, y, w, h, name="Button", f=lambda : print("Comming soon"), colorSchem=["#000000", "#444433", "#998755", "#AAAAAA"]):
        super().__init__(x, y, w, h)
        self.cv = canvas
        self.name = name
        self.function = f
        self.thm = colorSchem

        self.selected = False  # Etat du bouton au commencement
        self.pushed = False

        #### Les id canvas de ce qu'on dessine du bouton ####
        self.wdg = None
        self.txt = None

    def onMotion(self, cursor): # coordonnée du curseur

        self.selected = self.detect( cursor[0], cursor[1] )
        if not self.pushed:
            if self.selected :
                self.grow(5)
                self.render(self.thm[1])
            else:
                self.grow(0)
                self.render(self.thm[0])
        else:
            if self.selected:
                self.render(self.thm[2])

    def onPress(self):
        if self.selected :
            self.pushed = True
            self.grow(0)
            self.render(self.thm[2])
        return self.selected

    def onRelease(self):
        if self.selected:
            if self.pushed:
                self.grow(5)
                self.render(self.thm[1])
                self.function()
            else:
                self.grow(5)
                self.render(self.thm[0])
        else:
            self.grow(0)
            self.render(self.thm[0])
        self.pushed = False

        return self.selected

    def destroy(self):
        self.cv.delete(self.wdg)
        self.cv.delete(self.txt)


    def grow(self, v=0):
        self.rect = [self.x-v, self.y-v, self.x+self.w+v, self.y+self.h+v]

    def render(self, color = None):
        if self.wdg != None and self.txt != None:
            self.destroy()

        if color == None : # La couleur par defaut
            color = self.thm[0]

        self.wdg = self.cv.create_rectangle( self.rect, fill=color, outline="", tag="Button")
        self.txt = self.cv.create_text( self.x + self.w//2, self.y + self.h//2, font="Arial 12", text=self.name, fill=self.thm[3], tag="Button")






class Menu :
    def __init__(self, cv, x, y, w, h, thm=["#000000", "#444433", "#998755", "#AAAAAA"], menusToDestroy = [] ):
        self.cv = cv
        self.isActive = False  # L'état de l'ensemble (visuel + de l'interactivité) des boutons.
        self.buttons = []  # Liste de tout les boutons du menu

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.thm = thm
        # Liste de menu a detruire lorsqu'on interagit avec ce menu
        self.menusToDestroy = menusToDestroy
        self.selfDestruct = False  # Auto destruction

    def addButton(self, title="Button", function=lambda : print("Comming soon")):
        self.buttons.append(Button(self.cv, self.x, self.y, self.w, self.h, title, function, self.thm))
        self.y += 100

    def start(self):
        if not self.isActive:
            self.isActive = True

            for button in self.buttons:
                button.render()
        else:
            self.destroy()


    def updateOnPress(self):
        """The update of a all buttons when left clicking with the mouse"""
        if self.isActive:
            for button in self.buttons:
                pressed = button.onPress()
                if pressed:
                    if self.menusToDestroy != []:
                        for menu in self.menusToDestroy:
                            menu.destroy()

    def updateOnRelease(self):
        if self.isActive:
            for button in self.buttons:
                pressed = button.onRelease()
                if pressed and self.selfDestruct:
                    self.destroy()
                    break  # On ne veut pas qu'il continue a inspecter les bouton lorsqu'il s'auto detruit

    def updateOnMotion(self, cursor):
        if self.isActive:
            for button in self.buttons:
                button.onMotion(cursor)

    def destroy(self):
        if self.isActive:  # Si on ne l'a pas deja detruit
            self.isActive = False
            for button in self.buttons:
                button.destroy()
