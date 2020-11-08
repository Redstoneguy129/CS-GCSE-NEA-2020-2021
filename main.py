import json
import hashlib
import PIL.Image
import PIL.ImageTk
from tkinter import *
from enum import Enum
from os import path as path
from random import randint as ri


class Screen(Enum):
    LOGIN = "Login"
    GAME = "Game"
    SCORE = "Score"


openGame = True
currentScreen = Screen.LOGIN
youPlayerMain = None
opponentPlayerMain = None


def handle_focus_out(entry: Entry, string: str):
    entry.delete(0, END)
    entry.config(fg='grey')
    entry.insert(0, string)


def handle_focus_in(entry: Entry):
    entry.delete(0, END)
    entry.config(fg='black')


def create_entry(root: Tk, name: str, show: bool) -> Entry:
    entry = Entry(root, width=35, show="*") if not show else Entry(root, width=35)
    if show:
        entry.delete(0, END)
        entry.config(fg='grey')
        entry.insert(0, name)
        entry.bind("<FocusIn>", handle_focus_in(entry))
        entry.bind("<FocusOut>", handle_focus_out(entry, name))
    return entry


class Player:
    def __init__(self, isPlayer: bool):
        self.isPlayer = isPlayer
        self.turn = False
        self.scores = []
        self.score = 0

    def addScore(self, score: int):
        self.score += score

    def getIsPlayer(self) -> bool:
        return self.isPlayer

    def getTurn(self) -> bool:
        return self.turn

    def getScores(self) -> []:
        return self.scores


class LoginScreen:

    def __init__(self, root: Tk):
        self.label = Label(root)
        self.root = root
        self.username = create_entry(root, "Username", True)
        self.username.place(x=180, y=100, anchor=NW)
        self.password = create_entry(root, "Password", False)
        self.password.place(x=180, y=150, anchor=NW)
        Button(root, text="Login", command=self.login).place(x=180, y=180, anchor=NW)
        Button(root, text="Create", command=self.create).place(x=350, y=180, anchor=NW)
        root.bind("<Return>", self.login)

    def login(self):
        with open("DBData.json") as DBDataFile:
            DBDataSerial = json.load(DBDataFile)
            if not self.username.get() in DBDataSerial:
                self.label.destroy()
                self.label = Label(self.root, text="*That account does not exist!", fg="red",
                                   font='Comic-Sans 11 italic')
                self.label.place(x=185, y=75, anchor=NW)
            else:
                if DBDataSerial[self.username.get()] != hashlib.md5(
                        self.password.get().encode()).hexdigest():
                    self.label.destroy()
                    self.label = Label(self.root, text="*Username or Password is incorrect!", fg="red",
                                       font='Comic-Sans 11 italic')
                    self.label.place(x=163, y=75, anchor=NW)
                else:
                    global currentScreen
                    currentScreen = Screen.GAME
                    self.root.destroy()

    def create(self):
        with open("DBData.json") as DBDataFileRead:
            DBDataSerial = json.load(DBDataFileRead)
        if not self.username.get() in DBDataSerial:
            with open("DBData.json", "w") as DBDataFile:
                DBDataSerial[self.username.get()] = hashlib.md5(self.password.get().encode()).hexdigest()
                json.dump(DBDataSerial, DBDataFile)
        else:
            self.label.destroy()
            self.label = Label(self.root, text="*Account with that username already exists!", fg="red",
                               font='Comic-Sans 11 italic')
            self.label.place(x=150, y=75, anchor=NW)


