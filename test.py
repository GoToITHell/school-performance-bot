import sqlite3
try:
    with open("users_data.db", "r", encoding="utf-8") as data_base:

except FileNotFoundError:
    user_data = {}
#data_base = sqlite3.connect('users_data.db')
curcor = data_base.cursor()

curcor.execute('''CREATE TABLE IF NOT EXISTS user_data (id TEXT PRIMARY KEY NOT NULL,
 class INTEGER NOT NULL, letter TEXT  NOT NULL, name TEXT NOT NULL,
username TEXT NOT NULL)''')
curcor.execute("INSERT INTO user_data VALUES ('14323434', 11, 'b', 'Jhon', 'jhon123456')")
curcor.execute("INSERT INTO user_data VALUES ('11256434', 1, 'a', 'Aria', 'Stark228')")
a = '11256434'
curcor.execute(f'''SELECT * FROM user_data WHERE "id" ={a} ''')
data = curcor.fetchall() # в data хранится воообще всё что только можно
print(data) # чуть подумал и уже не так уж и плохо выглядит
'''for i in data:
    if '11256434' in i:
        print(i)
        i1 = list(i)  # преобразование кортежа в массив
        print(i1[1])   # бинго!, сырой макет готов'''

data_base.commit()
data_base.close()
id_user={
    "123456": {
        "class": 11,
        "letter": "а",
        "name": "Jhon",
        "username": "jhon-123456"
    }
}