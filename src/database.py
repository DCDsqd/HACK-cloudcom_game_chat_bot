import sqlite3
from collections import defaultdict
from sqlite3 import Error
import logging
from time_control import cur_time, cur_date, cur_time_for_logger
import sys
import random

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='../logs/launch_%s.log' % cur_time_for_logger(),
    encoding='utf-8',
    level=logging.INFO
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


# Basic common functions outside of Database class:

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


class Database:

    def __init__(self):
        self.gamedata_conn = create_connection('../db/gamedata.db')
        self.database_conn = create_connection('../db/database.db')

    def __del__(self):
        self.gamedata_conn.close()
        self.database_conn.close()

    # This function updates a specific column with a value for a given user in the SQLite database. It takes three
    # parameters: col_name is the name of the column to update, text is the new value to set, and user_id is the ID of
    # the user whose record to update. It uses the create_connection function to establish a connection to the database,
    # executes an update query using execute_query, and closes the connection.
    def update_users(self, col_name: str, text, user_id: int) -> None:
        updater = f"""
                UPDATE users
                SET '{col_name}' = '{text}'
                WHERE id = '{user_id}';
                """
        execute_query(self.database_conn, updater)

    def get_tasks(self, is_multiplayer: int) -> list:
        query = f"""
                SELECT * FROM tasks WHERE is_multiplayer='{is_multiplayer}';
                """
        res = execute_read_query(self.gamedata_conn, query)
        return res

    # This function retrieves the hair_id, face_id, and shoulders_id of a user from the database given their user_id. It
    # returns a tuple containing these three values.
    def get_avatar_ids(self, user_id: int) -> tuple:
        query = f"""
                SELECT hair_id, face_id, shoulders_id 
                FROM users 
                WHERE id = '{user_id}';
                """
        res = execute_read_query(self.database_conn, query)
        return res[0][0], res[0][1], res[0][2]

    # This function returns all the data from the given part of the gamedata database (hair, face, or shoulders). It
    # creates a connection to the database, executes a SELECT query, fetches all the data, and then closes the
    # connection. The result is returned.
    def select_all_body_parts_by_type(self, part: str) -> list:  # TODO: Rename to something more informative!!!
        query = f"""
                SELECT * FROM {part};
                """
        res = execute_read_query(self.gamedata_conn, query)
        return res

    # This function takes a table name and name of a body part and returns the corresponding id of that body part from
    # the gamedata database.
    def body_type_name_to_id(self, table: str, name: str) -> int:
        query = f"""
                SELECT id FROM {table} WHERE name='{name}';
                """
        res = execute_read_query(self.gamedata_conn, query)
        return res[0][0]

    # This function takes a user ID as an argument and returns a boolean indicating whether the user exists in the
    # database or not.
    def check_if_user_exists(self, user_id: int) -> bool:
        query = f"""
                    SELECT username FROM users WHERE id='{user_id}';
                """
        res = execute_read_query(self.database_conn, query)
        if len(res) == 0:
            return False
        return True

    def check_if_user_exists_by_nick(self, user_nick: str) -> bool:
        query = f"""
                    SELECT id FROM users WHERE personal_username='{user_nick}';
                """
        res = execute_read_query(self.database_conn, query)
        if len(res) == 0:
            return False
        return True

    # This function creates all tables in the database.db and gamedata.db databases using the SQL scripts stored in the
    # sql directory.
    def create_all_tables_from_sql_scripts(self) -> None:
        with open('../sql/database_create_tables.sql', 'r') as sql_file:
            self.database_conn.executescript(sql_file.read())

        with open('../sql/gamedata_create_tables.sql', 'r') as sql_file:
            self.gamedata_conn.executescript(sql_file.read())

    # This function selects all the rows from the ranks table in the gamedata.db database and returns a list of
    # dictionaries, where each dictionary represents a rank with its corresponding name and the amount of experience
    # points needed to reach it.
    def select_ranks_table(self) -> list:
        query = f"""
                SELECT name, exp_to_earn FROM ranks ORDER BY exp_to_earn;
                """
        res = execute_read_query(self.gamedata_conn, query)
        return res  # [{name, exp_to_earn}...]

    # This function takes a user ID as input, retrieves the user's experience (exp) from the database, and returns it as
    # output.
    def get_user_exp(self, user_id: int) -> int:
        query = f"""
                SELECT exp FROM users WHERE id='{user_id}';
                """
        res = execute_read_query(self.database_conn, query)
        return res[0][0]

    # This function updates the list of participants in a global event by adding a new participant's ID to the existing
    # list of participants. It takes two arguments - global_event_id (the ID of the global event) and new_participant_id
    # (the ID of the new participant). The function connects to the database.db database, retrieves the current list of
    # participants for the given global_event_id, appends the new_participant_id to the list (if it's not already
    # present), and updates the participants field in the global_events table. The function does not return anything.
    def update_participants_in_global_event(self, global_event_id: int, new_participant_id: int) -> None:
        query = f"""
                        INSERT INTO global_events_participants (id, user_id)
                        SELECT '{global_event_id}', '{new_participant_id}'
                        WHERE NOT EXISTS (
                            SELECT 1 FROM global_events_participants
                            WHERE id = '{global_event_id}' AND user_id = '{new_participant_id}'
                        )
                    """
        execute_query(self.database_conn, query)

    def get_user_events(self, user_id: int) -> list:
        query = f"""
                    SELECT e.* FROM global_events e
                    JOIN global_events_participants p ON e.id = p.id
                    WHERE p.user_id = '{user_id}'
                    ORDER BY e.start_time DESC LIMIT 20
                    """
        return execute_read_query(self.database_conn, query)

    # This function relies on fact that @text is valid, so that:
    # parse_new_event_info_string(@text) == {True, 'Some message'}
    def save_new_event_info_string_to_db(self, text: str) -> None:
        fields = text.split('\n')
        name = fields[0]
        descr = fields[1]
        start_time = fields[2]
        duration = fields[3]
        exp_reward = fields[4]
        query = f"""
                INSERT INTO global_events (name,descr,start_time,duration,exp_reward) VALUES 
                ('{name}','{descr}','{start_time}','{duration}','{exp_reward}');
                """
        execute_query(self.database_conn, query)

    # This function selects all buildings from the "buildings" table in the gamedata database and returns a list of
    # tuples containing the building id and name.
    def select_all_buildings(self) -> list:
        query = f"""
                SELECT id, name FROM buildings; 
                """
        res = execute_read_query(self.gamedata_conn, query)
        return res

    # This function creates a new friend request by inserting a new row into the "friends" table of the database with the
    # sender_id and receiver_id specified as input parameters. The request will be marked as not accepted (is_accepted = 0)
    # by default.
    def create_friend_request(self, id_sender: int, id_receiver: int) -> None:
        query = f"""
                    INSERT INTO friends (sender_id,receiver_id) VALUES 
                    ('{id_sender}','{id_receiver}');
                """
        execute_query(self.database_conn, query)

    # Accepts a friend request by updating the 'is_accepted' field to 1 and setting the 'date_accepted' field to the
    # current time
    def accept_friend_request(self, id_sender: int, id_receiver: int) -> None:
        query = f"""
                    UPDATE friends SET
                    is_accepted = 1,
                    date_accepted = '{cur_time()}' WHERE  
                    sender_id = '{id_receiver}' AND
                    receiver_id = '{id_sender}';
                """
        execute_query(self.database_conn, query)

    # Deletes a friendship connection between two users from the 'friends' table in the database. The function uses a
    # single query to delete the friendship connection in both directions.
    def delete_from_friends(self, id_initiator: int, id_target: int) -> None:
        query = f"""
            DELETE FROM friends WHERE  
            (sender_id = '{id_initiator}' AND receiver_id = '{id_target}')
            OR (sender_id = '{id_target}' AND receiver_id = '{id_initiator}');
        """
        self.database_conn.execute(query)

    # Get the list of friend IDs for the given user. Only returns the IDs of friends who have accepted the request.
    def get_friend_list_ids(self, user_id: int) -> list:
        friend_list = []
        query = f"""
            SELECT CASE WHEN sender_id = '{user_id}' THEN receiver_id ELSE sender_id END
            FROM friends
            WHERE (sender_id = '{user_id}' OR receiver_id = '{user_id}')
            AND is_accepted = 1
        """
        cursor = self.database_conn.execute(query)
        for row in cursor:
            friend_list.append(row[0])
        return friend_list

    # Retrieves a list of the IDs of users who sent friend requests to the given user,
    # but the requests haven't been accepted yet.
    def get_incoming_pending_friend_requests(self, user_id: int) -> list:
        query = f"""
            SELECT sender_id FROM friends 
            WHERE receiver_id = '{user_id}' AND is_accepted = 0;
        """
        cursor = self.database_conn.execute(query)
        requests_list = [row[0] for row in cursor]
        return requests_list

    # Returns a list of `receiver_id`s for all pending friend requests initiated by the user with `user_id`.
    def get_outgoing_pending_friend_requests(self, user_id: int) -> list:
        query = f"""
            SELECT receiver_id FROM friends 
            WHERE sender_id = '{user_id}' AND is_accepted = 0;
        """
        cursor = self.database_conn.execute(query)
        requests_list = [row[0] for row in cursor]
        return requests_list

    # Checks whether two ids are currently friends, returns:
    # -1 if they are not friends
    # 0 if @first_user_id is a sender
    # 1 if @first_user_id is a receiver (reversed order)
    # 2 if @first_user_id is a sender, but request is still pending
    # 3 if @first_user_id is a receiver (reversed_order), but request is still pending
    def check_if_friends(self, first_user_id: int, second_user_id: int) -> int:
        query = f"""
                    SELECT is_accepted FROM friends WHERE  
                    sender_id = '{first_user_id}' AND
                    receiver_id = '{second_user_id}';
                """
        res = execute_read_query(self.database_conn, query)
        if len(res) != 0:
            return 0 if res[0][0] == 1 else 2

        query = f"""
                    SELECT is_accepted FROM friends WHERE  
                    sender_id = '{second_user_id}' AND
                    receiver_id = '{first_user_id}';
                """
        res = execute_read_query(self.database_conn, query)
        if len(res) != 0:
            return 1 if res[0][0] == 1 else 3
        return -1

    def check_if_need_to_update_daily_tasks(self, user_id: int) -> bool:
        query = f"""
                    SELECT last_update FROM user_daily_tasks_updated WHERE  
                    user_id = '{user_id}';
                """
        res = execute_read_query(self.database_conn, query)
        return not res or res[0][0] != cur_date()

    # @task_type should be one of:
    # 1) 'small'
    # 2) 'medium'
    # 3) 'class_license'
    # 4) 'any' (Do not take into consideration type of the task)
    def get_random_task(self, task_type: str) -> list:
        query = f"""SELECT * FROM tasks"""
        if task_type != 'any':
            query += f""" WHERE type = '{task_type}'"""
        query += f""" ORDER BY RANDOM() LIMIT 1"""
        task = execute_read_query(self.gamedata_conn, query)
        return task[0]

    def regenerate_daily_tasks(self, user_id: int) -> None:
        # Delete outdated daily tasks (if they exist)
        query = f"""
                    DELETE FROM user_daily_tasks WHERE  
                    user_id = '{user_id}';
                """
        execute_query(self.database_conn, query)
        query = f"""
                    DELETE FROM user_multiplayer_daily_tasks WHERE  
                    user_id = '{user_id}';
                """
        execute_query(self.database_conn, query)
        # Add new random tasks
        random_small_task = self.get_random_task('small')
        random_medium_task = self.get_random_task('medium')
        random_class_license_task = self.get_random_task('class_license')
        random_special_task = self.get_random_task('special')
        random_random_task = self.get_random_task('random')
        query = f"""
                    INSERT INTO user_daily_tasks (user_id,task_id) VALUES
                    ('{user_id}','{random_small_task[0]}'),
                    ('{user_id}','{random_medium_task[0]}'),
                    ('{user_id}','{random_class_license_task[0]}');
                """
        execute_query(self.database_conn, query)

        query = f"""
                    INSERT INTO user_multiplayer_daily_tasks (user_id,task_id) VALUES
                    ('{user_id}','{random_special_task[0]}'),
                    ('{user_id}','{random_random_task[0]}');
                """
        execute_query(self.database_conn, query)

        # Update user_daily_tasks_updated table
        query = f"""
                    INSERT OR REPLACE INTO user_daily_tasks_updated (user_id, last_update)
                    VALUES ('{user_id}', '{cur_date()}');
                """
        execute_query(self.database_conn, query)

    def user_multiplayer_accept_task(self, sender_id: int, receiver_id: int) -> None:
        query = f"""
                SELECT user2_id, user3_id, user4_id FROM multiplayer_task_participants WHERE user1_id = {sender_id}
                """
        res = execute_read_query(self.database_conn, query)[0]
        for i in range(len(res)):
            if res[i] == receiver_id:
                query = f"""
                        UPDATE multiplayer_task_participants SET is_user{i + 2}_accepted = 1 WHERE user1_id = {sender_id}
                        """
                execute_query(self.database_conn, query)
                break

    def check_if_request_already_exists_in_multiplayer(self, user_id: int) -> bool:
        query = f"""
                SELECT id FROM multiplayer_task_participants WHERE user1_id = {user_id}
                """
        res = execute_read_query(self.database_conn, query)
        if not len(res):
            return False
        return True

    def delete_multiplayer_task_participants(self, sender_id: int) -> None:
        query = f"""
                DELETE FROM multiplayer_task_participants WHERE user1_id = {sender_id}
                """
        execute_query(self.database_conn, query)

    def get_cur_user_tasks(self, user_id: int, is_multiplayer: bool) -> dict:
        attach_query = """ATTACH '../db/gamedata.db' AS gamedata;"""
        execute_query(self.database_conn, attach_query)
        if not is_multiplayer:
            query = f"""
                        SELECT user_daily_tasks.task_id, gamedata.tasks.type, user_daily_tasks.is_completed
                        FROM user_daily_tasks
                        JOIN gamedata.tasks ON gamedata.tasks.id = user_daily_tasks.task_id
                        WHERE user_daily_tasks.user_id = '{user_id}';
                    """
        else:
            query = f"""
                        SELECT user_multiplayer_daily_tasks.task_id, gamedata.tasks.type, user_multiplayer_daily_tasks.is_completed
                        FROM user_multiplayer_daily_tasks
                        JOIN gamedata.tasks ON gamedata.tasks.id = user_multiplayer_daily_tasks.task_id
                        WHERE user_multiplayer_daily_tasks.user_id = '{user_id}';
                    """
        res = execute_read_query(self.database_conn, query)
        if not is_multiplayer and len(res) != 3:
            logging.warning('[Single task] Query result length is not equal to expected in function get_cur_user_tasks')
        elif is_multiplayer and len(res) != 2:
            logging.warning(
                '[Multiplayer task] Query result length is not equal to expected in function get_cur_user_tasks')
        tasks_list = {str(task_type): task_id if is_completed == 0 else -1 for task_id, task_type, is_completed in res}
        return tasks_list

    def get_task_by_id(self, task_id: int) -> list:
        query = f"""
                SELECT * FROM tasks WHERE id = '{task_id}';
                """
        res = execute_read_query(self.gamedata_conn, query)
        return res[0]

    def add_multiplayer_participants(self, user_id: int, task_id: int, text: str):
        try:
            ids = list(map(int, text.split()))
        except ValueError:
            return False, "ID должны быть числовым значением"
        if len(ids) != len(set(ids)):
            return False, "Вы ввели два одинаковых пользователя"
        if user_id in ids:
            return False, "Вы не можете пригласить самого себя"
        if len(ids) < 3:
            ids.extend([0] * (3 - len(ids)))
        is_accepted = []
        for i in ids:
            if i == 0:
                is_accepted.append(1)
            else:
                is_accepted.append(0)
        query = f"""
                INSERT INTO multiplayer_task_participants (task_id, user1_id, user2_id, user3_id, user4_id, 
                is_user2_accepted, is_user3_accepted, is_user4_accepted)
                VALUES ('{task_id}', '{user_id}', '{ids[0]}', '{ids[1]}', '{ids[2]}', 
                '{is_accepted[0]}', '{is_accepted[1]}', '{is_accepted[2]}')
                """
        execute_query(self.database_conn, query)
        return True, "Запросы на участие успешно отправлены"

    def get_top_10_players(self) -> list:
        query = """
                    SELECT personal_username, username, exp FROM users
                    ORDER BY exp
                    DESC LIMIT 10
                """
        return execute_read_query(self.database_conn, query)

    def create_poll(self, poll_id, name, descr, start_time, duration, exp_reward) -> None:
        query = f"""
                    INSERT INTO
                    polls (poll_id, name, descr, start_time, duration, exp_reward)
                    VALUES
                    ('{poll_id}', '{name}', '{descr}', '{start_time}', '{duration}', '{exp_reward}');
                """
        execute_query(self.database_conn, query)

    def get_duel_opponent(self, duel_id, player_id):
        query = f"""
                SELECT sender_id, receiver_id FROM duels WHERE id = {duel_id}
                """
        res = execute_read_query(self.database_conn, query)
        if player_id == res[0][0]:
            return res[0][1]
        return res[0][0]

    def create_poll_from_text(self, poll_id, text) -> None:
        fields = text.split('\n')
        name, descr, start_time, duration, exp_reward = fields[:5]
        self.create_poll(poll_id, name, descr, start_time, duration, exp_reward)

    def get_poll_votes(self, poll_id, col: str) -> list:
        query = f"SELECT {col} FROM polls WHERE poll_id={poll_id}"
        return execute_read_query(self.database_conn, query)

    def get_poll_votes_both_col(self, poll_id) -> list:
        return [self.get_poll_votes(poll_id, 'for')[0][0], self.get_poll_votes(poll_id, 'against')[0][0]]

    def increment_poll_votes(self, poll_id, col: str) -> None:
        cur_votes = int(self.get_poll_votes(poll_id, col)[0][0])
        query = f"""
                    UPDATE polls
                    SET '{col}' = '{cur_votes + 1}'
                    WHERE poll_id = '{poll_id}';
                """
        execute_query(self.database_conn, query)

    def finish_poll(self, poll_id) -> None:
        query = f"""
                    UPDATE polls
                    SET 'is_ended' = '1'
                    WHERE poll_id = '{poll_id}';
                """
        execute_query(self.database_conn, query)

    def create_global_event_from_poll(self, poll_id) -> None:
        query = "INSERT INTO global_events (name, descr, start_time, duration, exp_reward) SELECT name, descr, " \
                f"start_time, duration, exp_reward FROM polls WHERE poll_id = {poll_id}"
        execute_query(self.database_conn, query)

    # This is a function that updates the experience points of a user in the database. It takes in two arguments,
    # the user_id of the user whose experience points need to be updated and the amount of experience points to add. It
    # fetches the current experience points of the user from the database, adds the new experience points to it,
    # and then updates the database with the new experience points.
    def add_exp(self, user_id: int, exp: int) -> None:
        query = f"SELECT exp FROM users WHERE id={user_id}"
        db_data = execute_read_query(self.database_conn, query)
        self.update_users('exp', int(db_data[0][0]) + int(exp), user_id)

    def create_user(self, user_id, username) -> None:
        create_users = f"""
                INSERT INTO
                users (id, username, personal_username)
                VALUES
                ('{user_id}', '{username}', '{username}');
                """
        execute_query(self.database_conn, create_users)

    def get_user_info(self, user_id) -> list:
        query = f"SELECT personal_username, game_class, exp, game_subclass FROM users WHERE id={user_id}"
        return execute_read_query(self.database_conn, query)

    def get_user_nick(self, user_id) -> str:
        query = f"SELECT personal_username FROM users WHERE id={user_id}"
        return execute_read_query(self.database_conn, query)[0][0]

    def get_20_closest_global_events(self) -> list:
        query = """
                SELECT * FROM global_events
                WHERE is_complited = 0
                ORDER BY start_time
                DESC LIMIT 20
            """
        return execute_read_query(self.database_conn, query)

    def get_event_by_id(self, event_id):
        query = f"""
                SELECT * FROM global_events WHERE id = {event_id}
                """
        return execute_read_query(self.database_conn, query)

    def complete_task(self, event_id: int) -> None:
        query = f"""
                UPDATE global_events SET is_complited = 1 WHERE id = '{event_id}'
                """
        execute_query(self.database_conn, query)
        query = f"""
                DELETE FROM global_events_participants WHERE id = '{event_id}'
                """
        execute_query(self.database_conn, query)

    def is_complited(self, event_id: int) -> bool:
        query = f"""
                SELECT is_complited FROM global_events WHERE id = '{event_id}'
                """
        return bool(execute_read_query(self.database_conn, query)[0][0])

    def get_all_global_events(self) -> list:
        query = "SELECT * FROM global_events"
        return execute_read_query(self.database_conn, query)

    def delete_global_event(self, event_id) -> None:
        query = f"DELETE FROM global_events WHERE id = {event_id}"
        execute_query(self.database_conn, query)

    def check_if_user_is_admin(self, user_id) -> int:
        query = f"SELECT admin FROM users WHERE id={user_id}"
        return execute_read_query(self.database_conn, query)[0][0]

    def get_admins_id(self) -> list:
        query = "SELECT id FROM users WHERE admin = 1"
        return execute_read_query(self.database_conn, query)

    def get_all_user_ids(self) -> list:
        query = f"""
                    SELECT id FROM users
                """
        res = execute_read_query(self.database_conn, query)
        all_ids = []
        for i in range(len(res)):
            all_ids.append(res[i][0])
        return all_ids

    # This functions checks for existing duels and returns whether there could be
    # initialized new duel with given params
    def check_if_could_send_duel(self, sender_id, receiver_id) -> bool:
        query = f"""
                    SELECT id FROM duels
                    WHERE (sender_id='{sender_id}'      OR 
                          sender_id='{receiver_id}')    AND
                          (receiver_id='{receiver_id}'  OR
                          receiver_id='{sender_id}')    AND
                          status != 'finished'
                """
        res = execute_read_query(self.database_conn, query)

        if not res:
            return True

        query = f"""
                    SELECT id FROM duels
                    WHERE ((sender_id='{sender_id}'     OR 
                          sender_id='{receiver_id}')    AND
                          status == 'ongoing')          OR
                          ((receiver_id='{sender_id}'   OR
                          receiver_id='{receiver_id}')  AND
                          status == 'ongoing');
                """
        res = execute_read_query(self.database_conn, query)
        return False

    def add_participant_to_open_duel(self, sender_id: int, receiver_id: int):
        query = f"""
                UPDATE duels SET receiver_id = {receiver_id} WHERE sender_id = {sender_id}
                """
        execute_query(self.database_conn, query)

    def add_pending_duel(self, sender_id, receiver_id) -> None:
        query = f"""
                    INSERT INTO duels (sender_id, receiver_id, status)
                    VALUES('{sender_id}', '{receiver_id}', 'pending');
                """
        execute_query(self.database_conn, query)

    def start_duel(self, duel_id) -> None:
        query = f"""
                    UPDATE duels 
                    SET status = 'ongoing' 
                    WHERE id = '{duel_id}';
                """
        execute_query(self.database_conn, query)

    # @outcome should be set either to 1 (for sender win) or 2 (for receiver win)
    def finish_duel(self, duel_id, outcome) -> bool:
        if outcome != 1 and outcome != 2:
            logging.warning("Outcome variable in Database::finish_duel function is invalid!")
            return False
        query = f"""
                    UPDATE duels
                    SET status = 'finished',
                    outcome = '{outcome}'
                    WHERE id = '{duel_id}';
                """
        execute_query(self.database_conn, query)
        return True

    def get_pending_duel(self, sender_id, receiver_id) -> int:
        query = f"""
                    SELECT id FROM duels 
                    WHERE sender_id = '{sender_id}' AND 
                          receiver_id = '{receiver_id}' AND 
                          status = 'pending';
                """
        res = execute_read_query(self.database_conn, query)
        if not res:
            logging.error(
                f"Trying to initialize duel object while it does not exist in database.duels! Duel sender, receiver = {sender_id}, {receiver_id}")
            return -1
        if len(res) > 1:
            logging.error(
                f"Trying to initialize duel object while it exisits more then once in database.duels! Duel sender, receiver = {sender_id}, {receiver_id}")
            return -1

        return res[0][0]

    def load_armor_enchantments_perks(self, ench_id) -> list:
        query = f"""
                    SELECT  name, 
                            mirror_dmg, 
                            physical_damage_decr, 
                            magic_damage_decr,
                            element_damage_decr,
                            no_damage_chance,
                            health_buff 
                    FROM enchantments_armor
                    WHERE id = '{ench_id}';
                """
        ans_list = []
        res = execute_read_query(self.gamedata_conn, query)
        for i in range(len(res[0])):
            ans_list.append(res[0][i])
        return ans_list

    def load_weapon_enchantments_perks(self, ench_id) -> list:
        query = f"""
                    SELECT  name, 
                            physical_dmg_incr, 
                            stun_chance,
                            crit_chance,
                            bleeding_chance,
                            armor_ignore_chance,
                            vampirism,
                            element_dmg_incr 
                    FROM enchantments_weapon 
                    WHERE id = '{ench_id}';
                """
        return (execute_read_query(self.gamedata_conn, query))[0]

    def get_all_armor_enchantments_ids(self) -> list:
        query = f"""
                    SELECT id FROM enchantments_armor;
                """
        ids_list = []
        res = execute_read_query(self.gamedata_conn, query)
        for i in range(len(res)):
            ids_list.append(res[i][0])
        return ids_list

    def get_all_weapon_enchantments_ids(self) -> list:
        query = f"""
                    SELECT id FROM enchantments_weapon;
                """
        ids_list = []
        res = execute_read_query(self.gamedata_conn, query)
        for i in range(len(res)):
            ids_list.append(res[i][0])
        return ids_list

    def add_chat_id(self, chat_id: int, title: str) -> None:
        query = f"""
                    INSERT INTO chats (chat_id, title)
                    VALUES('{chat_id}', '{title}');
                """
        execute_query(self.database_conn, query)

    def delete_chat_id(self, chat_id: int) -> None:
        query = f"DELETE FROM chats WHERE chat_id = {chat_id}"
        execute_query(self.database_conn, query)

    def get_chat_ids(self) -> list:
        query = f"SELECT * FROM chats"
        chats = execute_read_query(self.database_conn, query)
        return chats

    def get_user_active_weapon_meta_id(self, user_id) -> int:
        query = f"""
                    SELECT active_weapon_meta_id FROM users 
                    WHERE id = '{user_id}';
                """
        return execute_read_query(self.database_conn, query)[0][0]

    def get_user_active_armor_meta_id(self, user_id) -> int:
        query = f"""
                    SELECT active_armor_meta_id FROM users 
                    WHERE id = '{user_id}';
                """
        return execute_read_query(self.database_conn, query)[0][0]

    # Only weapons and armor ids for @meta_id are allowed
    def load_all_item_info_for_battle_from_meta(self, meta_id) -> list:
        attach_query = "ATTACH '../db/gamedata.db' AS gamedata;"
        execute_query(self.database_conn, attach_query)

        query = f"""
                    SELECT  items_owned.base_item_id,
                            items_owned.enchantments, 
                            gamedata.base_items.name,
                            gamedata.base_items.strength
                    FROM items_owned
                    JOIN gamedata.base_items ON items_owned.base_item_id = gamedata.base_items.id
                    WHERE   items_owned.meta_item_id = '{meta_id}';
                """
        res = execute_read_query(self.database_conn, query)
        return res[0]

    def get_ench_name_by_id(self, ench_id, ench_type: str) -> str:
        query = ""
        if ench_type == 'armor':
            query = f"""
                        SELECT name FROM enchantments_armor WHERE id = '{ench_id}';
                    """
        elif ench_type == 'weapon':
            query = f"""
                        SELECT name FROM enchantments_weapon WHERE id = '{ench_id}';
                    """
        else:
            logging.error("Got wrong ench_type in get_ench_name_by_id()!")
            return "UNKNOWN_ENCHANTMENT"

        return str(execute_read_query(self.gamedata_conn, query)[0][0])

    def set_weapon(self, user_id, weapon_id):
        query = f"UPDATE users SET active_weapon_meta_id = {weapon_id} WHERE id = {user_id}"
        execute_query(self.database_conn, query)

    def get_item_file_name(self, user_id) -> tuple[str, str]:
        query = f"SELECT active_armor_meta_id, active_weapon_meta_id FROM users WHERE id = {user_id}"
        active_items = execute_read_query(self.database_conn, query)[0]
        query = f"SELECT base_item_id FROM items_owned WHERE meta_item_id = {active_items[0]} " \
                f"OR meta_item_id = {active_items[1]}"
        items_ids = execute_read_query(self.database_conn, query)
        query = f"SELECT filename FROM base_items WHERE id = {items_ids[0][0]} OR id = {items_ids[1][0]}"
        file_names = execute_read_query(self.gamedata_conn, query)
        return file_names[0][0], file_names[1][0]

    def set_armor(self, user_id, armor_id):
        query = f"UPDATE users SET active_armor_meta_id = {armor_id} WHERE id = {user_id}"
        execute_query(self.database_conn, query)

    def get_users_items(self, user_id):
        query = f"""
                    SELECT base_item_id, enchantments, meta_item_id FROM items_owned WHERE owner_id = {user_id};
                """
        items = execute_read_query(self.database_conn, query)
        result = []
        for i in range(len(items)):
            base_item_id = items[i][0]
            meta_item_enchs = items[i][1]
            meta_item_id = items[i][2]
            query = f"""
                        SELECT name, type, strength, rarity FROM base_items WHERE id = {base_item_id}
                    """
            base_query_res = execute_read_query(self.gamedata_conn, query)[0]
            base_item_name = base_query_res[0]
            base_item_type = base_query_res[1]
            base_item_strength = base_query_res[2]
            base_item_rarity = base_query_res[3]
            result.append([base_item_name, meta_item_enchs, base_item_type, base_item_strength, base_item_rarity, meta_item_id])
        return result

    def add_enchant(self, meta_item_id: str, item_type: str, user_id: int):
        if not meta_item_id.isdigit():
            return "Введите ID!"
        query = f"SELECT money FROM users WHERE id = {user_id}"
        money = int(execute_read_query(self.database_conn, query)[0][0])
        if money < 200:
            return "У Вас недостаточно средств для зачарования!"
        query = f"SELECT id, name FROM enchantments_{item_type} ORDER BY RANDOM() LIMIT 1"
        enchant = execute_read_query(self.gamedata_conn, query)
        query = f"SELECT enchantments FROM items_owned WHERE meta_item_id = {meta_item_id}"
        cur_enchants = execute_read_query(self.database_conn, query)
        if len(cur_enchants) == 0:
            return "Предмета с таким ID не существует!"
        query = f"UPDATE users SET money = money - 200 WHERE id = {user_id}"
        execute_query(self.database_conn, query)
        if cur_enchants[0][0] is None:
            query = f"UPDATE items_owned SET enchantments = {enchant[0][0]} WHERE meta_item_id = {meta_item_id}"
        else:
            if str(enchant[0][0]) in str(cur_enchants[0][0]):
                return f"Вы зачаровали предмет на чару '{enchant[0][1]}', " \
                       f"но эта чара уже была на Вашем оружие. Ничего не изменилось."
            query = f"UPDATE items_owned SET enchantments = '{str(cur_enchants[0][0]) + ',' + str(enchant[0][0])}' " \
                    f"WHERE meta_item_id = {meta_item_id}"
        execute_query(self.database_conn, query)
        return f"Вы успешно зачаровали предмет на чару '{enchant[0][1]}'"

    def craft_item(self, user_id, item_id):
        query = f"SELECT res1_id, res2_id FROM craft_consumable WHERE cons_id = {item_id}"
        res_ids = execute_read_query(self.gamedata_conn, query)[0]
        query = f"""
                SELECT COUNT(*) FROM res_owned
                WHERE user_id = {user_id} AND res_id IN ({res_ids[0]}, {res_ids[1]}) AND count > 0
            """
        if_can_craft = execute_read_query(self.database_conn, query)[0][0]
        if if_can_craft != 2:
            return "У Вас недостаточно ресурсов для создания этого предмета!"
        query = f"""
                UPDATE res_owned
                SET count = count - 1
                WHERE user_id = {user_id} and (res_id = {res_ids[0]} or res_id = {res_ids[1]})
                """
        execute_query(self.database_conn, query)
        query = f"""
                INSERT OR REPLACE INTO consumable_owned (user_id, consum_id, count)
                VALUES (
                    {user_id},
                    {item_id},
                    COALESCE((SELECT count + 1 FROM consumable_owned WHERE user_id = {user_id} AND consum_id = {item_id}), 1)
                );
                """
        execute_query(self.database_conn, query)
        return f"Вы успешно создали предмет №{item_id}"

    def get_inventory_by_user_id(self, user_id):
        query = f"SELECT res_id, count FROM res_owned WHERE user_id = {user_id} AND count > 0 ORDER BY count DESC"
        res_ids_old = execute_read_query(self.database_conn, query)
        if len(res_ids_old) == 0:
            return "Ваш рюкзак пуст..."
        res_ids = [item[0] for item in res_ids_old]
        res_count = [item[1] for item in res_ids_old]
        case_query = ' '.join([f"WHEN {id} THEN {index}" for index, id in enumerate(res_ids)])
        query = f"SELECT Name FROM res WHERE id IN ({','.join(str(id) for id in res_ids)}) ORDER BY CASE id {case_query} END"
        names = execute_read_query(self.gamedata_conn, query)
        names = [name[0] for name in names]
        text = "Вот что Вы нашли в рюкзаке:\n\n"
        items = [f"{names[i]} - {res_count[i]} шт." for i in range(len(names))]
        text += "\n".join(items)
        return text

    def add_guild_request(self, user_id: int, res_string: str):
        res_data = res_string.split()
        if len(res_data) != 2:
            return "Вы неверно ввели запрос!"
        if not res_data[0].isdigit() or not res_data[1].isdigit():
            return "Одно из введённых значений не является числом!"
        if int(res_data[0]) > 10 or int(res_data[0]) < 1:
            return "Таких ресурсов не существует!"
        if int(res_data[1]) > 10:
            return "Не жадничай! Запросить можно не более 10 ресурсов!"
        query = f"SELECT sender_id, res_id, is_got FROM guild_house WHERE sender_id = {user_id} AND res_id = {res_data[0]} AND is_got = 0"
        res = execute_read_query(self.database_conn, query)
        if len(res) != 0:
            return "Вы уже запросили этот ресурс!"
        query = f"""
                INSERT INTO guild_house (sender_id, res_id, count)
                VALUES ({user_id}, {res_data[0]}, {res_data[1]})
                """
        execute_query(self.database_conn, query)
        return "Вы успешно создали запрос!"

    def get_res_name_by_id(self, res_id) -> str:
        query = f"SELECT Name FROM res WHERE id = {res_id}"
        return execute_read_query(self.gamedata_conn, query)[0][0]

    def get_guild_requests(self, user_id) -> tuple[bool, str]:
        query = f"SELECT id, sender_id, res_id, count FROM guild_house " \
                f"WHERE is_got = 0 AND sender_id <> {user_id} ORDER BY count LIMIT 20"
        requests = execute_read_query(self.database_conn, query)
        if len(requests) == 0:
            return False, "Сейчас нет доступных запросов!"
        message = "Вот запросы людей:\n\n"
        for request in requests:
            message += f"ID: {request[0]}\n" \
                       f"Запрашивает: {db.get_user_nick(request[1])}\n" \
                       f"Ресурс: {db.get_res_name_by_id(request[2])}\n" \
                       f"Количество: {request[3]}\n\n"
        message += "Введите ID запроса, которому хотите помочь!"
        return True, message

    def send_res(self, user_id, request_id: str):
        if not request_id.isdigit():
            return "Вы ввели не число!"
        query = f"SELECT sender_id, res_id, count FROM guild_house WHERE id = {request_id}"
        request = execute_read_query(self.database_conn, query)[0]
        if int(user_id) == int(request[0]):
            return "Зачем Вам отправлять ресурсы самому себе? Хотя, если очень хочется... Всё же нет."
        query = f"SELECT EXISTS(SELECT 1 FROM res_owned WHERE user_id = {user_id} AND count >= {request[2]} AND " \
                f"res_id = {request[1]})"
        is_enough = int(execute_read_query(self.database_conn, query)[0][0])
        if not is_enough:
            return "У вас недостаточно ресурсов этого типа!"
        # Забираем ресурсы у user_id
        query = f"""
               UPDATE res_owned
               SET count = count - {request[2]}
               WHERE user_id = {user_id} and res_id = {request[1]}
               """
        execute_query(self.database_conn, query)
        # Отдаём их sender_id
        query = f"SELECT EXISTS(SELECT 1 FROM res_owned WHERE user_id = {request[0]} AND res_id = {request[1]})"
        is_exists = int(execute_read_query(self.database_conn, query)[0][0])
        if is_exists:
            query = f"UPDATE res_owned SET count = count + {request[2]} WHERE user_id = {request[0]}"
        else:
            query = f"INSERT INTO res_owned (user_id, res_id, count)" \
                    f"VALUES ({request[0]}, {request[1]}, {request[2]})"
        execute_query(self.database_conn, query)
        query = f"UPDATE guild_house SET 'is_got' = 1 WHERE sender_id = {request[0]} AND res_id = {request[1]}"
        execute_query(self.database_conn, query)
        return "Вы успешно отправили ресурсы!"

    def get_eng_class(self, user_id: int) -> str:
        rus = ['Маг', 'Лучник', 'Рыцарь', 'Охотник']
        eng = ['mage', 'archer', 'sword', 'hunter']
        classes = dict(zip(rus, eng))
        query = f"SELECT game_class FROM users WHERE id = {user_id}"
        rus_class = execute_read_query(self.database_conn, query)[0][0]
        return classes[rus_class]

    def get_rus_class(self, user_id: int) -> str:
        query = f"SELECT game_class FROM users WHERE id = {user_id}"
        rus_class = execute_read_query(self.database_conn, query)[0][0]
        return rus_class

    def show_possible_item_crafts(self, item_type: str, game_class: str):
        query = f"SELECT id, item_tier, res1_id, res1_count, res2_id, res2_count, gold_count " \
                f"FROM craft_items WHERE item_type = '{item_type}' AND class = '{game_class}'"
        items = execute_read_query(self.gamedata_conn, query)
        text = "Доступные предметы для создания:\n\n"
        for item in items:
            text += f"ID: {item[0]}\n" \
                    f"Редкость: {item[1]}\n" \
                    f"Создаётся из:\n" \
                    f"Ресурс №1: {db.get_res_name_by_id(item[2])} - {item[3]} шт.\n" \
                    f"Ресурс №2: {db.get_res_name_by_id(item[4])} - {item[5]} шт.\n" \
                    f"Золото: {item[6]} монет\n\n"
        return text

    def get_user_money(self, user_id: int) -> int:
        query = f"SELECT money FROM users WHERE id = {user_id}"
        return execute_read_query(self.database_conn, query)[0][0]

    def create_new_item(self, user_id: int, item_id: str):
        if not item_id.isdigit():
            return "Неправильный ввод! Попробуйте ещё раз!"
        if int(item_id) > 32 or int(item_id) < 1:
            return "Такого оружия не существует!"
        query = f"SELECT res1_id, res1_count, res2_id, res2_count, gold_count, " \
                f"item_tier, item_type FROM craft_items WHERE id = '{item_id}'"
        item = execute_read_query(self.gamedata_conn, query)[0]
        query = f"SELECT 1 FROM res_owned WHERE user_id = {user_id} AND res_id = {item[0]} AND count >= {item[1]}"
        if_res1_enough = execute_read_query(self.database_conn, query)
        if len(if_res1_enough) == 0:
            return "У Вас не хватает 1-го ресурса!"
        query = f"SELECT 1 FROM res_owned WHERE user_id = {user_id} AND res_id = {item[2]} AND count >= {item[3]}"
        if_res2_enough = execute_read_query(self.database_conn, query)
        if len(if_res2_enough) == 0:
            return "У Вас не хватает 2-го ресурса!"
        gold = self.get_user_money(user_id)
        if item[4] > gold:
            return "У Вас недостаточно золота!"
        query = f"""
            UPDATE res_owned
            SET count = CASE
                WHEN res_id = {item[0]} THEN count - {item[1]}
                WHEN res_id = {item[2]} THEN count - {item[3]}
                ELSE count
                END
            WHERE res_id IN ({item[0]}, {item[2]})
        """
        execute_query(self.database_conn, query)
        query = f"UPDATE users SET money = money - {item[4]} WHERE id = {user_id}"
        execute_query(self.database_conn, query)
        query = f"SELECT id, name FROM base_items WHERE rarity = {item[5]} AND " \
                f"class = '{db.get_rus_class(user_id)}' AND type = '{item[6]}'"
        items_to_rand = execute_read_query(self.gamedata_conn, query)
        created_item = random.choice(items_to_rand)
        query = f"INSERT INTO items_owned (owner_id, base_item_id, date) VALUES " \
                f"('{user_id}', '{created_item[0]}', '{cur_date()}')"
        execute_query(self.database_conn, query)
        return f'Вы создали предмет "{created_item[1]}"!'

    def get_ability_main_info(self, ability_id) -> list:
        query = f"""
                    SELECT name, buff, dmg_perc, area, target
                    FROM abilities
                    WHERE id = {ability_id};
                """
        return execute_read_query(self.gamedata_conn, query)[0]

    def get_buff_info(self, buff_id) -> list:
        query = f"""
                    SELECT name, stun, dmg, time, defence, miss
                    FROM buffs
                    WHERE id = {buff_id};
                """
        return execute_read_query(self.gamedata_conn, query)[0]

    def get_top_arena(self) -> str:
        query = """
                SELECT *
                FROM duels
                WHERE status = 'finished'
                """
        all_duels = execute_read_query(self.database_conn, query)
        top = defaultdict(int)
        for _, player1_id, player2_id, result, _ in all_duels:
            win_id, lose_id = (player1_id, player2_id) if result == 1 else (player2_id, player1_id)
            top[win_id] -= 1
            top[lose_id] += 2
        top = sorted(top.items(), key=lambda item: item[1])
        res = 'Топ арены:\n'
        for num, (player_id, score) in enumerate(top, start=1):
            res += f'{num}. Игрок с id: {player_id} со счётом {score}\n'
        return res

    def get_duels_record_for_user(self, user_id: int) -> str:
        query_wins = f"""
                            SELECT id
                            FROM duels
                            WHERE (sender_id = {user_id} AND outcome = 1) OR
                                  (receiver_id = {user_id} AND outcome = 2);
                      """
        wins = len(execute_read_query(self.database_conn, query_wins))

        query_losses = f"""
                            SELECT id
                            FROM duels
                            WHERE (sender_id = {user_id} AND outcome = 2) OR
                                  (receiver_id = {user_id} AND outcome = 1);
                       """
        losses = len(execute_read_query(self.database_conn, query_losses))

        return str(wins) + "-" + str(losses)

    def get_all_abilities_ids_for_class(self, class_id: str):
        if class_id != "Маг" and class_id != "Лучник" and class_id != "Рыцарь" and class_id != "Охотник":
            logging.error(f"In get_all_abilities_ids_for_class() got unknown class_id = {class_id}")
        query = f"""
                    SELECT id FROM abilities WHERE class = '{class_id}'
                """
        res = execute_read_query(self.gamedata_conn, query)
        ans = []
        for r in res:
            ans.append(r[0])
        return ans

    def get_player_class_by_id(self, user_id):
        query = f"""
                    SELECT game_class FROM users WHERE id = '{user_id}';
                """
        return execute_read_query(self.database_conn, query)[0][0]

    def get_ability_name(self, ability_id) -> str:
        query = f"""
                    SELECT name FROM abilities WHERE id = '{ability_id}';
                """
        return execute_read_query(self.gamedata_conn, query)[0][0]

    def get_ability_id_from_name(self, ability_name) -> int:
        query = f"""
                    SELECT id FROM abilities WHERE name = '{ability_name}';
                """
        return execute_read_query(self.gamedata_conn, query)[0][0]

    def get_dange_main_info(self, dange_id) -> list:
        query = f"""
                    SELECT name, fights, filename FROM danges WHERE id = '{dange_id}';
                """
        return execute_read_query(self.gamedata_conn, query)[0]

    def get_all_mobs_ids_on_dange(self, dange_id) -> list:
        query = f"""
                    SELECT enemy_id FROM danges_enemies WHERE dange_id = '{dange_id}';
                """
        res = []
        for i in execute_read_query(self.gamedata_conn, query):
            res.append(i[0])
        return res

    def get_mob_main_info(self, mob_id: int) -> list:
        query = f"""
                    SELECT name, health, attack, defence FROM enemies WHERE id = '{mob_id}';
                """
        return execute_read_query(self.gamedata_conn, query)[0]

    def get_consumable_main_info(self, consumable_id: int) -> list:
        query = f"""
                    SELECT name, buff, area, target FROM consumable WHERE id = '{consumable_id}';
                """
        return execute_read_query(self.gamedata_conn, query)[0]

    def get_list_of_owned_consumables(self, user_id: int) -> list:
        query = f"""
                    SELECT consum_id, count FROM consumable_owned WHERE user_id = '{user_id}';
                """
        return execute_read_query(self.database_conn, query)

    def use_consumable_for_user(self, user_id: int, consum_id: int) -> None:
        query = f"""
                    UPDATE consumable_owned 
                    SET count = (SELECT count FROM consumable_owned 
                                WHERE user_id = '{user_id}' AND consum_id = '{consum_id}') - 1
                    WHERE user_id = '{user_id}' AND consum_id = '{consum_id}';
                """
        execute_query(self.database_conn, query)

    def get_consumable_id_from_name(self, consumable_name: str) -> int:
        query = f"""
                    SELECT id FROM consumables WHERE name = '{consumable_name}';
                """
        return execute_read_query(self.gamedata_conn, query)[0][0]

    def give_default_items_to_user(self, user_id: int, user_class_in_russian: str) -> None:
        query = f"""
                    SELECT id 
                    FROM base_items 
                    WHERE rarity = 1
                    AND type = 'armor'
                    AND class = '{user_class_in_russian}'
                    ORDER BY cost
                    LIMIT 1;
                 """
        base_armor_id = execute_read_query(self.gamedata_conn, query)[0][0]

        query = f"""
                    SELECT id 
                    FROM base_items 
                    WHERE rarity = 1
                    AND type = 'weapon'
                    AND class = '{user_class_in_russian}'
                    ORDER BY cost
                    LIMIT 1;
                 """
        base_weapon_id = execute_read_query(self.gamedata_conn, query)[0][0]

        create_armor_query = f"""
                                INSERT INTO items_owned (owner_id, base_item_id, enchantments, date)
                                VALUES ({user_id}, {base_armor_id}, "", '{cur_date()}');
                              """
        execute_query(self.database_conn, create_armor_query)

        meta_armor_id_query = f"""
                                SELECT meta_item_id FROM items_owned
                                WHERE base_item_id = {base_armor_id}
                                AND owner_id = {user_id};
                             """
        meta_armor_id = execute_read_query(self.database_conn, meta_armor_id_query)[0][0]

        create_weapon_query = f"""
                                INSERT INTO items_owned (owner_id, base_item_id, enchantments, date)
                                VALUES ({user_id}, {base_weapon_id}, "", '{cur_date()}');
                              """
        execute_query(self.database_conn, create_weapon_query)

        meta_weapon_id_query = f"""
                                    SELECT meta_item_id FROM items_owned
                                    WHERE base_item_id = {base_weapon_id}
                                    AND owner_id = {user_id};
                                 """
        meta_weapon_id = execute_read_query(self.database_conn, meta_weapon_id_query)[0][0]

        update_query = f"""
                            UPDATE users 
                            SET active_armor_meta_id = {meta_armor_id}, 
                            active_weapon_meta_id = {meta_weapon_id}
                            WHERE id = {user_id};
                        """
        execute_query(self.database_conn, update_query)

    def small_task_info_for_user(self, user_id: int) -> list:
        query = f"""
                    SELECT task_id 
                    FROM user_daily_tasks
                    WHERE user_id = {user_id};
                 """
        res = execute_read_query(self.database_conn, query)
        all_tasks = []
        for i in range(len(res)):
            all_tasks.append(res[i][0])

        query = f"""
                    SELECT id, exp_reward, item_reward, dange_id
                    FROM tasks
                    WHERE (id = {all_tasks[0]} OR
                          id = {all_tasks[1]} OR
                          id = {all_tasks[2]}) AND
                          type = 'small';
                 """
        task = execute_read_query(self.gamedata_conn, query)[0]
        return task

    def medium_task_info_for_user(self, user_id: int) -> list:
        query = f"""
                    SELECT task_id 
                    FROM user_daily_tasks
                    WHERE user_id = {user_id};
                 """
        res = execute_read_query(self.database_conn, query)
        all_tasks = []
        for i in range(len(res)):
            all_tasks.append(res[i][0])

        query = f"""
                    SELECT id, exp_reward, item_reward, dange_id
                    FROM tasks
                    WHERE (id = {all_tasks[0]} OR
                          id = {all_tasks[1]} OR
                          id = {all_tasks[2]}) AND
                          type = 'medium';
                 """
        task = execute_read_query(self.gamedata_conn, query)[0]
        return task

    def class_license_task_info_for_user(self, user_id: int) -> list:
        query = f"""
                    SELECT task_id 
                    FROM user_daily_tasks
                    WHERE user_id = {user_id};
                 """
        res = execute_read_query(self.database_conn, query)
        all_tasks = []
        for i in range(len(res)):
            all_tasks.append(res[i][0])

        query = f"""
                    SELECT id, exp_reward, item_reward, dange_id
                    FROM tasks
                    WHERE (id = {all_tasks[0]} OR
                          id = {all_tasks[1]} OR
                          id = {all_tasks[2]}) AND
                          type = 'class_license';
                 """
        task = execute_read_query(self.gamedata_conn, query)[0]
        return task


# Global Database variable
db = Database()
