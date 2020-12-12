# importing inbuilt python libraries
from tkinter import *
import sqlite3
import os
import hashlib
import main


def hash_password(password, salt=None):
    if salt == None:
        salt = os.urandom(16)  # randomly generates a 16 bit binary string if the user is registering, otherwise uses
        # their salt that was assigned.
    password = str(password)
    hashed = hashlib.pbkdf2_hmac('sha256',  # The hash digest algorithm for hmac
                                 password.encode('utf-8'),  # Convert the password into bytes
                                 salt, 1000  # number of iterations of hash- more iterations makes it more secure
                                 )

    return hashed, salt


class database():

    def __init__(self):
        self.conn = sqlite3.connect(':memory:')  # establishing a connection with the memory, so that I can debug,
        # with a new database each time
        self.c = self.conn.cursor()

        # this is used to solve the problem of the c.fetchall() function returning a unicode string rather than utf-8
        # before, it would return " u'username' " now with this line it returns " 'username' "
        self.conn.text_factory = str

        self.c.execute('''CREATE TABLE HandwritingUsers(
          userID integer NOT NULL PRIMARY KEY,
          username text NOT NULL,
          pw_hashed text NOT NULL,
          salt  text    NOT NULL,
          accuracy integer,
          num_attempts integer
          )''')

        self.conn.commit()
        pw, s = hash_password('1')
        self.c.execute(
            "INSERT INTO HandwritingUsers(username,pw_hashed, salt, num_attempts,accuracy) VALUES(?,?,?,?,?)",
            ('example', pw, s, '1', '2'))  # done in this way to prevent sql injection
        self.c.execute("INSERT INTO HandwritingUsers(username,pw_hashed, salt) VALUES(?,?,?)",
                       ('jane', pw, s))
        self.conn.commit()

    def insert(self, username, password):
        username = str(username)
        pw_hashed, salt = hash_password(password)  # no salt provided, default provided as none
        self.c.execute("INSERT INTO HandwritingUsers(username,pw_hashed,salt) VALUES(?,?,?)",
                       (username, pw_hashed, salt))
        self.conn.commit()
        print('Your information has been added!')

    def user_password_match(self, username, entered_password):
        self.c.execute(" SELECT username, salt FROM HandwritingUsers WHERE username = ?", (username,))
        fetched = self.c.fetchone()
        if fetched == None:
            print('user not registered')
            return False
        else:
            their_salt = fetched[1]  # grabbed salt of the user from the database
            pw_hashed, salt = hash_password(entered_password, their_salt)  # used their salt to hash the password
            # they entered. If match, they are given access

            self.c.execute(
                " SELECT username, pw_hashed, salt FROM HandwritingUsers WHERE username = ? AND pw_hashed = ? ",
                (username, pw_hashed))
            user_details = self.c.fetchall()

            if len(user_details) == 0:
                print('not in database')
                return False
            else:
                print('you"re in')
                return True

    def display_leaderboard(self):
        self.c.execute(
            'SELECT username, accuracy, num_attempts FROM HandwritingUsers WHERE num_attempts != 0 ORDER BY accuracy ASC')
        self.conn.commit()  # dont want to display people who havent attempted the game yet

        return self.c.fetchmany(5)  # returns top 5

    def get_user_score(self, user):
        self.c.execute(" SELECT username, accuracy, num_attempts  FROM HandwritingUsers WHERE username = ?", (user,))
        return self.c.fetchall()

    def update_column(self, col, value, user):

        self.c.execute('UPDATE HandwritingUsers SET ? = ? WHERE UserID = ?', (col, value, user))


class logreg:

    def __init__(self):
        self.db = database()
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

        Button(self.__main_screen, text="Continue as Guest", height="2", width="15", command=self.__continue).pack()

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
            Button(register_success_screen, text="OK", command=register_success_screen.destroy).pack()

        password = self.password.get()
        username = self.username.get()
        if 20 > len(username) > 2:
            if username.isalnum():
                if username[0].isalpha():
                    if len(password) > 8:
                        if ' ' not in password and ' ' not in username:
                            register_success()
                            self.db.insert(username, password)
                        else:
                            register_failed('Must not have spaces. Use underscores instead(_)')
                    else:
                        register_failed('password must be longer than 8 char')
                else:
                    register_failed('First character must be a letter')
            else:
                register_failed('Username must be alphanumeric')
        else:
            register_failed('that username length is invalid')

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
            username = self.username_to_verify.get()
            password = self.password_to_verify.get()

            if self.db.user_password_match(username, password):
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
              text="Welcome to the handwriting game - digit edition! \n In this game you will be tested on how neatly you can write numbers.\n The computer will read your writing, \n and will give you an overall score for how legible your writing was!\n Your score will be compared with your friends to see \nwhich of you has the neater writing!").pack()
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
        self.__leaderboard_screen.geometry("300x250")

        self.username_to_search = StringVar()

        leaders = self.db.display_leaderboard()
        print('hello')
        print(leaders)
        row1 = 'Username,accuracy, number of attempts'
        Label(self.__leaderboard_screen, text=row1).pack()
        for row in leaders:
            Label(self.__leaderboard_screen, text=f'{row[0]} | {row[1]} | {row[2]}').pack()
        # Label(self.__leaderboard_screen, text='row').pack()
        self.search_username = Entry(self.__leaderboard_screen, textvariable=self.username_to_search).pack()
        Button(self.__leaderboard_screen, text='search username', width=15, height=2, command=self.find_username).pack()

    def find_username(self):
        user = self.username_to_search.get()  # gets entered text
        scores = self.db.get_user_score(user)  # returns sql statemtn that grabs all scores by that username
        row1 = 'Username, accuracy, number of attempts'
        Label(self.__leaderboard_screen, text=row1).pack()
        for row in scores:
            Label(self.__leaderboard_screen, text=f'{row[0]} | {row[1]} | {row[2]}').pack()

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

        main.predict(self.root, num_images, self.login_success)

        self.__begin_screen = Tk()  # don't want this to be a top level of anything, since i want to keep this open
        self.__begin_screen.title("Results")
        self.__begin_screen.geometry("300x250")

        def get_results():
            f = open('user_score.txt', 'r')
            num_correct = 0
            for row in f:
                lrow = row[:-1]  # remove \n
                print(lrow)
                attempt_num = lrow[0]  # first digit
                prompt = lrow[2]  # next digit, after whitespace
                guess = lrow[4]  # next digit, after whitespace
                certainty = int(lrow[6:])  # rest of the string, after whitespace
                Label(self.__begin_screen,
                      text=f"Image number{attempt_num}\n You should have drawn a {prompt}.\n I think that's a {guess} I'm {certainty}% certain").pack()
                if guess == prompt and certainty > 60:
                    num_correct += 1
                else:
                    Label(self.__begin_screen, text=" You've not drawn that well enough for me to recognise it.").pack()



        Button(self.__begin_screen, text='Get results', width=15, height=2, command=get_results).pack()


l = logreg()
l._start_screen()

