from random import randrange as rdm
import Save as IE
import Timer, Smiley

#def disp(M) :
#    for l in M:
#        for d in l:
#            x = d["value"]
#            spacing = ""
#            if ( x >= 0 ):
#                spacing = " "
#            print(spacing, x, end="")
#        print()


class MineField :
    def __init__(self, n, p, nMine) :
        self.n = n
        self.p = p
        self.nMine = nMine

    def placeMine(self, i=None, j=None) :
        n, p = self.n, self.p
        mineToPlace = self.nMine
        def blankMatrice(n, p):
            matrice = []
            for i in range(n):
                matrice.append([])
                for j in range(p):
                    matrice[i].append({
                        "value": 0,
                        "visible": False,
                        "flagged": False
                    }) # state: 0 = invisible | 1 = visible
            return matrice

        def addToAdj(m, x, y):

            container = [-1, 0, 1]
            for k in container:
                for h in container:
                    i = y+h
                    j = x+k
                    if ( 0 <= i < n and 0 <= j < p and m[i][j]["value"] >= 0):
                        m[i][j]["value"] += 1
            return m

        self.m = blankMatrice(self.n, self.p)

        while mineToPlace > 0:
            x, y = rdm(self.n), rdm(self.p)

            if i == None:
                i = -1
                j = -1


            if not ( ( y-1 <= i <= y+1) and ( x-1 <= j <= x+1) ):  # Quand la bombe est assez loin du curseur
                case = self.m[y][x]
                if case["value"] >= 0:
                    case["value"] = -1
                    self.m = addToAdj(self.m, x, y)

                    mineToPlace -= 1
        #disp(self.m)






