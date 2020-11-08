from tkinter import *
#window
main_screen = Tk()  # create a window
main_screen.geometry("300x250") # set window size
main_screen.title("Login/register")  # set window title


# create a Form label
Label(text="Choose Login Or Register", bg="blue", width="300", height="2", font=("Calibri", 13)).pack()
Label(text="").pack()

# create Login Button
Button(text="Login", height="2", width="30").pack()
Label(text="").pack()

# create a register button
Button(text="Register", height="2", width="30").pack()

main_screen.mainloop()  # start the GUI

