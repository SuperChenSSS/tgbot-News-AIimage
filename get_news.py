# 这里是获得新闻的标题import requests
from openai import OpenAI
import requests

# 获取新闻并返回content， list,hotpoint model
def hotpoint():
    url = 'https://newsapi.org/v2/top-headlines?'+\
    'searchIn=content&'+\
    'sortBy=popularity&'+\
    'sources=bbc-news&'+\
    'apiKey=a24ff47e10d246e5a424965b53b31559'
    content_temp = requests.get(url).json()
    content = []
    for i in content_temp['articles']:
        content.append(i['title'])
    return content

# 获取新闻并返回content， list,everything model，里面要输入关键词
def everything(keyword=''):
    if keyword:
        url = 'https://newsapi.org/v2/everything?'+\
            'q='+keyword+'&'+\
            'searchIn=content&'+\
            'pagesize=20&'+\
            'sortBy=relevancy&'+\
            'apiKey=a24ff47e10d246e5a424965b53b31559'

        content_temp = requests.get(url).json()
        # print(content_temp)
        content = []
        for i in content_temp['articles']:
            content.append(i['title'])
        return content

    else:
        content = ['you have to input at least one keyword']
        return content

#这里是看document文档的，可以输入document1,document2,我自己用的
def see_document(document_name):
    for i in document_name:
        print(i)

document1 = ['model:everything',
'keyword:q=keyword',
'searchIn=title/description/content',
'sortBy=relevancy,popularity,publishedAt',
'language=ar,de,en,es,fr,he,it,nl,no,pt,ru,sv,ud,zh',
'from=2025-03-01&to=2025-03-22&/from=2025-03-01',
'country=us']

document2 = ['model=top-headlines',
'country=us or more',
'category=business,entertainment,general,health,science,sports,technology',
'keyword=q=keyword',
'pagesize=The number of results to return per page (request). 20 is the default, 100 is the maximum']

if __name__ == "__main__":
    pass
