import sqlite3
import hashlib
import os


def hash_password(password, salt=None):
    """
    If user has already got a salt, then that will be passed in as salt parameter. If not, salt is defined as None, and
    so a new salt is generated for them.
    hashes password using hashlib
    :param password:
    :param salt:
    :return: hashed password, salt
    """
    if salt is None:
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
        """
        check if user is in database
        :param username:
        :return True:
        """
        self.c.execute("select * From Users where username = ?", (username,))
        fetched = self.c.fetchone()
        if fetched is None:
            return False
        return True

    def insert(self, username, password):
        """
        inserts the username into the database, and also hashes the password, then stores the salt,password,username.
        :param username: StringVar
        :param password: string
        """
        username = str(username)
        password = str(password)
        pw_hashed, salt = hash_password(password)  # no salt provided, default provided as none
        self.c.execute("INSERT INTO Users(username,pw_hashed,salt) VALUES(?,?,?)",
                       (username, pw_hashed, salt))  # used parameterised sql to prevent sql injection
        self.conn.commit()

    def user_password_match(self, username, entered_password):
        """
        Check if username and password match
        :param username:
        :param entered_password:
        :return:
        """
        self.c.execute(" SELECT username, salt FROM Users WHERE username = ?", (username,))
        fetched = self.c.fetchone()
        if fetched is None:
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
                return False
            else:
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
        """

        :param user:
        :return: list of Rounds that user has done, list
        """
        username = str(user)
        try:
            self.c.execute('select UserID from Users Where username = ?', (username,))
            their_UserID = self.c.fetchone()[0]

            self.c.execute('''
            SELECT Rounds.RoundID, Rounds.Correct, Rounds.Number_to_draw, Rounds.Number_drawn, Rounds.certainty
            FROM Rounds
            WHERE Rounds.UserID = ? ''', (their_UserID,))
        except TypeError:
            return ['nothing entered']

        return self.c.fetchall()

    def insert_round(self, user, attempt_num, correct, num_to_draw, num_drawn, certainty):
        """
        :param user: StringVar, username. stringvar since it is a tkinter entry. converted to string below
        :param attempt_num: int
        :param correct: Bool
        :param num_to_draw: int
        :param num_drawn: int
        :param certainty: int
        :return: nothing
        Adds row to round table, using text file
        """
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
            'insert into Rounds(RoundID,UserID,ResultID, Correct,Number_to_draw, Number_drawn, Certainty) VALUES(?,?,'
            '?,?,?,?,?)',
            (attempt_num, userID, resultID, correct, num_to_draw, num_drawn, certainty))
        self.conn.commit()
        # self.c.execute('select * from Rounds ')

    def insert_results(self, username, accuracy=None, num_attempts=None, num_correct=None):
        """

        :param username:
        :param accuracy: how certain the network was.
        :param num_attempts:
        :param num_correct:
        :return:
        """

        # when first
        # creating result row, these values are none until the game ends, and they can be determined
        user = str(username)
        self.c.execute('select UserID from Users where username = ?', (user,))
        userID = self.c.fetchone()[0]
        self.c.execute(
            'insert into Results(UserID, Overall_accuracy,num_attempts, num_correct) VALUES(?,?,?,?)',
            (userID, accuracy, num_attempts, num_correct))
        self.c.execute('select * from Results')
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

