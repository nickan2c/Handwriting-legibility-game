# importing inbuilt python libraries
from tkinter import *
import sqlite3
import os
import hashlib


# You don't reverse it, you never reverse a password. That's why we hash it and we don't encrypt it.
# If you need to compare an input password with a stored password, you hash the input and compare the hashes.
# If you encrypt a password anyone with the key can decrypt it and see it. It's not safe

def hash_password(password):
    salt = os.urandom(32)  # randomly generates a 32 bit binary string

    key = hashlib.pbkdf2_hmac('sha256',  # The hash digest algorithm for hmac
                              password.encode('utf-8'),  # Convert the password into bytes
                              salt, 1000  # number of iterations of hash- more iterations makes it more secure
                              )

    return salt + key


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
          accuracy integer
          num_attempts integer
          )''')

        self.conn.commit()

        self.c.execute("INSERT INTO HandwritingUsers(username,pw_hashed) VALUES(?,?)",
                       ('example', '1'))  # done in this way to prevent sql injection
        self.conn.commit()

    def insert(self, username, password):
        pw_hashed = hash_password(password)
        self.c.execute("INSERT INTO HandwritingUsers(username,pw_hashed) VALUES(?,?)", (username, pw_hashed))
        self.conn.commit()
        print('Your information has been added!')

    def user_password_match(self, username, entered_password):
        check_pw_hashed = hash_password(entered_password)

        self.c.execute(" SELECT username, pw_hashed FROM HandwritingUsers WHERE username = ? AND pw_hashed = ? ",
                       (username, check_pw_hashed))
        user_details = self.c.fetchall()

        if len(user_details) == 0:
            print('not in database')
            return False
        else:
            return True


class logreg:

    def __init__(self):
        self.db = database()

    def main_screen(self):
        self.main_screen = Tk()  # create window
        self.main_screen.geometry("300x250")  # set window size
        self.main_screen.title("Account Login")  # set window title

        Label(text="Please Select Your Choice", bg="white", width="20", height="2").pack()  # pack puts it into screen
        Label(text="").pack()  # leaves a gap for aesthetic purposes

        Button(text="Login", height="2", width="15", command=self.login).pack()  # upon clicking, calls login function
        Label(text="").pack()

        Button(text="Register", height="2", width="15",
               command=self.register).pack()  # upon clicking, calls register function

        self.main_screen.mainloop()

    def register(self):
        self.register_screen = Toplevel(self.main_screen)
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
        Button(self.register_screen, text="Register", width=10, height=1, bg="blue", command=self.register_user).pack()

    def register_user(self):
        pass

    def login(self):
        self.login_screen = Toplevel(self.main_screen)
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

        def login_verify():
            username = self.username_to_verify.get()
            password = self.password_to_verify.get()

            if self.db.user_password_match(username, password):
                login_success()
            else:
                login_failed()

        Label(self.login_screen, text="").pack()
        Button(self.login_screen, text="Confirm Login", width=10, height=1, command=login_verify).pack()

    # db = database()


l = logreg()
l.main_screen()
