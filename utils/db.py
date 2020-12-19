from flask import current_app
from bluep.db import get_db

def execute_sql(sql: str, db_input: dict={}):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(sql, db_input)
    connection.commit()
    return cursor


def select_query(**query_dict):
    filters = query_dict["filters"]
    s = []
    for each in filters:
        s.append(each + "=:" + each)
    where_string = " and ".join(s)
    sql = f"""
        select {",".join(query_dict["columns"])}
        from {query_dict["table_name"]}
        where {where_string}
        """

    userId = query_dict.get("userId","unknown_user")
    current_app.logger.debug(f'U={userId} M=SQL: {sql}')
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
    userId = query_dict.get("userId","unknown_user")
    current_app.logger.debug(f'U={userId} M=SQL: {sql}')
    cursor = execute_sql(sql, columns)
    print(cursor.rowcount)
    return cursor


def insert_row(**query_dict):
    columns = query_dict["columns"]
    table_name = query_dict["table_name"]

    col_string = ",".join(columns.keys())
    values = ":" + ", :".join(columns.keys())

    sql = "insert into {} ({}) values ({})".format(table_name, col_string, values)
    userId = query_dict.get("userId","unknown_user")
    current_app.logger.info(f'U={userId} M=SQL: {sql}')
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

def get_roomCode(roomId):
    columns = ["roomCode"]
    filters = {
        "roomId": roomId,
    }
    c = select_query(userId=None,table_name="roomInfo",columns=columns,filters=filters)
    roomCode = c.fetchone()
    if roomCode:
        return roomCode[0]
    return None

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
            roomUserId integer,
            userId text not null,
            cards text,
            points integer,
            lastWon integer,
            PRIMARY KEY (roomId, userId)
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
        execute_sql('''CREATE TABLE gameStatus
            (
            roomId integer PRIMARY KEY,
            roomState text,
            player1 integer,
            player2 integer,
            player3 integer,
            player4 integer
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
    c = execute_sql("INSERT INTO users VALUES ('a','ashwathhegde.66@gmail.com','pbkdf2:sha256:150000$FmVyGKiv$245a018c5d15eda5bd6bc789d6c17ee7ed035c9bc7cc3e199d6d67ee2114068a')")
    c = execute_sql("INSERT INTO users VALUES ('b','8ash0hegde@gmail.com','pbkdf2:sha256:150000$0wFtn6lF$73be1fa2a642425081c8f9f75e59f73fa47ec14ab00b73a7d0998afedca1dac3')")
    c = execute_sql("INSERT INTO tempUsers VALUES ('ashwath','ashwaheg@abc.def','1111111111','aaaaaaaaaaaaaaaaaaaaa')")
    c = execute_sql("INSERT INTO roomInfo(roomState,roomCode,host) VALUES ('Y','12345','ashwath')")
    #c = execute_sql("INSERT INTO roomStatus(userId,roomUserId,cards,points,lastWon) VALUES ('ashwath','1','A1,b2','1','0')")

if __name__ == "__main__":
    init_db()
