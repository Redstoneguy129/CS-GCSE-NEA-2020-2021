import io
import re
import os
import json
import base64
import hashlib
from tkinter import *
from enum import Enum
from io import BytesIO
from os import path as path
from sys import path as syspath
from random import randint as ri

syspath.append(os.getcwd() + "\\dependencies")  # Adds the external dependencies PIL.
import PIL.Image
import PIL.ImageTk

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


dices = [
    "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"]
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
        image = PIL.Image.open(io.BytesIO(base64.b64decode(re.sub("^data:image/.+;base64,", '', dices[frame if frame is not None else self.frame]))))
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
                        self.root.after(600, self.updateDiceRoll, ri(0, 5), player)
                    else:
                        self.OpponentPlayer.turn = True
                        self.root.after(600, self.updateDiceRoll, ri(0, 5), self.OpponentPlayer)
                else:
                    if player.getTurn():
                        player.turn = False
                        self.OpponentPlayer = player
                        self.root.after(600, self.updateDiceRoll, ri(0, 5), player)
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
