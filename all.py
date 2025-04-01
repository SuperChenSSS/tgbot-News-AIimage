from biying import fetch_and_decode #这里是获得版块分类名，可存sql可不存sql
from sql import delete_database,insert_data,get_data  #这里是对sql操作的函数，用于添加，删除原数据，获得数据的
from get_news import hotpoint,everything #这里是获得新闻的两种方式，hotpoint只能获得当下热点，everything可以进行关键词筛选
from deepseek import DS  #全扔DS


print(DS(hotpoint(),fetch_and_decode()))
