import datetime


def cur_time() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def cur_date() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d')


# This function is used to ensure that given time in a form of string
# could be used in the bot system (db + code) since we use everywhere
# only one determined time string format which is: "yyyy-MM-dd hh:mm:ss"
def ensure_time_format(time_str: str) -> bool:
    try:
        datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False

