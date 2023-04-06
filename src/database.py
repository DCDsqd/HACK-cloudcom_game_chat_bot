import sqlite3
from sqlite3 import Error
import logging
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def cur_time() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def cur_date() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d')


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
def create_connection(path) -> sqlite3.Connection:
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        logging.warning(f"The error '{e}' occurred")
    return connection


# This function executes a SQL query on a database connection and logs if any error occurs during execution.
def execute_query(connection: sqlite3.Connection, query: str) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        logging.info("Query executed successfully")
    except Error as e:
        logging.warning(f"The error '{e}' occurred")


# This is a function to execute a read query on a SQLite database using the given connection and SQL query. It
# returns the result obtained from executing the query.
def execute_read_query(connection: sqlite3.Connection, query: str) -> list:
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
def inserter(col_name: str, text: str, user_id: int) -> None:
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
def get_avatar_ids(user_id: int) -> tuple:
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
def select_all(part: str) -> list:
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT * FROM {part};
            """
    res = execute_read_query(con, query)
    con.close()
    return res


# This function takes a table name and name of a body part and returns the corresponding id of that body part from
# the gamedata database.
def body_type_name_to_id(table: str, name: str) -> int:
    con = create_connection('../db/gamedata.db')
    query = f"""
            SELECT id FROM {table} WHERE name='{name}';
            """
    res = execute_read_query(con, query)
    print(type(res[0][0]))
    return res[0][0]


# This function takes a user ID as an argument and returns a boolean indicating whether the user exists in the
# database or not.
def check_if_user_exists(user_id: int) -> bool:
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


# This function selects all the rows from the ranks table in the gamedata.db database and returns a list of
# dictionaries, where each dictionary represents a rank with its corresponding name and the amount of experience
# points needed to reach it.
def select_ranks_table() -> list:
    conn = sqlite3.connect('../db/gamedata.db')
    query = f"""
            SELECT name, exp_to_earn FROM ranks ORDER BY exp_to_earn;
            """
    res = execute_read_query(conn, query)
    conn.close()
    return res  # [{name, exp_to_earn}...]


# This function takes a user ID as input, retrieves the user's experience (exp) from the database, and returns it as
# output.
def get_user_exp(user_id: int) -> int:
    conn = sqlite3.connect('../db/database.db')
    query = f"""
            SELECT exp FROM users WHERE id='{user_id}';
            """
    res = execute_read_query(conn, query)
    conn.close()
    print(type(res[0][0]))
    return res[0][0]


# This function updates the list of participants in a global event by adding a new participant's ID to the existing
# list of participants. It takes two arguments - global_event_id (the ID of the global event) and new_participant_id
# (the ID of the new participant). The function connects to the database.db database, retrieves the current list of
# participants for the given global_event_id, appends the new_participant_id to the list (if it's not already
# present), and updates the participants field in the global_events table. The function does not return anything.
def update_participants_in_global_event(global_event_id: int, new_participant_id: int) -> None:
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
def save_new_event_info_string_to_db(text: str) -> None:
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


# This function selects all buildings from the "buildings" table in the gamedata database and returns a list of
# tuples containing the building id and name.
def select_all_buildings() -> list:
    conn = sqlite3.connect('../db/gamedata.db')
    query = f"""
            SELECT id, name FROM buildings; 
            """
    res = execute_read_query(conn, query)
    return res


# This function creates a new friend request by inserting a new row into the "friends" table of the database with the
# sender_id and receiver_id specified as input parameters. The request will be marked as not accepted (is_accepted = 0)
# by default.
def create_friend_request(id_sender: int, id_receiver: int) -> None:
    conn = sqlite3.connect('../db/database.db')

    query = f"""
                INSERT INTO friends (sender_id,receiver_id) VALUES 
                ('{id_sender}','{id_receiver}');
            """
    execute_query(conn, query)
    conn.close()


# Accepts a friend request by updating the 'is_accepted' field to 1 and setting the 'date_accepted' field to the
# current time
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


# Deletes a friendship connection between two users from the 'friends' table in the database. The function uses a
# single query to delete the friendship connection in both directions.
def delete_from_friends(id_initiator: int, id_target: int) -> None:
    with sqlite3.connect('../db/database.db') as conn:
        query = f"""
            DELETE FROM friends WHERE  
            (sender_id = '{id_initiator}' AND receiver_id = '{id_target}')
            OR (sender_id = '{id_target}' AND receiver_id = '{id_initiator}');
        """
        conn.execute(query)


# Get the list of friend IDs for the given user. Only returns the IDs of friends who have accepted the request.
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


# Retrieves a list of the IDs of users who sent friend requests to the given user,
# but the requests haven't been accepted yet.
def get_incoming_pending_friend_requests(user_id: int) -> list:
    with sqlite3.connect('../db/database.db') as conn:
        query = f"""
            SELECT sender_id FROM friends 
            WHERE receiver_id = '{user_id}' AND is_accepted = 0;
        """
        cursor = conn.execute(query)
        requests_list = [row[0] for row in cursor]
    return requests_list


# Returns a list of `receiver_id`s for all pending friend requests initiated by the user with `user_id`.
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
                user_id = '{user_id}';
            """
    res = execute_read_query(conn, query)
    if len(res) == 0:
        return True
    conn.close()
    return bool(res[0][0] != cur_date())


