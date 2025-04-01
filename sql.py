import mysql.connector
from biying import fetch_and_decode

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="x8x8x888",
    database="cloud"
)

#用于清空table
def delete_database(table_name):
    mycursor = mydb.cursor()# 创建游标对象，用于执行 SQL 语句
    delete_query = f"DELETE FROM {table_name}"
    mycursor.execute(delete_query)# 执行删除操作
    mydb.commit()# 提交事务，使删除操作生效
    print("delete success")

#用于将数据插入mysql,这里的data需要是一个list，里面的内容也是list
def insert_data(table_name,data):
    mycursor = mydb.cursor()# 创建游标对象，用于执行 SQL 语句
    # eg : data_list = [[1],[2],[3]]  # 定义要插入的多条数据,这里的数据必须是list，然后多个数据的话需要用list组装
    insert_query = "INSERT INTO " + table_name + " (hot_concept_name) VALUES (%s)"
    print
    mycursor.executemany(insert_query, data)# 批量执行插入操作
    mydb.commit()# 提交事务，使插入操作生效
    print(mycursor.rowcount, "条记录插入成功。")

#获得sql的版块名称，这里获得的格式是list[tuple]
def get_data(table_name):
    mycursor = mydb.cursor()
    select_query = f"SELECT hot_concept_name FROM {table_name}"# 构建查询表中所有数据的 SQL 语句
    mycursor.execute(select_query)# 执行查询操作
    results = mycursor.fetchall()# 获取查询结果
    return results
