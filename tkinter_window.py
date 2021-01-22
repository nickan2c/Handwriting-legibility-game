from tkinter import *
import sqlite3
import os
import hashlib

import client


def hash_password(password, salt=None):
    '''
    If user has already got a salt, then that will be passed in as salt parameter. If not, salt is defined as None, and
    so a new salt is generated for them.
    hashes password using hashlib
    :param password:
    :param salt:
    :return: hashed password, salt
    '''
    if salt == None:
        salt = os.urandom(16)  # randomly generates a 16 bit binary string if the user is registering, otherwise uses
        # their salt that was assigned.
    password = str(password)
    hashed = hashlib.pbkdf2_hmac('sha256',  # The hash digest algorithm for hmac
                                 password.encode('utf-8'),  # Convert the password into bytes
                                 salt, 1000  # number of iterations of hash- more iterations makes it more secure
                                 )

    return hashed, salt


class database:

    def __init__(self):
        self.conn = sqlite3.connect('HandwritingUsers')  # establishes connection with database
        self.c = self.conn.cursor()

        # this is used to solve the problem of the c.fetchall() function returning a unicode string rather than utf-8
        # before, it would return " u'username' " now with this line it returns " 'username' "
        self.conn.text_factory = str

        self.c.execute('''CREATE TABLE IF NOT EXISTS Users(
                  UserID integer NOT NULL PRIMARY KEY,
                  username text NOT NULL,
                  pw_hashed text NOT NULL,
                  salt  text    NOT NULL
                  )''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS Results(
                         ResultID integer NOT NULL PRIMARY KEY,
                         UserID integer NOT NULL,
                         Overall_accuracy integer,
                         num_attempts integer,
                         num_correct integer
                         )''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS  Rounds(
                          RoundID integer NOT NULL,
                          UserID integer NOT NULL,
                          ResultID integer NOT NULL,
                          Correct text,
                          Number_to_draw integer,
                          Number_drawn integer,
                          Certainty integer,
                          primary key (RoundID, UserID,ResultID)
                          )''')
        self.conn.commit()

    def user_in_db(self, username):
        '''
        check if user is in database
        :param username:
        :return True:
        '''
        self.c.execute("select * From Users where username = ?", (username,))
        fetched = self.c.fetchone()
        if fetched == None:
            return False
        return True

    def insert(self, username, password):
        '''
        inserts the username into the database, and also hashes the password, then stores the salt,password,username.
        :param username StringVar:
        :param password str:
        :return:
        '''
        username = str(username)
        password = str(password)
        pw_hashed, salt = hash_password(password)  # no salt provided, default provided as none
        self.c.execute("INSERT INTO Users(username,pw_hashed,salt) VALUES(?,?,?)",
                       (username, pw_hashed, salt))  # used parameterised sql to prevent sql injection
        self.conn.commit()
        print('Your information has been added!')

    def user_password_match(self, username, entered_password):
        '''
        Check if username and password match
        :param username:
        :param entered_password:
        :return:
        '''
        self.c.execute(" SELECT username, salt FROM Users WHERE username = ?", (username,))
        fetched = self.c.fetchone()
        if fetched == None:
            print('user not registered')
            return False
        else:
            their_salt = fetched[1]  # grabbed salt of the user from the database
            pw_hashed, salt = hash_password(entered_password, their_salt)  # used their salt to hash the password
            # they entered. If match, they are given access

            self.c.execute(
                " SELECT username, pw_hashed, salt FROM Users WHERE username = ? AND pw_hashed = ? ",
                (username, pw_hashed))
            user_details = self.c.fetchall()

            if len(user_details) == 0:
                print('not in database')
                return False
            else:
                print('you"re in')
                return True

    def display_leaderboard(self):
        self.c.execute('''SELECT Users.username, Results.Overall_accuracy,Results.num_attempts,Results.num_correct
        FROM Users,Results 
        WHERE Users.UserID = Results.UserID 
        AND Results.num_attempts != 0
        ORDER BY Results.Overall_accuracy DESC
        ''')  # don't want to display people who haven't attempted the game yet

        return self.c.fetchmany(5)  # returns top 5

    def get_user_scores(self, user):  # get every round user has done, and display
        '''

        :param user:
        :return: list of Rounds that user has done, list
        '''
        username = str(user)
        try:
            self.c.execute('select UserID from Users Where username = ?', (username,))
            their_UserID = self.c.fetchone()[0]

            self.c.execute('''SELECT Rounds.RoundID, Rounds.Correct, Rounds.Number_to_draw, Rounds.Number_drawn, Rounds.certainty
                            FROM Rounds
                            WHERE Rounds.UserID = ?
                            ''', (their_UserID,))
        except TypeError:
            print('nothing entered')
            return ['nothing entered']

        return self.c.fetchall()

    def insert_round(self, user, attempt_num, correct, num_to_draw, num_drawn, certainty):
        '''
        :param user: StringVar, username. stringvar since it is a tkinter entry. converted to string below
        :param attempt_num: int
        :param correct: Bool
        :param num_to_draw: int
        :param num_drawn: int
        :param certainty: int
        :return: nothing
        Adds row to round table, using text file
        '''
        user = str(user)
        if correct:
            correct = 'Yes'
        else:
            correct = 'no'

        self.c.execute('select UserID from Users where username = ?', (user,))
        userID = self.c.fetchone()[0]

        self.c.execute('select ResultID from Results where userID = ?', (userID,))

        resultID = self.c.fetchall()  # want to find most recent result ID for updating. Since resultID auto increment,
        # the most recent will be the largest. Therefore I can find the maximum value in the list c.fetchall()
        resultID = max(resultID)[0]

        self.c.execute(
            'insert into Rounds(RoundID,UserID,ResultID, Correct,Number_to_draw, Number_drawn, Certainty) VALUES(?,?,?,?,?,?,?)',
            (attempt_num, userID, resultID, correct, num_to_draw, num_drawn, certainty))
        self.conn.commit()
        # self.c.execute('select * from Rounds ')
        # print(self.c.fetchall())

    def insert_results(self, username, accuracy=None, num_attempts=None, num_correct=None):
        '''

        :param username:
        :param accuracy: how certain the network was.
        :param num_attempts:
        :param num_correct:
        :return:
        '''

        # when first
        # creating result row, these values are none until the game ends, and they can be determined
        user = str(username)
        self.c.execute('select UserID from Users where username = ?', (user,))
        userID = self.c.fetchone()[0]
        self.c.execute(
            'insert into Results(UserID, Overall_accuracy,num_attempts, num_correct) VALUES(?,?,?,?)',
            (userID, accuracy, num_attempts, num_correct))
        self.c.execute('select * from Results')
        # print(self.c.fetchall())
        self.conn.commit()

    def update_results(self, username, accuracy, num_attempts, num_correct):  # when first
        # creating result row, these values are none until the game ends, and they can be determined
        user = str(username)
        self.c.execute('select UserID from Users where username = ?', (user,))
        userID = self.c.fetchone()[0]
        self.c.execute('select MAX(ResultID) from Results where userID = ?', (userID,))

        resultID = self.c.fetchall()  # want to find most recent result ID for updating. Since resultID auto increment,
        # the most recent will be the largest. Therefore I can find the maximum value in the list c.fetchall()
        resultID = resultID[0][0]

        self.c.execute(
            "Update Results SET(Overall_accuracy,num_attempts, num_correct) = (?,?,?) where UserID =? and ResultID = ?",
            (accuracy, num_attempts, num_correct, userID, resultID))
        self.c.execute('select * from Results')
        self.conn.commit()


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
                   "score for how legible your writing was!\n Your score will be compared with your friends to see "
                   "\nwhich of you has the neater writing!").pack()

        Label(self.__continue_screen, text="").pack()
        Label(self.__continue_screen, text="").pack()
        if self.login_success:
            Label(self.__continue_screen, text="You are logged in").pack()
        elif not self.login_success:
            Label(self.__continue_screen,
                  text="You are not logged in. By continuing your score will not be saved.").pack()

        Button(self.__continue_screen, text='Get started!', width=10, height=1, command=self.__selection).pack()

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
        Button(self.__leaderboard_screen, text='search username', width=15, height=2, command=self.find_username).pack()

    def find_username(self):
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

        Button(self.__selection_screen, text='begin', width=15, height=2, command=self.begin).pack()

    def begin(self):
        num_images = int(self.num_images_selected.get())

        client.server_predict(self.root, num_images, self.login_success)

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
                                    command=self.get_results)
        self.result_button.pack()

        self.__begin_screen.mainloop()

    def get_results(self):

        certainties = []
        correct = False
        self.result_button.destroy()  # destroy button so that user cannot press multiple times

        f = open('user_score.txt', 'r')

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


win = tkinter_windows()
win._start_screen()
