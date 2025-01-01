from time import time
from datetime import timedelta as timeFormater

class Timer:
    def __init__(self, root, cv, x, y):
        self.root = root
        self.cv = cv

        self.x = x
        self.y = y

        self.timeWhenSaved = None
        self.timeWhenLoading = None
        self.continueCounter = False

        self.cv.create_rectangle(x-75, y-25, x+75, y+25, fill="#9592b4", outline="", tag="Timer")
        self.id = None
        self.initialTime = time()
        self.draw()

    def save(self):
        return [self.initialTime, time()]

    def load(self, data):
        initialTime, timeWhenSaved = data
        deltaTime = time() - timeWhenSaved
        self.initialTime = initialTime + deltaTime

    def stop(self):
        self.continueCounter = False

    def draw(self):
        t = int(time() - self.initialTime)
        txt = timeFormater(seconds=t)

        if self.id != None:
            self.cv.delete(self.id)
        self.id = self.cv.create_text(self.x, self.y, fill="#141417",font="Arial 22", text=txt, tag="Timer")

    def update(self):
        self.draw()
        if self.continueCounter:
            self.root.after(200, self.update)

    def reset(self):
        self.initialTime = time()
        self.draw()

    def start(self):
        self.continueCounter = True
        self.update()

    def isRunning(self):
        """Return true when the timer is running"""
        return self.continueCounter
