


import requests

#这里fetch_and_decode 会return (item_set),list里面的每个元素都是list,刚好用于存放在mysql里面
def fetch_and_decode(): 
    response = requests.get('http://api.biyingapi.com/hszg/list/4C3FDEA4-A4E5-4111-BF73-ED0AB2F3043B')
    response.raise_for_status()
    data = response.json()
    item_set = []
    for item in data:
        if '热门' in item['name'] and 'A股-热门概念' != item['name'] and "香港股市-热门港股" != item["name"] and "外汇-热门汇率" != item["name"]:
            item_set.append([item['name'][8:]])
        
    # print(item_set)
    return item_set

# print(fetch_and_decode())
if __name__ == "__main__":  # 确保在主程序中执行
    
    data = fetch_and_decode()
    print(data)



