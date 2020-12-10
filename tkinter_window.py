# importing inbuilt python libraries
from tkinter import *
import sqlite3
import os
import hashlib


# import main

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
        self.c.execute("INSERT INTO HandwritingUsers(username,pw_hashed, salt, num_attempts) VALUES(?,?,?,?)",
                       ('example', pw, s, 1))  # done in this way to prevent sql injection
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
        their_salt = self.c.fetchone()[1]  # grabbed salt of the user from the database, it is stored with the name

        pw_hashed, salt = hash_password(entered_password, their_salt)  # used their salt to salt the password
        # they entered. If match, they are given access

        self.c.execute(" SELECT username, pw_hashed, salt FROM HandwritingUsers WHERE username = ? AND pw_hashed = ? ",
                       (username, pw_hashed))
        user_details = self.c.fetchall()

        if len(user_details) == 0:
            print('not in database')
            return False
        else:
            print('you"re in')
            return True

    def display_leaderboard(self):
        self.c.execute('SELECT username, accuracy, num_attempts FROM HandwritingUsers WHERE num_attempts != 0 ORDER BY accuracy ASC')
        self.conn.commit()

        return self.c.fetchall()


class logreg:

    def __init__(self):
        self.db = database()
        self.login_success = False

    def _start_screen(self):
        self.root = Tk()
        self.root.geometry("300x250")  # set window size
        self.root.title("Account Login")  # set window title

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

        Label(self.__main_screen, text="Please Select Your Choice", bg="white", width="20", height="2").pack()  # pack puts it into screen
        Label(self.__main_screen,text="").pack()  # leaves a gap for aesthetic purposes

        Button(self.__main_screen,text="Login", height="2", width="15", command=self.__login).pack()  # upon clicking, calls login function
        Label(self.__main_screen,text="").pack()

        Button(self.__main_screen,text="Register", height="2", width="15",
               command=self.__register).pack()  # upon clicking, calls register function
        Label(self.__main_screen,text="").pack()

        Button(self.__main_screen,text="Continue as Guest", height="2", width="15", command=self.__continue).pack()



    def __register(self):
        self.register_screen = Toplevel(self.__main_screen) # like a stack
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
        Button(self.register_screen, text="Register", width=10, height=1, bg="blue", command=self.__register_user).pack()

    def __register_user(self):
        self.db.insert(self.username.get(), self.password.get())
        print('You have been registered')

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

        def delete_login_failed_screen():
            self.login_failed_screen.destroy()

        def delete_login_success_screen():
            self.login_success_screen.destroy()

        def login_success():
            self.login_success_screen = Toplevel(self.login_screen)
            self.login_success_screen.title("Success")
            self.login_success_screen.geometry("150x100")

            Label(self.login_success_screen, text="Login Success").pack()
            Button(self.login_success_screen, text="OK", command=delete_login_success_screen).pack()

        def login_failed():
            self.login_failed_screen = Toplevel(self.login_screen)
            self.login_failed_screen.title("Error")
            self.login_failed_screen.geometry("150x100")

            Label(self.login_failed_screen, text="Invalid credentials supplied").pack()  # will not say which of user
            # and password are wrong, more secure
            Button(self.login_failed_screen, text="OK", command=delete_login_failed_screen).pack()
            self.login_success = False


        def login_verify():
            username = self.username_to_verify.get()
            password = self.password_to_verify.get()

            if self.db.user_password_match(username, password):
                login_success()
                self.login_success = True

            else:
                login_failed()
                self.login_success = False

        Label(self.login_screen, text="").pack()
        Button(self.login_screen, text="Confirm Login", width=10, height=1, command=login_verify).pack()

    def __continue(self):
        self.__continue_screen = Toplevel(self.__main_screen)  # like a stack
        self.__continue_screen.title("Welcome!")
        self.__continue_screen.geometry("500x350")

        Label(self.__continue_screen, text="Welcome to the handwriting game - digit edition! \n In this game you will be tested on how neatly you can write numbers.\n The computer will read your writing, \n and will give you an overall score for how legible your writing was!\n Your score will be compared with your friends to see \nwhich of you has the neater writing!").pack()
        Label(self.__continue_screen, text="").pack()
        Label(self.__continue_screen, text="").pack()
        Label(self.__continue_screen, text="").pack()

        Button(self.__continue_screen, text='Get started!', width=10, height=1, command=self.__main_screen.quit).pack()

    def __leaderboard(self):
        self.__leaderboard_screen = Toplevel(self.root)  # like a stack
        self.__leaderboard_screen.title("Leaderboard")
        self.__leaderboard_screen.geometry("300x250")

        leaders = self.db.display_leaderboard()
        print('hello')
        print(leaders)
        row1 = 'Username,accuracy, number of attempts'
        for row in leaders:
            print(row)
            Label(self.__leaderboard_screen, text=row1).pack()
            Label(self.__leaderboard_screen, text=row).pack()
        #Label(self.__leaderboard_screen, text='row').pack()


l = logreg()
l._start_screen()

# import main
# main.predict(l.login_success)
