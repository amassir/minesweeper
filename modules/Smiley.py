

class Smiley :
    def __init__(self, cns, x, y):
        from tkinter import PhotoImage
        self.cns = cns
        self.x = x
        self.y = y

        self.ref = {} # Reference de toutes les images d'émotions
        path = "./img/emoticons/"

        for state in ["happy", "tickle"]: # ["happy", "pokerface", "tickle", "anxious","dead"]
            img = PhotoImage(file = path + state + ".gif")
            self.ref[state] = img.subsample(5, 5)

        self.draw("happy")

    def draw(self, state):
        self.cns.delete("emoji")
        if not state in self.ref: return
        self.cns.create_image(self.x, self.y, image = self.ref[state], tag="emoji")
