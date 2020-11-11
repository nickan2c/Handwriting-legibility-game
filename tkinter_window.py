from tkinter import *


class logreg:

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
        pass

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

        Label(self.login_screen, text="").pack()
        Button(self.login_screen, text="Login", width=10, height=1, command=self.login_verify).pack()

    def login_verify(self):
        pass


l = logreg()
l.main_screen()