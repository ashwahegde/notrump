from flask import current_app
from bluep.db import get_db

def execute_sql(sql: str, db_input: dict={}):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(sql, db_input)
    connection.commit()
    return cursor


def select_query(**query_dict):
    columns = query_dict["columns"]
    col_string = ",".join(columns)
    table_name = query_dict["table_name"]
    filters = query_dict["filters"]
    s = []
    for each in filters:
        s.append(each + "=:" + each)
    where_string = " and ".join(s)
    sql = "select {} from {} where {}".format(col_string, table_name, where_string)
    current_app.logger.debug(f'U={query_dict["userId"]} M=SQL: {sql}')
    cursor = execute_sql(sql, filters)
    return cursor

def update_rows(**query_dict):
    table_name = query_dict["table_name"]

    columns = query_dict["columns"]
    column_string = []
    for each in columns:
        column_string.append(each + "=:" + each)
    column_string = ", ".join(column_string)

    where_clause = query_dict["filters"]
    where_string = []
    for each in where_clause:
        where_string.append(each + "=:" + each)
    where_string = " and ".join(where_string)

    sql = "update {} set {} where {}".format(table_name, column_string, where_string)
    columns.update(where_clause)
    current_app.logger.debug(f'U={query_dict["userId"]} M=SQL: {sql}')
    cursor = execute_sql(sql, columns)
    print(cursor.rowcount)
    return cursor


def insert_row(**query_dict):
    columns = query_dict["columns"]
    table_name = query_dict["table_name"]

    col_string = ",".join(columns.keys())
    values = ":" + ", :".join(columns.keys())

    sql = "insert into {} ({}) values ({})".format(table_name, col_string, values)
    current_app.logger.info(f'U={query_dict["userId"]} M=SQL: {sql}')
    cursor = execute_sql(sql, columns)
    return cursor


def complex_query(sql, query_dict):
    current_app.logger.debug(f'U={query_dict["userId"]} M=SQL: {sql}')
    cursor = execute_sql(sql, query_dict)
    return cursor

def check_user(userId):
    columns = ["*"]
    filters = {
        "userId": userId,
    }
    c = select_query(userId=userId,table_name="users",columns=columns,filters=filters)
    if c.fetchone():
        return True
    else:
        return False

def check_tempUser(userId):
    columns = ["*"]
    filters = {
        "userId": userId,
    }
    c = select_query(userId=userId,table_name="tempUsers",columns=columns,filters=filters)
    if c.fetchone():
        return True
    else:
        return False

def check_email(emailId):
    columns = ["*"]
    filters = {
        "emailId": emailId,
    }
    c = select_query(userId=emailId,table_name="users",columns=columns,filters=filters)
    if c.fetchone():
        return True
    else:
        return False

def check_tempEmail(emailId):
    columns = ["*"]
    filters = {
        "emailId": emailId,
    }
    c = select_query(userId=emailId,table_name="tempUsers",columns=columns,filters=filters)
    if c.fetchone():
        return True
    else:
        return False

def check_otp(user_info):
    c = select_query(**{
        "userId": user_info["userId"],
        "table_name": "tempUsers",
        "columns": ["otp"],
        "filters": {
            "userId": user_info["userId"],
        }
    })
    otp =  c.fetchone()
    if otp:
        otp = otp[0]
    if otp == user_info["otp"]:
        return True
    else:
        return False

def get_passwordHash(userId):
        columns = ["passwordHash"]
        filters = {
            "userId": userId,
        }
        c = select_query(userId=userId,table_name="users",columns=columns,filters=filters)
        passwordHash = c.fetchone()
        if passwordHash:
            return passwordHash[0]
        return passwordHash

def get_tempPasswordHash(userId):
        columns = ["passwordHash"]
        filters = {
            "userId": userId,
        }
        c = select_query(userId=userId,table_name="tempUsers",columns=columns,filters=filters)
        passwordHash = c.fetchone()
        if passwordHash:
            return passwordHash[0]
        return passwordHash

def select_query_dict(**query_dict):
    columns = query_dict["columns"]
    cursor = select_query(**query_dict)
    info = {}
    arow = cursor.fetchone()
    if not arow:
        return {}
    for i,acol in enumerate(arow):
        info[columns[i]] = acol
    return info

def init_db():
    try:
        execute_sql('''CREATE TABLE users
            (
            userId text primary key,
            emailId text,
            passwordHash text
            )'''
        )
        execute_sql('''CREATE TABLE tempUsers
            (
            userId text primary key,
            emailId text,
            otp integer,
            passwordHash text
            )'''
        )
        execute_sql('''CREATE TABLE roomStatus
            (
            roomId integer not null,
            roomUserId integer not null,
            userId text,
            roomState text,
            points integer,
            lastWon integer,
            PRIMARY KEY (roomId, roomUserId)
            )'''
        )
        execute_sql('''CREATE TABLE roomInfo
            (
            roomId integer PRIMARY KEY AUTOINCREMENT,
            roomState text,
            roomCode integer,
            host text
            )'''
        )
        insert_row(**{
                "userId": "admin",
                "columns": {
                    "name": "roomInfo",
                    "seq": "1000",
                },
                "table_name": "sqlite_sequence"
            })
    except Exception as e:
        current_app.logger.error(f"error occured while creating table: {e}")
        raise "table already exists"
    c = execute_sql("INSERT INTO users VALUES ('ashwath','ashwaheg@abc.def','aaaaaaaaaaaaaaaaaaaaa')")
    c = execute_sql("INSERT INTO tempUsers VALUES ('ashwath','ashwaheg@abc.def','1111111111','aaaaaaaaaaaaaaaaaaaaa')")
    c = execute_sql("INSERT INTO roomInfo(roomState,roomCode,host) VALUES ('Y','12345','ashwath')")
    #c = execute_sql("INSERT INTO roomStatus(userId,roomUserId,roomState,points,lastWon) VALUES ('ashwath','1','A1,b2','1','0')")

if __name__ == "__main__":
    init_db()
