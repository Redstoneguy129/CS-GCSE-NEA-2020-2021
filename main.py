import json
import hashlib
import PIL.Image
import PIL.ImageTk
from tkinter import *
from enum import Enum
from os import path as path
from random import randint as ri

"""
NEA Development - Cameron Whyte 2020
This was made by Cameron Whyte
"""


class Screen(Enum):
    """
    Class to create Enums i'll use to identify the current screen
    """
    LOGIN = "Login"
    GAME = "Game"
    SCORE = "Score"


openGame = True  # Keeps the Tkinter root instance running.
currentScreen = Screen.LOGIN  # Sets the screen to LOGIN so when user runs program it goes straight to the screen.
youPlayerMain = None  # User has not been defined yet so setting to None will say it exists.
opponentPlayerMain = None  # Bot has not been defined yet so setting to None will say it exists.


def handle_focus_out(entry: Entry, string: str):
    """
    :param entry:
    :param string:

    Nice method for the entry boxes in Login screen, makes text grey when not editing.
    """
    entry.delete(0, END)
    entry.config(fg='grey')
    entry.insert(0, string)


def handle_focus_in(entry: Entry):
    """
    :param entry:

    Nice method for the entry boxes in Login screen, makes text black when editing.
    """
    entry.delete(0, END)
    entry.config(fg='black')


def create_entry(root: Tk, name: str, show: bool) -> Entry:
    """
    :param root:
    :param name:
    :param show:
    :return:

    Creates the Entry box for username and password, also links them to the focus handler methods.
    """
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
        """
        :param isPlayer:

        Player class for accessing the scores, turns and score list.
        Can be used to identify if current roller is a bot or not.
        Stores scores throughout the game here.
        """
        self.isPlayer = isPlayer
        self.turn = False
        self.scores = []
        self.score = 0

    def addScore(self, score: int):
        """
        Adds the given score to the players total score for that round.
        :param score:
        :return:
        """
        self.score += score

    def getIsPlayer(self) -> bool:
        """
        If player isn't the bot then it returns True as it's a real player.
        :return:
        """
        return self.isPlayer

    def getTurn(self) -> bool:
        """
        If player is rolling it returns true.
        This is used to determine the rolls user has lest in the :UpdateDiceRoll method.
        :return:
        """
        return self.turn

    def getScores(self) -> []:
        """
        Returns the list of scores from the whole game.
        :return:
        """
        return self.scores


class LoginScreen:

    def __init__(self, root: Tk):
        """
        :param root:

        This is the screen where if enabled the user needs to either create an account or login to an existing one.
        """
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
        """
        :return:

        Logs in with credentials given, if incorrect or does not exist then gives error.
        """
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
        """
        :return:

        Creates an account for the new user to play the game.
        Also uses an MD5 Hashing algorithm to encrypt the passwords so if someone views json file they wont know the password.
        """
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
        """
        The Game screen is the main part of the game.
        This method registers the labels and buttons for the screen.
        :param root:
        """
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
        """
        Returns the top player as You or Opponent.
        :return:
        """
        self.topPlayerLabel.destroy()
        self.topPlayerLabel = Label(self.root, text="You" if self.topPlayer.getIsPlayer() else "Opponent",
                                    font='Comic-Sans 14 italic')
        self.topPlayerLabel.place(x=235, y=320, anchor=NW)

    def updateDiceRoll(self, frame: int, player: Player):
        """
        Changes the dice texture while also editing the scores and setting turns.
        :param frame:
        :param player:
        :return:
        """
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
        """
        When player clicks the dice this method runs.
        If the 5th round hasn't occurred yet then it updates the dice roll method.
        If the 5th round has occurred then it ends the game and continues to the Score screen with the scores collected from the players.
        :return:
        """
        if self.rounds > 4:
            self.endGame()
        else:
            if self.youPlayer.getTurn():
                self.updateDiceRoll(ri(0, 5), self.youPlayer)

    def endGame(self):
        """
        Ends the game and switches to the Score screen.
        :return:
        """
        global youPlayerMain
        global opponentPlayerMain
        global currentScreen
        youPlayerMain = self.youPlayer
        opponentPlayerMain = self.OpponentPlayer
        currentScreen = Screen.SCORE
        self.root.destroy()


