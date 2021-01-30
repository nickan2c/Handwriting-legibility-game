# importing inbuilt python libraries
from tkinter import *
import random
import time
# Importing my files
import client
from networkp import *
from database import *


class queue:  # used to select a prompt, and make sure the prompt isn't the same twice in a row
    def __init__(self, length):
        self.nums = []
        for i in range(1, length):
            self.nums.append(i)
        random.shuffle(self.nums)  # shuffles nums

    def refresh(self):
        self.last = self.dequeue()
        self.enqueue(self.last)
        return self.last

    def enqueue(self, item):
        self.nums.insert(0, item)  # puts it a front. Didn't use append since pop returns final element of list,
        # so adding to queue from the front makes it easier

    def dequeue(self):
        return self.nums.pop()


class tkinter_windows:

    def __init__(self):
        self.db = database()  # association- composition
        self.login_success = False

    def _start_screen(self):
        self.root = Tk()
        self.root.geometry("300x250")  # set window size
        self.root.title("Handwriting tester")  # set window title

        Label(text="Please Select Your Choice", bg="white", width="20", height="2").pack()  # pack puts it into screen
        Label(text="").pack()  # leaves a gap for aesthetic purposes

        Button(text="Leaderboard", height="2", width="15",
               command=self.__leaderboard).pack()  # upon clicking, calls login function
        Label(text="").pack()

        Button(text="play", height="2", width="15",
               command=self.__main_screen).pack()  # upon clicking, calls register function

        self.root.mainloop()

    def __main_screen(self):
        self.__main_screen = Toplevel(self.root)  # create window
        self.__main_screen.geometry("300x250")  # set window size
        self.__main_screen.title("Account selection")  # set window title

        Label(self.__main_screen, text="Please Select Your Choice", bg="white", width="20",
              height="2").pack()  # pack puts it into screen
        Label(self.__main_screen, text="").pack()  # leaves a gap for aesthetic purposes

        Button(self.__main_screen, text="Login", height="2", width="15",
               command=self.__login).pack()  # upon clicking, calls login function
        Label(self.__main_screen, text="").pack()

        Button(self.__main_screen, text="Register", height="2", width="15",
               command=self.__register).pack()  # upon clicking, calls register function
        Label(self.__main_screen, text="").pack()

        Button(self.__main_screen, text="Continue", height="2", width="15", command=self.__continue).pack()

    def __register(self):
        self.register_screen = Toplevel(self.__main_screen)  # like a stack
        self.register_screen.title("Register")
        self.register_screen.geometry("300x250")

        # define how the text entered will be stored
        self.username = StringVar()
        self.password = StringVar()

        Label(self.register_screen, text="Please enter your details below").pack()
        Label(self.register_screen, text="").pack()

        username_label = Label(self.register_screen, text="Username * ")
        username_label.pack()

        self.username_entry = Entry(self.register_screen, textvariable=self.username)
        self.username_entry.pack()

        password_label = Label(self.register_screen, text="Password * ")
        password_label.pack()

        self.password_entry = Entry(self.register_screen, textvariable=self.password, show='*')
        self.password_entry.pack()

        Label(self.register_screen, text="").pack()
        Button(self.register_screen, text="Register", width=10, height=1, bg="blue",
               command=self.__register_user).pack()

    def __register_user(self):
        def register_failed(error_msg):
            register_failed_screen = Toplevel(self.register_screen)
            register_failed_screen.title("Error")
            register_failed_screen.geometry("150x100")

            Label(register_failed_screen, text=error_msg).pack()
            Button(register_failed_screen, text="OK", command=register_failed_screen.destroy).pack()

        def register_success():
            register_success_screen = Toplevel(self.register_screen)
            register_success_screen.title("Success")
            register_success_screen.geometry("150x100")

            Label(register_success_screen, text="You have been registered").pack()
            Label(register_success_screen, text="You may now login").pack()

            Button(register_success_screen, text="OK", command=register_success_screen.destroy).pack()

        password = str(self.password.get())
        username = str(self.username.get())

        if 3 > len(username) or len(username) > 20:  # username length
            register_failed('that username length is invalid')
        elif ' ' in password or ' ' in username:  # no whitespace
            register_failed('Must not have spaces. Use underscores instead(_)')
        elif not username.isalnum():
            register_failed('Username must be alphanumeric')
        elif not username[0].isalpha():  # first letter must be capital
            register_failed('First character must be a letter')
        elif len(password) < 8:  # password length
            register_failed('password must be longer than 8 characters')
        elif self.db.user_in_db(username):
            register_failed('That username is already in use')
        else:
            self.db.insert(username, password)
            register_success()

    def __login(self):
        self.login_screen = Toplevel(self.__main_screen)
        self.login_screen.title("Login")
        self.login_screen.geometry("300x250")

        Label(self.login_screen, text="Please enter your details below").pack()
        Label(self.login_screen, text="").pack()

        # define how the text entered will be stored
        self.username_to_verify = StringVar()
        self.password_to_verify = StringVar()

        Label(self.login_screen, text="Username * ").pack()

        self.username_login_entry = Entry(self.login_screen, textvariable=self.username_to_verify).pack()

        Label(self.login_screen, text="").pack()
        Label(self.login_screen, text="Password * ").pack()

        self.password_login_entry = Entry(self.login_screen, textvariable=self.password_to_verify, show='*').pack()

        def login_success():
            self.login_success_screen = Toplevel(self.login_screen)
            self.login_success_screen.title("Success")
            self.login_success_screen.geometry("150x100")

            Label(self.login_success_screen, text="Login Success").pack()
            Button(self.login_success_screen, text="OK", command=self.login_success_screen.destroy).pack()

            self.login_success = True

        def login_failed(error_msg):
            self.login_failed_screen = Toplevel(self.login_screen)
            self.login_failed_screen.title("Error")
            self.login_failed_screen.geometry("150x100")

            Label(self.login_failed_screen, text=error_msg).pack()
            Button(self.login_failed_screen, text="OK", command=self.login_failed_screen.destroy).pack()
            self.login_success = False

        def login_verify():
            self.username = self.username_to_verify.get()
            self.password = self.password_to_verify.get()

            if self.db.user_password_match(self.username, self.password):
                login_success()
            else:
                login_failed('invalid credentials')

        Label(self.login_screen, text="").pack()
        Button(self.login_screen, text="Confirm Login", width=10, height=1, command=login_verify).pack()

    def __continue(self):
        self.__continue_screen = Toplevel(self.__main_screen)  # like a stack
        self.__continue_screen.title("Welcome!")
        self.__continue_screen.geometry("500x350")

        Label(self.__continue_screen,
              text="Welcome to the handwriting game - digit edition! \n In this game you will be tested on how neatly "
                   "you can write numbers.\n The computer will read your writing, \n and will give you an overall "
                   "score for how legible your writing was!\n").pack()

        Label(self.__continue_screen, text="").pack()
        Label(self.__continue_screen, text="").pack()
        if self.login_success:
            Label(self.__continue_screen, text="You are logged in").pack()

            Button(self.__continue_screen, text='Play with a friend!', width=15, height=1,
                   command=self.__play_with_friend).pack()

        elif not self.login_success:
            Label(self.__continue_screen,
                  text="You are not logged in. Log in to be able to save your score, and play with a friend!.").pack()

        Button(self.__continue_screen, text='Play solo!', width=15, height=1, command=self.__selection).pack()

    def __play_with_friend(self):
        self.__pw_friend = Toplevel(self.__continue_screen)  # like a stack
        self.__pw_friend.title("Selections")
        self.__pw_friend.geometry("400x300")
        self.n = Network()
        Label(self.__pw_friend, text="Connected to the server.").pack()
        self.n.send((self.username, 'init'))
        while True:
            users = self.n.send(('play?', 'game'))  # are they both loaded in?
            if len(users) == 2:  # waits until they have both loaded to break
                break

        def startw_friend():
            self.n.send((int(self.num_images_selected.get()), 'num_games'))
            num_games = self.n.send(('', 'num_games?'))
            Label(self.__pw_friend, text=f'There will be {num_games} rounds').pack()
            Button(self.__pw_friend, text='begin', width=15, height=2,
                   command=lambda: self.__beginw_friend(num_games, player=1)).pack()

        if self.username == users[0]:  # whoever loaded in first
            Label(self.__pw_friend, text="You are player 1! You get to choose the number of games.").pack()
            self.num_images_selected = StringVar()

            optionList = []
            for i in range(1, 20):
                optionList.append(str(i))

            self.num_images_selected.set(optionList[0])

            Label(self.__pw_friend, text='Select the number of images you would like to go through').pack()
            OptionMenu(self.__pw_friend, self.num_images_selected, *optionList).pack()  # drop down menu

            Button(self.__pw_friend, text='confirm', width=15, height=2,
                   command=startw_friend).pack()

        elif self.username == users[1]:
            Label(self.__pw_friend, text=f"You are player 2! Wait until player 1 ({users[0]}) selects").pack()

            while True:
                reply = self.n.send(('selected?', 'selected?'))  # are they both loaded in?
                if reply == 'yes':  # if replies yes then continues
                    num_games = self.n.send(('', 'num_games?'))
                    Label(self.__pw_friend, text=f'There will be {num_games} rounds').pack()
                    Button(self.__pw_friend, text='begin', width=15, height=2,
                           command=lambda: self.__beginw_friend(num_games, player=2)).pack()
                    break

    def __beginw_friend(self, num_games, player):
        client.server_predict(self.root, player, num_games, self.login_success)

        self.accuracy = 0
        self.num_correct = 0
        self.num_attempts = 0

        self.__begin_screen = Tk()  # don't want this to be a top level of anything, since i want to keep this open
        self.__begin_screen.title("Results")
        self.__begin_screen.geometry("300x250")

        if self.login_success:
            self.db.insert_results(str(self.username))  # This creates a resultID for the user so that when rounds
            # are being inserted into db, there is a valid resultID

        self.result_button = Button(self.__begin_screen, text='Get results', width=15, height=2,
                                    command=lambda: self.__get_results_friend(player))
        self.result_button.pack()

        self.__begin_screen.mainloop()

    def __leaderboard(self):
        self.__leaderboard_screen = Toplevel(self.root)  # like a stack
        self.__leaderboard_screen.title("Leaderboard")
        self.__leaderboard_screen.geometry("400x350")

        self.username_to_search = StringVar()

        leaders = self.db.display_leaderboard()

        row1 = 'Username,accuracy, number of attempts, number correct'
        Label(self.__leaderboard_screen, text=row1).pack()
        for row in leaders:
            Label(self.__leaderboard_screen, text=f'{row[0]} | {row[1]} | {row[2]} | {row[3]} ').pack()

        self.search_username = Entry(self.__leaderboard_screen, textvariable=self.username_to_search).pack()
        Button(self.__leaderboard_screen, text='search username', width=15, height=2,
               command=self.__find_username).pack()

    def __find_username(self):
        user = str(self.username_to_search.get())  # gets entered text
        scores = self.db.get_user_scores(user)  # returns sql statement that grabs all scores by that username
        row1 = 'Round num, Correct, Prompt, Seen, Certainty(%)'
        Label(self.__leaderboard_screen, text=row1).pack()
        for row in scores:
            Label(self.__leaderboard_screen, text=row).pack()

    def __selection(self):
        self.__selection_screen = Toplevel(self.__continue_screen)  # like a stack
        self.__selection_screen.title("Selections")
        self.__selection_screen.geometry("400x300")
        self.num_images_selected = StringVar()

        optionList = []
        for i in range(1, 20):
            optionList.append(str(i))

        self.num_images_selected.set(optionList[0])

        Label(self.__selection_screen, text='Select the number of images you would like to go through').pack()
        OptionMenu(self.__selection_screen, self.num_images_selected, *optionList).pack()  # drop down menu

        Label(self.__selection_screen, text='Select the number of images you would like to go through').pack()

        Button(self.__selection_screen, text='begin', width=15, height=2, command=self.__begin).pack()

    def __begin(self):
        num_images = int(self.num_images_selected.get())

        client.server_predict(self.root, 1, num_images, self.login_success)

        self.accuracy = 0
        self.num_correct = 0
        self.num_attempts = 0

        self.__begin_screen = Tk()  # don't want this to be a top level of anything, since i want to keep this open
        self.__begin_screen.title("Results")
        self.__begin_screen.geometry("300x250")

        if self.login_success:
            self.db.insert_results(str(self.username))  # This creates a resultID for the user so that when rounds
            # are being inserted into db, there is a valid resultID

        self.result_button = Button(self.__begin_screen, text='Get results', width=15, height=2,
                                    command=self.__get_results)
        self.result_button.pack()

        self.__begin_screen.mainloop()

    def __get_results(self):

        certainties = []
        correct = False
        self.result_button.destroy()  # destroy button so that user cannot press multiple times

        f = open('user_score1.txt', 'r')

        for row in f:
            new_row = row[:-1]  # remove \n by list slicing
            attempt_num = int(new_row[0])  # first digit
            prompt = int(new_row[2])  # next digit, after whitespace
            guess = int(new_row[4])  # next digit, after whitespace
            certainty = int(new_row[6:])  # rest of the string, after whitespace
            certainties.append(certainty)

            Label(self.__begin_screen,
                  text=f"Image number{attempt_num}\n You should have drawn a {prompt}.\n I think that's a {guess} I'm {certainty}% certain").pack()
            if guess == prompt and certainty > 60:
                correct = True
                self.num_correct += 1
                Label(text=" Great drawing!").pack()

            else:
                Label(text=" You've not drawn that well enough for me to recognise it.").pack()
            self.num_attempts += 1

            if self.login_success:
                self.db.insert_round(str(self.username), attempt_num, correct, prompt, guess, certainty)

        if self.login_success:

            self.db.c.execute('select UserID from Users Where username = ?', (self.username,))
            userID = self.db.c.fetchone()[0]

            self.db.c.execute('''SELECT MAX(ResultID)
                                        FROM Users, Results
                                        Where Results.UserID = Users.UserID
                                        ''')
            newest_resultID = self.db.c.fetchone()[0]

            # gets average accuracy of user rounds
            self.db.c.execute('''SELECT AVG(Rounds.certainty)
                    FROM Rounds, Users, Results
                    Where (Users.UserID = Rounds.UserID) AND (Results.UserID = Rounds.UserID) 
                    AND Users.UserID = ?
                    AND Rounds.ResultID = ?
                    AND Rounds.Correct = ?
                    ''', (userID, newest_resultID, 'Yes'))

            self.accuracy = self.db.c.fetchone()[0]

            if self.accuracy is None:
                self.accuracy = 0
            self.db.update_results(self.username, self.accuracy, self.num_attempts, self.num_correct)

    def __get_results_friend(self, player):  # split page into 2, top for u and bot for friend
        certainties = []
        correct = False
        self.result_button.destroy()  # destroy button so that user cannot press multiple times

        f = open(f'user_score{player}.txt', 'r')
        Label(self.__begin_screen, text=f"Player {player} (you)").pack()
        for row in f:
            new_row = row[:-1]  # remove \n by list slicing
            attempt_num = int(new_row[0])  # first digit
            prompt = int(new_row[2])  # next digit, after whitespace
            guess = int(new_row[4])  # next digit, after whitespace
            certainty = int(new_row[6:])  # rest of the string, after whitespace
            certainties.append(certainty)

            Label(self.__begin_screen,
                  text=f"Image number{attempt_num}\n You should have drawn a {prompt}.\n I think that's a {guess} I'm {certainty}% certain").pack()
            if guess == prompt and certainty > 60:
                correct = True
                self.num_correct += 1
                Label(text=" Great drawing!").pack()

            else:
                Label(text=" You've not drawn that well enough for me to recognise it.").pack()
            self.num_attempts += 1

            if self.login_success:
                self.db.insert_round(str(self.username), attempt_num, correct, prompt, guess, certainty)

        Label(text='').pack()

        while True:
            time.sleep(1)  # to not overload the network, check every second.
            if self.n.send(('ready?', 'ready?')) == 'yes':
                break

        if player == 1:
            Label(self.__begin_screen, text="Player 2").pack()
            f = open('user_score2.txt', 'r')
            for row in f:
                new_row = row[:-1]  # remove \n by list slicing
                attempt_num = int(new_row[0])  # first digit
                prompt = int(new_row[2])  # next digit, after whitespace
                guess = int(new_row[4])  # next digit, after whitespace
                certainty = int(new_row[6:])  # rest of the string, after whitespace
                certainties.append(certainty)

                Label(self.__begin_screen,
                      text=f"Image number{attempt_num}\n You should have drawn a {prompt}.\n I think that's a {guess} I'm {certainty}% certain").pack()
                if guess == prompt and certainty > 60:
                    self.num_correct += 1
                    Label(text=" Great drawing!").pack()

                else:
                    Label(text=" You've not drawn that well enough for me to recognise it.").pack()
                self.num_attempts += 1

        elif player == 2:
            Label(self.__begin_screen, text="Player 1").pack()
            f = open('user_score1.txt', 'r')
            for row in f:
                new_row = row[:-1]  # remove \n by list slicing
                attempt_num = int(new_row[0])  # first digit
                prompt = int(new_row[2])  # next digit, after whitespace
                guess = int(new_row[4])  # next digit, after whitespace
                certainty = int(new_row[6:])  # rest of the string, after whitespace
                certainties.append(certainty)

                Label(self.__begin_screen,
                      text=f"Image number{attempt_num}\n You should have drawn a {prompt}.\n I think that's a {guess} I'm {certainty}% certain").pack()
                if guess == prompt and certainty > 60:
                    self.num_correct += 1
                    Label(text=" Great drawing!").pack()

                else:
                    Label(text=" You've not drawn that well enough for me to recognise it.").pack()
                self.num_attempts += 1

        if self.login_success:

            self.db.c.execute('select UserID from Users Where username = ?', (self.username,))
            userID = self.db.c.fetchone()[0]

            self.db.c.execute('''SELECT MAX(ResultID)
                                                FROM Users, Results
                                                Where Results.UserID = Users.UserID
                                                ''')
            newest_resultID = self.db.c.fetchone()[0]

            # gets average accuracy of user rounds
            self.db.c.execute('''SELECT AVG(Rounds.certainty)
                            FROM Rounds, Users, Results
                            Where (Users.UserID = Rounds.UserID) AND (Results.UserID = Rounds.UserID) 
                            AND Users.UserID = ?
                            AND Rounds.ResultID = ?
                            AND Rounds.Correct = ?
                            ''', (userID, newest_resultID, 'Yes'))

            self.accuracy = self.db.c.fetchone()[0]

            if self.accuracy is None:
                self.accuracy = 0
            self.db.update_results(self.username, self.accuracy, self.num_attempts, self.num_correct)

        Label(text=f'Overall accuracy:{self.accuracy}. You got {self.num_correct} correct!')


win = tkinter_windows()
win._start_screen()
