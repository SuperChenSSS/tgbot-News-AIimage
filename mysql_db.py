import pymysql
from dotenv import load_dotenv
import os
import logging
from ChatGPT_HKBU import HKBU_ChatGPT

#load_dotenv(".terraform/secrets.txt")
DB_HOST = os.environ.get("HOST")
DB_PORT = int(os.environ.get("REDISPORT", 3306))
DB_USER = os.environ.get("USER_NAME")
DB_PASSWORD = os.environ.get("PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

def connect_sql():
    try:
        pool = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
        )
        return pool
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

def fetch_data(pool, query, args=None):
    try:
        with pool.cursor() as cursor:
            cursor.execute(query, args)
            result = cursor.fetchall()
            return result
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

def insert_db(table, connection, timestamp, command, filename):
    """
    向数据库中插入数据。

    参数:
        connection: pymysql 连接。
        timestamp (datetime): 时间戳。
        command (str): 命令。
        filename (str): 文件名。
    """
    query = f"INSERT INTO {table} VALUES (\"%s\", \"%s\", \"%s\");"
    args = (timestamp, command, filename)
    # print(query % args)

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, args)
            connection.commit()
            logging.info(f"Data inserted successfully: {table}, {timestamp}, {command}, {filename}")
    except Exception as e:
        connection.rollback()
        logging.error(f"Error inserting data: {e}")

def close_db(connection):
    if connection:
        connection.close()

def gpt_summary(connection, table, number, model):
    chatgpt = HKBU_ChatGPT()
    if not connection:
        logging.error("Failed to create MySQL connection. Application may not function correctly.")
        return
    try:
        query = f"SELECT * FROM {table} ORDER BY timestamp DESC limit {number};"
        data = fetch_data(connection, query)
        prompt = f"Below are data stored from the database in JSON format, with table column (timestamp, command, filename):\n{data}\n Please summarize the commands and ignore other columns into sentences."
        #print(prompt + model)
        response = chatgpt.submit(prompt, model)
        return response
    except Exception as e:
        logging.error(f"Error summarizing data with {model}: {e}")
        return f"Error summarizing data: {e}"

def main():
    connection = connect_sql()
    if not connection:
        logging.error("Failed to create MySQL connection. Application may not function correctly.")
        return

    try:
        table = "ai_image"
        # timestamp = "2021-09-01 12:00:00"
        # command = "ls -l"
        # filename = "example.txt"
        # insert_db(table, connection, timestamp, command, filename)

        # # 示例查询
        # query = f"SELECT * FROM {table}"
        # data = fetch_data(connection, query)
        # print(data)
        response = gpt_summary(connection, table, 5, model="chatgpt")
        print(response)

    except Exception as e:
        logging.error(f"Error in main: {e}")

    finally:
        close_db(connection)

if __name__ == "__main__":
    main()