# @task_type should be one of:
# 1) 'small'
# 2) 'medium'
# 3) 'class_license'
# 4) 'any' (Do not take into consideration type of the task)
def get_random_task(task_type: str) -> list:
    conn = sqlite3.connect('../db/gamedata.db')
    query = f"""SELECT * FROM tasks"""
    if task_type != 'any':
        query += f""" WHERE type = '{task_type}'"""
    query += f""" ORDER BY RANDOM() LIMIT 1"""
    task = execute_read_query(conn, query)
    conn.close()
    return task[0]


def regenerate_daily_tasks(user_id: int) -> None:
    conn = sqlite3.connect('../db/database.db')

    # Delete outdated daily tasks (if they exist)
    query = f"""
                DELETE FROM user_daily_tasks WHERE  
                user_id = '{user_id}';
            """
    execute_query(conn, query)

    # Add new random tasks
    random_small_task = get_random_task('small')
    random_medium_task = get_random_task('medium')
    random_class_license_task = get_random_task('class_license')
    query = f"""
                INSERT INTO user_daily_tasks (user_id,task_id) VALUES
                ('{user_id}','{random_small_task[0]}'),
                ('{user_id}','{random_medium_task[0]}'),
                ('{user_id}','{random_class_license_task[0]}');
            """
    execute_query(conn, query)

    # Update user_daily_tasks_updated table
    query = f"""
                INSERT OR REPLACE INTO user_daily_tasks_updated (user_id, last_update)
                VALUES ('{user_id}', '{cur_date()}');
            """
    execute_query(conn, query)

    conn.close()


def get_cur_user_tasks(user_id: int) -> dict:
    conn = sqlite3.connect('../db/database.db')

    attach_query = """ATTACH '../db/gamedata.db' AS gamedata;"""
    execute_query(conn, attach_query)

    query = f"""
                SELECT user_daily_tasks.task_id, gamedata.tasks.type, user_daily_tasks.is_completed
                FROM user_daily_tasks
                JOIN gamedata.tasks ON gamedata.tasks.id = user_daily_tasks.task_id
                WHERE user_daily_tasks.user_id = '{user_id}';
            """
    res = execute_read_query(conn, query)
    conn.close()

    # Expect to return only 3 tasks
    if len(res) != 3:
        logging.warning('Query result length is not equal to expected in function get_cur_user_tasks')

    tasks_list = {}

    for i in range(len(res)):
        # Mark completed tasks as "-1"
        if res[i][2] == 0:
            tasks_list[str(res[i][1])] = res[i][0]
        else:
            tasks_list[str(res[i][1])] = -1

    return tasks_list


def get_task_by_id(task_id: int) -> list:
    con = create_connection('../db/gamedata.db')
    query = f"""
                SELECT * FROM tasks WHERE id = '{task_id}';
            """
    res = execute_read_query(con, query)
    con.close()
    return res[0]