class Game:
    def __init__(self, root, cv, offset, windowWidth, theme):
        self.n = 10  # Hauteur
        self.p = 10  # Longueur
        self.bomb = 9# Nombre de bombe

        #### Dimension ####
        self.xOffset, self.yOffset = offset # coordonnés a partir duquelle on peut dessiner le champ de mine
        self.trueWidth = windowWidth
        self.width = windowWidth - 250 # Longueur du champ de mine
        self.caseLength = ( self.width // self.p ) - 2  # Taille des blocks
        self.caseSpace = 2 # Taille de l'espacement
        self.height = ( self.caseLength + self.caseSpace ) * self.n
        self.yAlign = self.yOffset // 2 # Coord y pour l'alignement des widgets

        ####  Score   ####
        self.score = 0
        self.step = 1
        self.scoreMax = (( self.n * self.p ) - self.bomb) * self.step

        self.root = root
        self.cv = cv
        self.theme = theme

        self.active = True
        self.cheat = False  # Le cheat est de base inactif

        self.firstClick = True
        self.selectionIndex = None
        self.revealLoopId = None

        self.mf = MineField(self.n, self.p, self.bomb)
        self.timer = Timer.Timer(root, cv, self.trueWidth*3//4, self.yAlign)
        self.smiley = Smiley.Smiley(cv, self.trueWidth//2, self.yAlign)



    def changeDim(self, n, p):
        self.n = n
        self.p = p
        self.caseLength = ( self.width // self.p ) - 2  # Taille des blocks
        self.height = ( self.caseLength + self.caseSpace ) * self.n
        self.start()

    def destroy(self):
        self.cv.delete("MineField")
        self.cv.delete("MF_Selection")
        self.cv.delete("Score")

    def draw(self):
        """Dessin initial du champ de mine sur le canvas"""
        w = self.caseLength
        d = self.caseSpace + w # Distance de l'espacement
        mid = d//2

        x, y = self.xOffset, self.yOffset
        self.destroy()  # On supprime le precedant champ de mine du canvas

        score = str(self.score) + " / " + str(self.scoreMax)
        self.cv.create_text(self.width // 3, self.yAlign - 20, fill=self.theme["Secondary"][1], font="Arial 22", text="Score: " + str(score), tag="Score")
        self.cv.create_text(self.width // 3, self.yAlign + 20, fill=self.theme["Primary"]["warning"], font="Arial 22", text="Mines: "+str(self.bomb), tag="Score")

        for i in range(self.n):
            for j in range(self.p):
                case = self.mf.m[i][j]
                if case["visible"]:
                    if case["value"] < 0 :  # Si c'est une bombe
                        self.cv.create_rectangle(x, y, x+w, y+w,fill=self.theme["Primary"]["warning"], outline="", tag="MineField")
                        self.cv.create_text(x+mid, y+mid+8, fill=self.theme["Primary"]["font"][1], font="Arial 20", text="*", tag="MineField")
                    elif case["value"] > 0:
                        self.cv.create_rectangle(x, y, x+w, y+w,fill=self.theme["Primary"]["game"][1], outline="", tag="MineField")
                        self.cv.create_text(x+mid, y+mid+5, fill=self.theme["Primary"]["font"][1], font="Arial 20", text=case["value"], tag="MineField")
                    else:
                        self.cv.create_rectangle(x, y, x+w, y+w,fill=self.theme["Primary"]["game"][1], outline="", tag="MineField")

                else:  # Si le contenu de la case n'est pas révelé
                    self.cv.create_rectangle(x, y, x+w, y+w,fill=self.theme["Primary"]["game"][0], outline="", tag="MineField")
                    if case["flagged"]:
                        self.cv.create_rectangle(x+w//3, y+w//4, x+w//3+2, y + w*3//4, fill=self.theme["Primary"]["warning"], outline="", tag="MineField")
                        self.cv.create_polygon(x+w//3, y+w//4, x+w//3 +10,  y + w//4 + 5, x+w//3, y + w//4 +10, fill=self.theme["Primary"]["warning"], outline="", tag="MineField")
                x += d
            x = self.xOffset
            y += d

    def start(self):
        self.stopReveal()
        self.active = True
        self.gameOver = False
        self.firstClick = True
        self.mf.placeMine()
        self.score = 0
        self.scoreMax = (( self.n * self.p ) - self.bomb) * self.step
        self.draw()
        if self.timer != None:
            self.timer.stop()
            self.timer.reset()

    def mkNotif(self, txt, color="Default"):
        """Faire des notifications sur le canvas."""
        if color == "Default":
            color = self.theme["Primary"]["notification"]

        w = self.cv.winfo_width()
        t = 2000
        idBlock = self.cv.create_rectangle(0, w-25, w , w, fill=color, outline="", tag="Notification")
        idTxt = self.cv.create_text(w//2, w-10, fill=self.theme["Primary"]["font"][1],font="Arial 17", text=txt, tag="Notification")
        self.root.after(t, lambda: self.cv.delete(idBlock, idTxt))

    def save(self):
        if self.gameOver:
            self.mkNotif("You cannot save when the game is over.", self.theme["Primary"]["warning"])
            return

        if self.revealLoopId == None:  # Si on est pas encore en train de reveler des cases sur le champs
            data = {"mf": self.mf,
                    "time": self.timer.save(),
                    "score": [self.score, self.scoreMax]}
            result = IE.save(data)

            if result == -1:
                self.mkNotif("An error occured while saving.", self.theme["Primary"]["warning"])
            else:
                self.mkNotif("Progress Saved.")
        else:
            self.mkNotif("Wait a bit before saving.", self.theme["Primary"]["warning"])
    def load(self):
        data = IE.load()
        if data != -1:  # Si on a pas eut d'erreur
            # On arrette tout revelation des cases en cours
            self.gameOver = False
            self.stopReveal()
            self.timer.stop()
            self.active = True
            self.firstClick = False  # On ne modifie pas le champs de mine lors du premier click vu qu'on veut charger un champs de mine
            self.mf = data["mf"]
            self.timer.load(data["time"])
            self.score, self.scoreMax = data["score"]
            self.draw()
            self.mkNotif("Progress has been loaded")
        else:
            self.mkNotif("Loading error: Couldn't access data.dem", "#AA3233")


    def select(self, i=None, j=None):
        self.cv.delete("MF_Selection")

        if i == None:
            self.selectionIndex = None
            if self.cheat:
                self.root.config(cursor="arrow")
            return
        else:
            self.selectionIndex = (i, j)

        case = self.mf.m[i][j]

        space = self.caseSpace
        w = self.caseSpace + self.caseLength
        x = w*j + self.xOffset
        y = w*i + self.yOffset

        if self.cheat:
            self.root.config(cursor="arrow")

        if ( case["visible"] ): # Si c'est un case revelé
            if case["value"] < 0:  # Si c'est une bombe
                self.cv.create_rectangle(x-space, y-space, x+w, y+w,fill=self.theme["Primary"]["warning"], outline="", tag="MF_Selection")
                self.cv.create_text(x+w//2, y+ w//2 +8, fill=self.theme["Primary"]["font"][1],font="Arial 20", text="*", tag="MF_Selection")
            elif case["value"] > 0:
                self.cv.create_rectangle(x-space, y-space, x+w, y+w, fill=self.theme["Primary"]["game"][1], outline="", tag="MF_Selection")
                self.cv.create_text(x+w//2, y+ w//2 +5, fill=self.theme["Primary"]["font"][1],font="Arial 20", text=case["value"], tag="MF_Selection")
            else:
                self.cv.create_rectangle(x-space, y-space, x+w, y+w,fill=self.theme["Primary"]["game"][1], outline="", tag="MF_Selection")

        else:  # Quand la case n'a pas deja ete revelé
            self.cv.create_rectangle(x-space, y-space, x+w, y+w,fill=self.theme["Primary"]["notification"], outline="", tag="MF_Selection")
            if case["flagged"]:
                self.cv.create_rectangle(x+w//3, y+w//4, x+w//3+2, y + w*3//4, fill=self.theme["Primary"]["game"][0], outline="", tag="MF_Selection")
                self.cv.create_polygon(x+w//3, y+w//4, x+w//3 +10,  y + w//4 + 5, x+w//3, y + w//4 +10, fill=self.theme["Primary"]["game"][0], outline="", tag="MF_Selection")

            if case["value"] < 0 and self.cheat and not self.firstClick:  # Si l'on est sur une bombe et que l'on triche
                self.root.config(cursor="circle")


    def reveal(self, list):
        """Affichage de toute les case au alentour lorsque l'on tombe sur une valeur de zero"""

        container = [-1, 0, 1]
        cases = []

        for indexCouple in list:
            i, j = indexCouple
            for k in container:
                for h in container:
                    iNext, jNext = i+k, j+h
                    if ( 0 <= iNext < self.n and 0 <= jNext < self.p):  # Si on est dans les limites du bord de l'ecran
                        case = self.mf.m[iNext][jNext]  # La nouvelle case a decouvrir
                        if not case["visible"]:  # Si c'est une case qui n'a pas deja ete decouverte

                            case["visible"] = True
                            self.score += self.step

                            if case["value"] == 0:  # Si c'est encore une case nulle,
                                # On ajoute une prochaine verification a effectuer.
                                cases.append((iNext, jNext))


        self.draw()

        if cases != []:  # S'il reste des cases a reveler
            self.revealLoopId = self.root.after(45, lambda: self.reveal(cases))
        else:
            self.revealLoopId = None

    def stopReveal(self):
        """Fonction pour arretter la boucle de revelation en cours, si il y en a une"""
        if self.revealLoopId != None:
            self.root.after_cancel(self.revealLoopId)
            self.revealLoopId = None

    def loose(self):
        """Lorsque l'on perd"""
        self.active = False
        self.timer.stop()
        for i in range(self.n):
            for j in range(self.p):
                case = self.mf.m[i][j]
                if case["value"] < 0:
                    case["visible"] = True
        self.draw()

        self.gameOver = True

    def win(self):
        """Lorsque l'on gagne"""
        self.active = False
        self.timer.stop()
        self.gameOver = True

    def updateOnMotion(self, coords):
        """Update on click"""
        x, y = coords


        if ( self.xOffset < x < self.xOffset + self.width and self.yOffset < y < self.yOffset + self.height ):
            d = self.caseLength + self.caseSpace  # Distance de l'espacement
            x, y = x-self.xOffset, y-self.yOffset # On commence a 0, 0
            j, i = x // d ,  y // d # On normalise les coordonnés en index

            if (i, j) != self.selectionIndex:
                self.select(i, j)
        else:
            self.select()

    def updateOnPress(self, state ="left"):

        if self.selectionIndex != None and self.active:  # Si on a une selection
            i, j = self.selectionIndex

            if state == "left":

                if self.firstClick: # Si c'est ble premier clique,
                    self.firstClick = False
                    self.mf.placeMine(i, j)  # On place les mine en fonction de l'emplacement du clique

                case = self.mf.m[i][j]

                if not case["visible"]:  # Si on avait pas deja clické sur cette case
                    case["visible"] = True
                    if not self.timer.isRunning():
                        self.timer.start()
                    if case["value"] == 0:
                        self.reveal([(i, j)])
                    elif case["value"] < 0:
                        self.loose()
                        print("Loose")


                    if case["value"] >= 0:
                        self.score += self.step
                        if self.score == self.scoreMax:
                            self.win()
                            print("Win")

            else:
                case = self.mf.m[i][j]
                # Cas ou c'est un click droit
                if not case["visible"]:
                    case["flagged"] = not case["flagged"]

            self.draw()