class GameScreen:

    def __init__(self, root: Tk):
        self.root = root
        self.frame = 0
        self.rounds = 0
        self.topPlayer = None
        self.youPlayer = Player(True)
        self.youPlayer.turn = True
        self.OpponentPlayer = Player(False)
        Label(self.root, text="Click the Dice to roll", font='Comic-Sans 11 italic').place(x=217, y=50, anchor=NW)
        self.diceButton = Button(root, text="Roll!", command=self.rollDice)
        self.diceButton.place(x=220, y=100, anchor=NW)
        Label(self.root, text="Your Scores:", font='Comic-Sans 14').place(x=25, y=100, anchor=NW)
        self.youPlayerPrevScore = Label(self.root, text="Prev Score: " + str(0), font='Comic-Sans 11')
        self.youPlayerPrevScore.place(x=25, y=125, anchor=NW)
        self.youPlayerTotalScore = Label(self.root, text="Total Score: " + str(0), font='Comic-Sans 11')
        self.youPlayerTotalScore.place(x=25, y=150, anchor=NW)
        Label(self.root, text="Opponents Scores:", font='Comic-Sans 14').place(x=400, y=100, anchor=NW)
        self.OpponentPlayerPrevScore = Label(self.root, text="Prev Score: " + str(0), font='Comic-Sans 11')
        self.OpponentPlayerPrevScore.place(x=400, y=125, anchor=NW)
        self.OpponentPlayerTotalScore = Label(self.root, text="Total Score: " + str(0), font='Comic-Sans 11')
        self.OpponentPlayerTotalScore.place(x=400, y=150, anchor=NW)
        Label(self.root, text="Top Player:", font='Comic-Sans 14').place(x=235, y=270, anchor=NW)
        self.topPlayerLabel = Label(self.root, text="None", font='Comic-Sans 14 italic')
        self.topPlayerLabel.place(x=235, y=320, anchor=NW)
        self.updateDiceRoll(None, None)

    def getTopPlayer(self):
        self.topPlayerLabel.destroy()
        self.topPlayerLabel = Label(self.root, text="You" if self.topPlayer.getIsPlayer() else "Opponent",
                                    font='Comic-Sans 14 italic')
        self.topPlayerLabel.place(x=235, y=320, anchor=NW)

    def updateDiceRoll(self, frame: int, player: Player):
        image = PIL.Image.open("dice/Dice_" + str((frame if frame is not None else self.frame) + 1) + ".png")
        image.convert("RGB")
        image.resize((128, 128), PIL.Image.ANTIALIAS)
        img = PIL.ImageTk.PhotoImage(image)
        self.diceButton.configure(image=img)
        self.diceButton.image = img
        if frame is None:
            self.frame += 1
            if self.frame > 5:
                self.frame = 0
        else:
            if player is not None:
                player.addScore(frame + 1)
                if player == self.youPlayer:
                    if player.getTurn():
                        player.turn = False
                        self.youPlayer = player
                        self.root.after(0, self.updateDiceRoll, ri(0, 5), player)
                    else:
                        self.OpponentPlayer.turn = True
                        self.root.after(0, self.updateDiceRoll, ri(0, 5), self.OpponentPlayer)
                else:
                    if player.getTurn():
                        player.turn = False
                        self.OpponentPlayer = player
                        self.root.after(0, self.updateDiceRoll, ri(0, 5), player)
                    else:
                        self.youPlayerPrevScore.destroy()
                        self.youPlayerTotalScore.destroy()
                        self.OpponentPlayerPrevScore.destroy()
                        self.OpponentPlayerTotalScore.destroy()
                        self.youPlayer.scores.append(self.youPlayer.score)
                        self.youPlayerPrevScore = Label(self.root, text="Prev Score: " + str(self.youPlayer.score),
                                                        font='Comic-Sans 11')
                        self.youPlayerPrevScore.place(x=25, y=125, anchor=NW)
                        self.youPlayer.score = 0
                        self.OpponentPlayer.scores.append(self.OpponentPlayer.score)
                        self.OpponentPlayerPrevScore = Label(self.root,
                                                             text="Prev Score: " + str(self.OpponentPlayer.score),
                                                             font='Comic-Sans 11')
                        self.OpponentPlayerPrevScore.place(x=400, y=125, anchor=NW)
                        self.OpponentPlayer.score = 0
                        totalYouScore = 0
                        for i in self.youPlayer.scores:
                            totalYouScore += i
                        self.youPlayerTotalScore = Label(self.root, text="Total Score: " + str(totalYouScore),
                                                         font='Comic-Sans 11')
                        self.youPlayerTotalScore.place(x=25, y=150, anchor=NW)
                        totalOpponentScore = 0
                        for i in self.OpponentPlayer.scores:
                            totalOpponentScore += i
                        self.OpponentPlayerTotalScore = Label(self.root, text="Total Score: " + str(totalOpponentScore),
                                                              font='Comic-Sans 11')
                        self.OpponentPlayerTotalScore.place(x=400, y=150, anchor=NW)
                        self.topPlayer = self.youPlayer if totalYouScore > totalOpponentScore else self.OpponentPlayer
                        self.getTopPlayer()
                        self.rounds += 1
                        self.youPlayer.turn = True

    def rollDice(self):
        if self.rounds > 4:
            self.endGame()
        else:
            if self.youPlayer.getTurn():
                self.updateDiceRoll(ri(0, 5), self.youPlayer)

    def endGame(self):
        global youPlayerMain
        global opponentPlayerMain
        global currentScreen
        youPlayerMain = self.youPlayer
        opponentPlayerMain = self.OpponentPlayer
        currentScreen = Screen.SCORE
        self.root.destroy()


