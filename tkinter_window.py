from tkinter import *


def main_account_screen():
    global main_screen

    main_screen = Tk()  # create window
    main_screen.geometry("350x200")  # set window size
    main_screen.title("Account Login")  # set window title

    # create a Form label
    Label(text="Welcome to the handwriting test!", bg="teal", width="300", height="2").pack()
    Label(text="").pack()  # leaves a gap for aesthetic purposes

    # create Login Button
    Button(text="Login", height="2", width="30", command=login).pack()  # height and width defined for aesthetics
    Label(text="").pack()

    # create a register button
    Button(text="Register", height="2", width="30", command=register).pack()  # upon clicking, calls register function
    main_screen.mainloop()  # start the GUI


def login():
    global login_screen
    login_screen = Toplevel(main_screen)
    login_screen.title("Login")
    login_screen.geometry("300x250")
    Label(login_screen, text="Please enter details below to login").pack()
    Label(login_screen, text="").pack()

    global verify_username
    global verify_password

    username = StringVar()  # defines how the text entered will be stored
    password = StringVar()

    global username_login_entry
    global password_login_entry

    Label(login_screen, text="Username * ").pack()
    username_login_entry = Entry(login_screen, textvariable=username)  # makes the text entered into a variable
    username_login_entry.pack()

    Label(login_screen, text="").pack()
    Label(login_screen, text="Password * ").pack()

    password_login_entry = Entry(login_screen, textvariable=password, show='*')
    password_login_entry.pack()

    Label(login_screen, text="").pack()
    Button(login_screen, text="Login", width=10, height=1).pack()


def register():
    pass

main_account_screen()
