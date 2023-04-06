import sqlite3
from sqlite3 import Error
import logging
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def cur_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_tasks(is_multiplayer: int) -> list:
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT * FROM tasks WHERE is_multiplayer='{is_multiplayer}';
            """
    res = execute_read_query(con, query)
    con.close()
    return res


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
    try:
        datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False


# This function creates all tables in the database.db and gamedata.db databases using the SQL scripts stored in the
# sql directory.
def create_all_tables_from_sql_scripts() -> None:
    conn = sqlite3.connect('../db/database.db')
    with open('../sql/database_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()

    conn = sqlite3.connect('../db/gamedata.db')
    with open('../sql/gamedata_create_tables.sql', 'r') as sql_file:
        conn.executescript(sql_file.read())
    conn.close()


# TEST FUNCTION -> DELETE IN RELEASE
def create_all_tables_from_sql_scripts_test() -> None:
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
def update_participants_in_global_event(global_event_id, new_participant_id) -> None:
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
            """
    execute_query(conn, query)
    conn.close()


# This function relies on fact that @text is valid, a.k.a parse_new_event_info_string(@text) == {True, 'Some message'}
def save_new_event_info_string_to_db(text) -> None:
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
            """
    execute_query(conn, query)
    conn.close()


def select_all_buildings():
    conn = sqlite3.connect('../db/gamedata.db')
    query = f"""
            SELECT id, name FROM buildings; 
            """
    res = execute_read_query(conn, query)
    return res


def create_friend_request(id_sender: int, id_receiver: int) -> None:
    conn = sqlite3.connect('../db/database.db')

    query = f"""
                INSERT INTO friends (sender_id,receiver_id) VALUES 
                ('{id_sender}','{id_receiver}');
            """
    execute_query(conn, query)
    conn.close()


def accept_friend_request(id_sender: int, id_receiver: int) -> None:
    conn = sqlite3.connect('../db/database.db')
    query = f"""
                UPDATE friends SET
                is_accepted = 1,
                date_accepted = '{cur_time()}' WHERE  
                sender_id = '{id_receiver}' AND
                receiver_id = '{id_sender}';
            """
    execute_query(conn, query)
    conn.close()


def delete_from_friends(id_initiator: int, id_target: int) -> None:
    with sqlite3.connect('../db/database.db') as conn:
        query = f"""
            DELETE FROM friends WHERE  
            (sender_id = '{id_initiator}' AND receiver_id = '{id_target}')
            OR (sender_id = '{id_target}' AND receiver_id = '{id_initiator}');
        """
        conn.execute(query)


def get_friend_list_ids(user_id: int) -> list:
    friend_list = []
    with sqlite3.connect('../db/database.db') as conn:
        query = f"""
            SELECT CASE WHEN sender_id = '{user_id}' THEN receiver_id ELSE sender_id END
            FROM friends
            WHERE (sender_id = '{user_id}' OR receiver_id = '{user_id}')
            AND is_accepted = 1
        """
        cursor = conn.execute(query)
        for row in cursor:
            friend_list.append(row[0])
    return friend_list


def get_incoming_pending_friend_requests(user_id: int) -> list:
    with sqlite3.connect('../db/database.db') as conn:
        query = f"""
            SELECT sender_id FROM friends 
            WHERE receiver_id = '{user_id}' AND is_accepted = 0;
        """
        cursor = conn.execute(query)
        requests_list = [row[0] for row in cursor]
    return requests_list


def get_outgoing_pending_friend_requests(user_id: int) -> list:
    with sqlite3.connect('../db/database.db') as conn:
        query = f"""
            SELECT receiver_id FROM friends 
            WHERE sender_id = '{user_id}' AND is_accepted = 0;
        """
        cursor = conn.execute(query)
        requests_list = [row[0] for row in cursor]
    return requests_list


# Checks whether two ids are currently friends, returns:
# -1 if they are not friends
# 0 if @first_user_id is a sender
# 1 if @first_user_id is a receiver (reversed order)
# 2 if @first_user_id is a sender, but request is still pending
# 3 if @first_user_id is a receiver (reversed_order), but request is still pending
def check_if_friends(first_user_id: int, second_user_id: int) -> int:
    conn = sqlite3.connect('../db/database.db')
    query = f"""
                SELECT is_accepted FROM friends WHERE  
                sender_id = '{first_user_id}' AND
                receiver_id = '{second_user_id}';
            """
    res = execute_read_query(conn, query)
    if len(res) != 0:
        return 0 if res[0][0] == 1 else 2

    query = f"""
                SELECT is_accepted FROM friends WHERE  
                sender_id = '{second_user_id}' AND
                receiver_id = '{first_user_id}';
            """
    res = execute_read_query(conn, query)
    if len(res) != 0:
        return 1 if res[0][0] == 1 else 3

    conn.close()
    return -1


def check_if_need_to_update_daily_tasks(user_id: int) -> bool:
    conn = sqlite3.connect('../db/database.db')
    query = f"""
                SELECT last_update FROM user_daily_tasks_updated WHERE  
                user_id = '{user_id}');
            """
    res = execute_read_query(conn, query)
    if len(res) == 0:
        return False
    conn.close()
    return bool(res[0][0])


# @task_type should be one of:
# 1) 'small'
# 2) 'medium'
# 3) 'class_license'
# 4) 'any' (Do not take into consideration type of the task)
def get_random_task(task_type: str) -> list:
    conn = sqlite3.connect('../db/gamedata.db')
    query = f"""
                SELECT * FROM tasks"""
    if task_type != 'any':
        query += f""" WHERE type = '{task_type}'"""
    query += f""" ORDER BY RANDOM() LIMIT 1"""
    task = execute_read_query(conn, query)
    conn.close()
    return task


def regenerate_daily_tasks(user_id: int) -> None:
    conn = sqlite3.connect('../db/database.db')

    # Delete outdated daily tasks (if they exist)
    query = f"""
                DELETE FROM user_daily_tasks WHERE  
                user_id = '{user_id}');
            """
    execute_query(conn, query)

    # Add new random tasks
    random_small_task = get_random_task('small')
    random_medium_task = get_random_task('medium')
    random_class_license_task = get_random_task('class_license')
    query = f"""
                INSERT INTO user_daily_tasks (user_id,event_id) VALUES
                ('{user_id}','{random_small_task[0]}'),
                ('{user_id}','{random_medium_task[0]}'),
                ('{user_id}','{random_class_license_task[0]}');
            """
    execute_query(conn, query)

    # Update user_daily_tasks_updated table
    query = f"""
                INSERT OR IGNORE INTO user_daily_tasks_updated (user_id, last_updated)
                VALUES ('{cur_time()}')
                UPDATE user_daily_tasks_updated SET date = '{cur_time()}'
                WHERE user_id = '{user_id}');
            """
    execute_query(conn, query)

    conn.close()