class ScoreScreen:

    def __init__(self, root: Tk):
        """
        Method that determines the winner of the game.
        Lists on both sides of the screen the scores of both players.
        Buttons that allow the player to play again or close the program through the main windows close button or the button next to play again.
        :param root:
        """
        global youPlayerMain
        global opponentPlayerMain
        self.root = root
        self.youTotalScore = 0
        self.opponentTotalScore = 0
        Label(self.root, text="You", font="Comic-Sans 12 bold").place(x=10, y=90, anchor=NW)
        Label(self.root, text="Opponent", font="Comic-Sans 12 bold").place(x=445, y=90, anchor=NW)
        p = 0
        l = 0
        for i in youPlayerMain.scores:
            l += 1
            self.youTotalScore += i
            Label(self.root, text="Round " + str(l) + ":   " + str(i) + " points", font="Comic-Sans 12").place(x=10,
                                                                                                               y=110 + p,
                                                                                                               anchor=NW)
            p += 25
        p = 0
        l = 0
        for i in opponentPlayerMain.scores:
            l += 1
            self.opponentTotalScore += i
            Label(self.root, text="Round " + str(l) + ":   " + str(i) + " points", font="Comic-Sans 12").place(x=445,
                                                                                                               y=110 + p,
                                                                                                               anchor=NW)
            p += 25
        Label(self.root, text="Winner: You" if self.youTotalScore > self.opponentTotalScore else "Winner: Opponent",
              font="Comic-Sans 15").place(x=205, y=75, anchor=NW)
        Label(self.root, text="With " + str(
            self.youTotalScore if self.youTotalScore > self.opponentTotalScore else self.opponentTotalScore) + " points",
              font="Comic-Sans 12").place(x=235, y=110, anchor=NW)
        Label(self.root, text="Lost: You" if self.youTotalScore < self.opponentTotalScore else "Winner: Opponent",
              font="Comic-Sans 15").place(x=205, y=160, anchor=NW)
        Label(self.root, text="With " + str(
            self.youTotalScore if self.youTotalScore < self.opponentTotalScore else self.opponentTotalScore) + " points",
              font="Comic-Sans 12").place(x=235, y=195, anchor=NW)
        Button(root, text="Play Again", command=self.PlayAgain, width=12, height=2).place(x=150, y=250, anchor=NW)
        Button(root, text="End Game", command=lambda: CloseGame(self.root, None), width=12, height=2).place(x=300,
                                                                                                            y=250,
                                                                                                            anchor=NW)

    def PlayAgain(self):
        """
        Play again changes the current screen to Game and destroys its parent window.
        :return:
        """
        global youPlayerMain, opponentPlayerMain, currentScreen
        youPlayerMain = None
        opponentPlayerMain = None
        currentScreen = Screen.GAME
        self.root.destroy()


def trueClose(root: Tk, popup: Tk):
    """
    Actually closes the window if popup is okay.
    :param root:
    :param popup:
    :return:
    """
    global openGame
    openGame = False
    popup.destroy()
    root.destroy()


def CloseGame(root: Tk, name: str):
    """
    Checks if score screen to see if should open or popup or close game straight away.
    :param root:
    :param name:
    :return:
    """
    global currentScreen
    if currentScreen != Screen.SCORE:
        popup = Tk()
        popup.config(height=200, width=400)
        popup.title(name)
        popup.resizable(False, False)
        Label(popup, text="Are you sure you want to exit the game?", font="Comic-Sans 14 bold").place(x=10, y=35,
                                                                                                      anchor=NW)
        Button(popup, text="Okay", command=lambda: trueClose(root, popup)).place(x=180, y=75, anchor=NW)
        popup.mainloop()
    else:
        global openGame
        openGame = False
        root.destroy()


def start(name: str) -> Tk:
    """
    Starts the screens using Tkinter.
    Returns the root back to the main method.
    :param name:
    :return:
    """
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
    """
    Creates a json DB file is isn't already created for storing passwords.
    Starts a loop for the Tkinter screen.
    Also overwrites the default windows close event for popups to ask if user is sure.
    """
    print("NEA Development - Cameron Whyte 2020")
    if not path.isfile("DBData.json"):
        DBData = open("DBData.json", "w")
        DBData.write("{}")
        DBData.close()
    while openGame:
        window = start("NEA Development Dice Game")
        window.protocol("WM_DELETE_WINDOW", lambda: CloseGame(window, "NEA Development Dice Game"))
        window.mainloop()
