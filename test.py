# import openai
# import os

# from dotenv import load_dotenv,find_dotenv

# _=load_dotenv(find_dotenv())

# openai.api_key = os.getenv('sk-vZgSyK2bSTDxK8sbiCe9CKuuUBokjfgNmsfXzhqb5NVyL61V')

# def get_completion(prompt,model="gpt-3.5-turbo"):
#     message = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.creat(
#         model=model,
#         message=message,
#         temperature=0,
#     )
#     return response.choise[0].message["content"]

# text = f """"hello world"""

# prompt = f """hello world"""

# response = get_completion(prompt)
# print(prompt)

# 设置API密钥
# openai.api_key = 'sk-vZgSyK2bSTDxK8sbiCe9CKuuUBokjfgNmsfXzhqb5NVyL61V'

# # coding: utf-8
# import _thread as thread
# import os
# import time
# import base64
# import datetime
# import hashlib
# import hmac
# import json
# from urllib.parse import urlparse
# import ssl
# from datetime import datetime
# from time import mktime
# from urllib.parse import urlencode
# from wsgiref.handlers import format_date_time

# import websocket
# import openpyxl
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import os


# class Ws_Param(object):
#     # 初始化
#     def __init__(self, APPID, APIKey, APISecret, gpt_url):
#         self.APPID = APPID
#         self.APIKey = APIKey
#         self.APISecret = APISecret
#         self.host = urlparse(gpt_url).netloc
#         self.path = urlparse(gpt_url).path
#         self.gpt_url = gpt_url

#     # 生成url
#     def create_url(self):
#         # 生成RFC1123格式的时间戳
#         now = datetime.now()
#         date = format_date_time(mktime(now.timetuple()))

#         # 拼接字符串
#         signature_origin = "host: " + self.host + "\n"
#         signature_origin += "date: " + date + "\n"
#         signature_origin += "GET " + self.path + " HTTP/1.1"

#         # 进行hmac-sha256进行加密
#         signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
#                                  digestmod=hashlib.sha256).digest()

#         signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

#         authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

#         authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

#         # 将请求的鉴权参数组合为字典
#         v = {
#             "authorization": authorization,
#             "date": date,
#             "host": self.host
#         }
#         # 拼接鉴权参数，生成url
#         url = self.gpt_url + '?' + urlencode(v)
#         # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
#         return url


# # 收到websocket错误的处理
# def on_error(ws, error):
#     print("### error:", error)


# # 收到websocket关闭的处理
# def on_close(ws):
#     print("### closed ###")


# # 收到websocket连接建立的处理
# def on_open(ws):
#     thread.start_new_thread(run, (ws,))


# def run(ws, *args):
#     data = json.dumps(gen_params(appid=ws.appid, query=ws.query, domain=ws.domain))
#     ws.send(data)


# # 收到websocket消息的处理
# def on_message(ws, message):
#     # print(message)
#     data = json.loads(message)
#     code = data['header']['code']
#     if code != 0:
#         print(f'请求错误: {code}, {data}')
#         ws.close()
#     else:
#         choices = data["payload"]["choices"]
#         status = choices["status"]
#         content = choices["text"][0]["content"]
#         print(content,end='')
#         if status == 2:
#             print("#### 关闭会话")
#             ws.close()


# def gen_params(appid, query, domain):
#     """
#     通过appid和用户的提问来生成请参数
#     """

#     data = {
#         "header": {
#             "app_id": appid,
#             "uid": "1234",           
#             # "patch_id": []    #接入微调模型，对应服务发布后的resourceid          
#         },
#         "parameter": {
#             "chat": {
#                 "domain": domain,
#                 "temperature": 0.5,
#                 "max_tokens": 4096,
#                 "auditing": "default",
#             }
#         },
#         "payload": {
#             "message": {
#                 "text": [{"role": "user", "content": query}]
#             }
#         }
#     }
#     return data


# def main(appid, api_secret, api_key, gpt_url, domain, query):
#     wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
#     websocket.enableTrace(False)
#     wsUrl = wsParam.create_url()

#     ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
#     ws.appid = appid
#     ws.query = query
#     ws.domain = domain
#     ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# if __name__ == "__main__":
#     main(
#         appid="060a6068",
#         api_secret="NGZmZGQ2MTE3YzFkOWEzMzQxNzdhNmZj",
#         api_key="29ef4f525b229c060cd059f3b13bd023",
#         gpt_url="wss://spark-api.xf-yun.com/v4.0/chat",
#         domain="4.0Ultra",

#         query="给我写一篇100字的作文"
#     )



from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

#星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v4.0/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = '060a6068'
SPARKAI_API_SECRET = 'NGZmZGQ2MTE3YzFkOWEzMzQxNzdhNmZj'
SPARKAI_API_KEY = '29ef4f525b229c060cd059f3b13bd023'
#星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = '4.0Ultra'

if __name__ == '__main__':
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [ChatMessage(
        role="user",
        content='你好呀'
    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    print(a)