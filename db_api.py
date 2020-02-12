import psycopg2


class DataBase(object):
    def __init__(self, database, user, password=""):
        self.connection = psycopg2.connect(database=database,
                                           user=user,
                                           password=password)

    def __exit__(self):
        self.connection.close()

    def getLastId(self):
        cur = self.connection.cursor()

        cur.execute('''SELECT MAX(id) FROM Users;''')
        rows = cur.fetchone()

        if rows[0] is None:
            return 0
        else:
            return rows[0]

    def initTables(self):
        cur = self.connection.cursor()

        cur.execute('''CREATE TABLE Users
        (id INT PRIMARY KEY,
        chat_id INT NOT NULL CONSTRAINT Users_unique_chat_id UNIQUE,
        username VARCHAR(40) NOT NULL CONSTRAINT Users_unique_username UNIQUE
        );
        ''')

        cur.execute('''CREATE TABLE Flags
        (id INT PRIMARY KEY NOT NULL REFERENCES Users ON DELETE CASCADE,
        presence BOOL NOT NULL DEFAULT false,
        set_count BOOL NOT NULL DEFAULT false,
        nickname BOOL NOT NULL DEFAULT true,
        shadow_ban BOOL NOT NULL DEFAULT false
        );
        ''')

        cur.execute('''CREATE TABLE Messages
        (id SERIAL PRIMARY KEY,
        user_id INT NOT NULL REFERENCES Users(chat_id),
        tg_name VARCHAR(40),
        tg_id VARCHAR(40),
        content TEXT NOT NULL,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        ''')

        self.connection.commit()

    def createUser(self, chat_id, username):
        cur = self.connection.cursor()

        new_index = self.getLastId() + 1

        cur.execute('''INSERT INTO Users (id, chat_id, username) VALUES (%s, %s, %s);''',
                    (new_index, chat_id, username))

        cur.execute('''INSERT INTO Flags(id) VALUES(%s);''', (new_index,))

        self.connection.commit()

    def writeMessage(self, user_id, tg_name, tg_id, content):
        cur = self.connection.cursor()

        cur.execute('''INSERT INTO Messages (user_id, tg_name, tg_id, content) VALUES (%s, %s, %s, %s);''',
                    (user_id, tg_name, tg_id, content,))

        self.connection.commit()


def main():
    db = DataBase("postgres", "ubuntu")
    db.initTables()


if __name__ == '__main__':
    main()
