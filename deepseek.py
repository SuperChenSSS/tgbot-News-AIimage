import os
from openai import OpenAI


def DS(data,section):
    if isinstance(data,list):#将list转换成string
        data_temp = ''
        for i in data:
            data_temp = data_temp + '||' + i
        data = data_temp
        
    
    if isinstance(section,list):#将list转换成string
        
        section_temp = ''
        for i in section:
            for w in i:
                section_temp = section_temp + '||' + w
        section = section_temp
        
    # 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
    # 初始化Openai客户端，从环境变量中读取您的API Key
    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",# 此为默认路径，您可根据业务所在地域进行配置
        api_key=os.environ.get("ARK_API_KEY"),# 从环境变量中获取您的 API Key
    )

    # Non-streaming:
    print("----- standard request -----")
    completion = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model="doubao-1-5-pro-32k-250115",
        messages=[
            {"role": "system", "content": "你是证券帮手，你要帮我根据当前时事新闻帮我把最有可能上涨的热门板块进行分析"},
            {"role": "user", "content": data},
            {"role": "user", "content": section},],)

    return(completion.choices[0].message.content)
