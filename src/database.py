import sqlite3
from sqlite3 import Error
import logging
import time
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# This function creates a connection to a SQLite database at a given path and returns it. It also logs any errors
# that may occur during the connection process.
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        logging.info("Connection to SQLite DB successful")
    except Error as e:
        logging.warning(f"The error '{e}' occurred")

    return connection


# This function executes a SQL query on a database connection and logs if any error occurs during execution.
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        logging.info("Query executed successfully")
    except Error as e:
        logging.warning(f"The error '{e}' occurred")


# This is a function to execute a read query on a SQLite database using the given connection and SQL query. It
# returns the result obtained from executing the query.
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


# This function updates a specific column with a value for a given user in the SQLite database. It takes three
# parameters: col_name is the name of the column to update, text is the new value to set, and user_id is the ID of
# the user whose record to update. It uses the create_connection function to establish a connection to the database,
# executes an update query using execute_query, and closes the connection.
def inserter(col_name, text, user_id):
    con = create_connection('../db/database.db')
    updater = f"""
            UPDATE users
            SET '{col_name}' = '{text}'
            WHERE id = '{user_id}';
            """
    execute_query(con, updater)
    con.close()


# This function retrieves the hair_id, face_id, and shoulders_id of a user from the database given their user_id. It
# returns a tuple containing these three values.
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


# This function returns all the data from the given part of the gamedata database (hair, face, or shoulders). It
# creates a connection to the database, executes a SELECT query, fetches all the data, and then closes the
# connection. The result is returned.
def select_all(part):
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT * FROM {part};
            """
    res = execute_read_query(con, query)
    con.close()
    return res


# This function takes a table name and name of a body part and returns the corresponding id of that body part from
# the gamedata database.
def body_type_name_to_id(table, name):
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT id FROM {table} WHERE name='{name}';
            """
    res = execute_read_query(con, query)
    return res[0][0]


# This function takes a user ID as an argument and returns a boolean indicating whether the user exists in the
# database or not.
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

    second = time_str[17:19]
    if not second.isdigit():
        return False

    try:
        datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    except ValueError:
        return False

    return True


# This function creates all tables in the database.db and gamedata.db databases using the SQL scripts stored in the
# sql directory.
def create_all_tables_from_sql_scripts():
    conn = sqlite3.connect('../db/database.db')
    with open('../sql/database_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()

    conn = sqlite3.connect('../db/gamedata.db')
    with open('../sql/gamedata_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()


# TEST FUNCTION -> DELETE IN RELEASE
def create_all_tables_from_sql_scripts_test():
    conn = sqlite3.connect('../db/test/database.db')
    with open('../sql/database_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()

    conn = sqlite3.connect('../db/test/gamedata.db')
    with open('../sql/gamedata_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()


# This function selects all the rows from the ranks table in the gamedata.db database and returns a list of
# dictionaries, where each dictionary represents a rank with its corresponding name and the amount of experience
# points needed to reach it.
def select_ranks_table():
    conn = sqlite3.connect('../db/gamedata.db')
    query = f"""
            SELECT name, exp_to_earn FROM ranks ORDER BY exp_to_earn;
            """
    res = execute_read_query(conn, query)
    conn.close()
    return res  # [{name, exp_to_earn}...]


# This function takes a user ID as input, retrieves the user's experience (exp) from the database, and returns it as
# output.
def get_user_exp(user_id):
    conn = sqlite3.connect('../db/database.db')
    query = f"""
            SELECT exp FROM users WHERE id='{user_id}';
            """
    res = execute_read_query(conn, query)
    conn.close()
    return res[0][0]


# This function updates the list of participants in a global event by adding a new participant's ID to the existing
# list of participants. It takes two arguments - global_event_id (the ID of the global event) and new_participant_id
# (the ID of the new participant). The function connects to the database.db database, retrieves the current list of
# participants for the given global_event_id, appends the new_participant_id to the list (if it's not already
# present), and updates the participants field in the global_events table. The function does not return anything.
def update_participants_in_global_event(global_event_id, new_participant_id):
    conn = sqlite3.connect('../db/database.db')
    query = f"""
            SELECT participants FROM global_events WHERE id='{global_event_id}';
            """
    res = execute_read_query(conn, query)
    participants_text = res[0][0]
    if len(participants_text) == 0:
        participants_text = str(new_participant_id)
    else:
        participants_text += ',' + str(new_participant_id)
    query = f"""
            UPDATE global_events SET participants='{participants_text}' WHERE id='{global_event_id}';
            """  # probably should test this...
    execute_query(conn, query)
    conn.close()


# This function relies on fact that @text is valid, a.k.a parse_new_event_info_string(@text) == {True, 'Some message'}
def save_new_event_info_string_to_db(text):
    fields = text.split('\n')
    name = fields[0]
    descr = fields[1]
    start_time = fields[2]
    duration = fields[3]
    exp_reward = fields[4]
    conn = sqlite3.connect('../db/database.db')
    query = f"""
            INSERT INTO global_events (name,descr,start_time,duration,exp_reward) VALUES 
            ('{name}','{descr}','{start_time}','{duration}','{exp_reward}');
            """  # probably should test this as well...
    execute_query(conn, query)
    conn.close()