class ScoreScreen:

    def __init__(self, root: Tk):
        global youPlayerMain
        global opponentPlayerMain
        self.youTotalScore = 0
        self.opponentTotalScore = 0
        for i in youPlayerMain.scores:
            self.youTotalScore += i
        for i in opponentPlayerMain.scores:
            self.opponentTotalScore += i
        self.root = root
        Label(self.root, text="Winner: You" if self.youTotalScore > self.opponentTotalScore else "Winner: Opponent", font="Comic-Sans 15").place(x=205, y=75, anchor=NW)
        Label(self.root, text="With "+str(self.youTotalScore if self.youTotalScore > self.opponentTotalScore else self.opponentTotalScore)+" points", font="Comic-Sans 12").place(x=235, y=110, anchor=NW)
        Label(self.root, text="Lost: You" if self.youTotalScore < self.opponentTotalScore else "Winner: Opponent", font="Comic-Sans 15").place(x=205, y=160, anchor=NW)
        Label(self.root, text="With "+str(self.youTotalScore if self.youTotalScore > self.opponentTotalScore else self.opponentTotalScore)+" points", font="Comic-Sans 12").place(x=235, y=195, anchor=NW)


def trueClose(root: Tk, popup: Tk):
    global openGame
    openGame = False
    popup.destroy()
    root.destroy()


def CloseGame(root: Tk, name: str):
    global currentScreen
    if currentScreen != Screen.SCORE:
        popup = Tk()
        popup.config(height=200, width=400)
        popup.title(name)
        popup.resizable(False, False)
        Label(popup, text="Are you sure you want to exit the game?", font="Comic-Sans 14 bold").place(x=10, y=35, anchor=NW)
        Button(popup, text="Okay", command=lambda: trueClose(root, popup)).place(x=180, y=75, anchor=NW)
        popup.mainloop()
    else:
        global openGame
        openGame = False
        root.destroy()


def start(name: str) -> Tk:
    global currentScreen
    root = Tk()
    root.title(name)
    root.config(height=400, width=600)
    root.resizable(False, False)
    Label(root, text=currentScreen.value, font='Comic-Sans 18 bold').place(x=250, y=5, anchor=NW)
    LoginScreen(root) if currentScreen == Screen.LOGIN else GameScreen(
        root) if currentScreen == Screen.GAME else ScoreScreen(root) if currentScreen == Screen.SCORE else print(
        "Error occurred, code has been tampered with.")
    return root


if __name__ == '__main__':
    print("NEA Development - Cameron Whyte 2020")
    if not path.isfile("DBData.json"):
        DBData = open("DBData.json", "w")
        DBData.write("{}")
        DBData.close()
    while openGame:
        window = start("NEA Development Dice Game")
        window.protocol("WM_DELETE_WINDOW", lambda: CloseGame(window, "NEA Development Dice Game"))
        window.mainloop()