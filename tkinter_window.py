from tkinter import *

def main_account_screen():
    global main_screen

    # add command=register in button widget

    main_screen = Tk()   # create window
    main_screen.geometry("300x200") # set window size
    main_screen.title("Account Login") # set window title

    # create a Form label
    Label(text="Choose Login Or Register", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
    Label(text="").pack()

    # create Login Button
    Button(text="Login", height="2", width="30").pack()
    Label(text="").pack()

    # create a register button
    Button(text="Register", height="2", width="30", command=register).pack()
    main_screen.mainloop() # start the GUI


def register():
    register_screen = Toplevel(main_screen)
    register_screen.title("Register")
    register_screen.geometry("300x250")

    # Set text variables
    username = StringVar()
    password = StringVar()

    # Set label for user's instruction
    Label(register_screen, text="Please enter details below", bg="blue").pack()
    Label(register_screen, text="").pack()

    # Set username label
    username_lable = Label(register_screen, text="Username * ")
    username_lable.pack()

    # Set username entry
    # The Entry widget is a standard Tkinter widget used to enter or display a single line of text.

    username_entry = Entry(register_screen, textvariable=username)
    username_entry.pack()

    # Set password label
    password_lable = Label(register_screen, text="Password * ")
    password_lable.pack()

    # Set password entry
    password_entry = Entry(register_screen, textvariable=password, show='*')
    password_entry.pack()

    Label(register_screen, text="").pack()

    # Set register button
    Button(register_screen, text="Register", width=10, height=1, bg="blue").pack()

main_account_screen() # call the main_account_screen() function
