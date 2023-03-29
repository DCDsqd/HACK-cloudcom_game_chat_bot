import sqlite3
from sqlite3 import Error
import logging
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        logging.info("Connection to SQLite DB successful")
    except Error as e:
        logging.warning(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        logging.info("Query executed successfully")
    except Error as e:
        logging.warning(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def inserter(col_name, text, user_id):
    con = create_connection('../db/database.db')
    updater = f"""
            UPDATE users
            SET '{col_name}' = '{text}'
            WHERE id = '{user_id}';
            """
    execute_query(con, updater)
    con.close()


def get_avatar_ids(user_id):
    con = create_connection('../db/database.db')
    query = f"""
            SELECT hair_id, face_id, shoulders_id 
            FROM users 
            WHERE id = '{user_id}';
            """
    res = execute_read_query(con, query)
    con.close()
    return res[0][0], res[0][1], res[0][2]


def select_all_hair():
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT * FROM hair
            """
    res = execute_read_query(con, query)
    return res


def select_all_face():
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT * FROM face;
            """
    res = execute_read_query(con, query)
    return res


def select_all_shoulders():
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT * FROM shoulders;
            """
    res = execute_read_query(con, query)
    return res


def body_type_name_to_id(table, name):
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT id FROM {table} WHERE name='{name}';
            """
    res = execute_read_query(con, query)
    return res[0][0]


def check_if_user_exists(user_id) -> bool:
    con = create_connection('../db/database.db')
    query = f"""
            SELECT username FROM users WHERE id='{user_id}';
            """
    res = execute_read_query(con, query)
    if len(res) == 0:
        return False
    return True


# This function is used to ensure that given time in a form of string
# could be used in the bot system (db + code) since we use everywhere
# only one determined time string format which is: "yyyy-MM-dd hh:mm:ss"
def ensure_time_format(time_str: str) -> bool:
    if len(time_str) != len('yyyy-MM-dd hh:mm:ss'):
        return False

    if time_str[4] != '-' or time_str[7] != '-' or time_str[10] != ' ' or time_str[13] != ':' or time_str[16] != ':':
        return False

    year = time_str[0:3]
    if not year.isdigit():
        return False

    month = time_str[5:6]
    if not month.isdigit():
        return False

    day = time_str[8:9]
    if not day.isdigit():
        return False

    hour = time_str[11:12]
    if not hour.isdigit():
        return False

    minute = time_str[14:15]
    if not minute.isdigit():
        return False

    return True


def create_all_tables_from_sql_scripts():
    conn = sqlite3.connect('../db/database.db')
    with open('../sql/database_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()

    conn = sqlite3.connect('../db/gamedata.db')
    with open('../sql/gamedata_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()

def create_all_tables_from_sql_scripts_test():
    conn = sqlite3.connect('../db/test/database.db')
    with open('../sql/database_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()

    conn = sqlite3.connect('../db/test/gamedata.db')
    with open('../sql/gamedata_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()

def select_ranks_table():
    conn = sqlite3.connect('../db/gamedata.db')
    query = f"""
            SELECT name, exp_to_earn FROM ranks ORDER BY exp_to_earn;
            """
    res = execute_read_query(conn, query)
    conn.close()
    return res # [{name, exp_to_earn}...]

def get_user_exp(user_id):
    conn = sqlite3.connect('../db/database.db')
    query = f"""
            SELECT exp FROM users WHERE id='{user_id}';
            """
    res = execute_read_query(conn, query)
    conn.close()
    return res[0][0]

