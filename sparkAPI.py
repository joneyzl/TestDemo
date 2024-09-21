# # coding: utf-8
# import _thread as thread
# import time
# import base64

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
#                 "text": [
#                     {
#                         "role": "user",
#                          "content": query
#                         # "content": "根据购买者商品说明可能出现的商品问题，并给出建议"
#                     }
#                         ]
#             }
#         }
#     }
#     return data

# # def main(appid, api_secret, api_key, gpt_url, domain, query):
# #     wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
# #     websocket.enableTrace(False)
# #     wsUrl = wsParam.create_url()

# #     ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
# #     ws.appid = appid
# #     ws.query = query
# #     ws.domain = domain
# #     ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# # if __name__ == "__main__":
# #     main(
# #         appid="060a6068",
# #         api_secret="NGZmZGQ2MTE3YzFkOWEzMzQxNzdhNmZj",
# #         api_key="29ef4f525b229c060cd059f3b13bd023",
# #         gpt_url="wss://spark-api.xf-yun.com/v4.0/chat",
# #         domain="4.0Ultra",

# #         query= f"""
# # 背景说明：你作为一个智能购物助手，请根据购买者的商品种类具体说明可能出现的商品问题，并给出建议，200字左右，以XML格式输出

# # 例如："user": "我买了一个手机，但是屏幕总是花屏，我该怎么办？"
# # "answer": "<xml>
# # <p>您好，手机屏幕花屏可能是由于屏幕老化、屏幕碎裂、屏幕进水等原因造成的。建议您先检查手机是否有进水，如果有，请及时处理。如果手机没有进水，建议您联系客服进行维修。</p>
# # </xml>"
# # """
# #     )

# # 生成提示词的函数
# def generate_query(product_type, example_item, example_problem, solution):
#     query_template = """
#     背景说明：你作为一个智能购物助手，请根据购买者的商品种类 "{product_type}" 具体说明可能出现的商品问题，并给出建议，200字左右，以XML格式输出

#     例如："user": "我买了一个 {example_item}，但是 {example_problem}，我该怎么办？"
#     "answer": "<xml>
#     <p>{solution}</p>
#     </xml>"
#     """
#     return query_template.format(product_type=product_type, example_item=example_item, example_problem=example_problem, solution=solution)


# # WebSocket连接主函数
# def main(appid, api_secret, api_key, gpt_url, domain, query):
#     wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
#     websocket.enableTrace(False)
#     wsUrl = wsParam.create_url()

#     ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
#     ws.appid = appid
#     ws.query = query
#     ws.domain = domain
#     ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# # 测试示例
# if __name__ == "__main__":
#     # 商品种类的示例输入
#     query = generate_query(
#         product_type="耳机",
#         example_item="手机",
#         example_problem="屏幕总是花屏",
#         solution="手机屏幕花屏可能是由于屏幕老化、屏幕碎裂、屏幕进水等原因造成的。建议您先检查手机是否有进水，如果有，请及时处理。如果手机没有进水，建议您联系客服进行维修。"
#     )

#     # 调用WebSocket主函数
#     main(
#         appid="060a6068",
#         api_secret="NGZmZGQ2MTE3YzFkOWEzMzQxNzdhNmZj",
#         api_key="29ef4f525b229c060cd059f3b13bd023",
#         gpt_url="wss://spark-api.xf-yun.com/v4.0/chat",
#         domain="4.0Ultra",
#         query=query
#     )


import json
import base64
import hashlib
import hmac
from urllib.parse import urlparse, urlencode
from wsgiref.handlers import format_date_time
from collections import defaultdict
import websocket
import ssl
from time import mktime
from datetime import datetime
import _thread as thread

# 产品名称到类别的映射
product_to_category = {
    '手机': '电子产品',
    '耳机': '电子产品',
    '笔记本': '电子产品',
    '电视': '家电',
    '洗衣机': '家电',
    '冰箱': '家电',
    '鞋子': '服装',
    '衬衫': '服装',
    '裤子': '服装',
}

# Step 1: 读取购物数据并计算商品类别的购买次数、杀熟概率和近期购买次数
with open('D://Contest//华为云//购物小助手//shopping_data.json', 'r', encoding='utf-8') as f:
    shopping_data = json.load(f)

# 获取当前时间
current_date = datetime.now()
# 定义“近期”的天数，比如最近100天
recent_days_threshold = 100

# 初始化字典来存储商品类别的购买次数、时间差和近期购买次数
category_data = defaultdict(lambda: {'total_count': 0, 'total_time_diff': 0, 'recent_count': 0, 'items': 0})

# 计算每个商品类别的购买次数和距离现在的时间差
for item in shopping_data:
    product_date = datetime.strptime(item['购买日期'], "%Y-%m-%d")
    time_diff = (current_date - product_date).days
    category = item['商品类别']

    category_data[category]['total_count'] += 1
    category_data[category]['total_time_diff'] += time_diff
    category_data[category]['items'] += 1

    # 如果购买时间在“近期”内，增加近期购买次数
    if time_diff <= recent_days_threshold:
        category_data[category]['recent_count'] += 1

# 计算每个商品类别被杀熟的概率
category_kill_risk = {}
for category, data in category_data.items():
    avg_time_diff = data['total_time_diff'] / data['items']
    kill_risk = data['total_count'] / (avg_time_diff + 1)
    category_kill_risk[category] = kill_risk

# Step 2: WebSocket参数类，负责生成请求的URL
class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {"authorization": authorization, "date": date, "host": self.host}
        return self.gpt_url + '?' + urlencode(v)

# WebSocket回调函数
def on_message(ws, message):
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'<error><code>{code}</code><message>请求错误</message></error>')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        content = choices["text"][0]["content"]
        print(f'<response>{content}</response>', end='')

# WebSocket连接函数
def on_open(ws):
    thread.start_new_thread(run, (ws,))

def run(ws, *args):
    ws.send(ws.query)

# WebSocket主函数
def main(appid, api_secret, api_key, gpt_url, domain, query):
    wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()

    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_open=on_open)
    ws.appid = appid
    ws.query = json.dumps({
        "header": {"app_id": appid},
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "max_tokens": 4096,
            }
        },
        "payload": {"message": {"text": [{"role": "user", "content": query}]} }
    })
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

# 生成查询模板
def generate_query(product_type, example_item, example_problem, solution):
    query_template = """
    背景说明：你作为一个智能购物助手，请根据购买者的商品名称 " {example_item}" 具体说明可能出现的商品问题，并给出建议，200字左右，以XML格式输出

    <user><query>我想买一个 {example_item}，但是 {example_problem}，我该怎么办？</query></user>
    <answer><p>{solution}</p></answer>
    """
    return query_template.format(product_type=product_type, example_item=example_item, example_problem=example_problem, solution=solution)

# Step 3: 根据用户输入的商品名称输出对应的分类信息
def output_category_info(product_name):
    if product_name in product_to_category:
        category = product_to_category[product_name]
        
        if category in category_data:
            data = category_data[category]
            total_count = data['total_count']
            recent_count = data['recent_count']
            kill_risk = category_kill_risk[category]
            
            # 输出该类商品的购买信息，以XML格式
            print(f"<category_info><category>{category}</category><total_count>{total_count}</total_count><recent_count>{recent_count}</recent_count><kill_risk>{kill_risk:.2f}</kill_risk></category_info>")
            
            # 调用 WebSocket，生成商品问题的解决方案
            query = generate_query(
                product_type=category,
                example_item=product_name,
                example_problem="质量问题和售后服务",  # 这里可以替换为实际问题描述
                solution="建议选择可靠品牌并查看售后政策，优先选择官方渠道购买。"  # 这里可以替换为实际解决方案
            )

            # WebSocket连接主函数
            main(
                appid="060a6068",
                api_secret="NGZmZGQ2MTE3YzFkOWEzMzQxNzdhNmZj",
                api_key="29ef4f525b229c060cd059f3b13bd023",
                gpt_url="wss://spark-api.xf-yun.com/v4.0/chat",
                domain="4.0Ultra",
                query=query
            )
        else:
            print(f"<error><message>未找到类别: {category} 的购买数据</message></error>")
    else:
        print(f"<error><message>未找到产品: {product_name} 的分类信息</message></error>")

# Step 4: 用户输入想要购买的产品名称
user_input_product = input("请输入您想要购买的产品名称: ")

# 调用函数输出该产品对应类别的信息
output_category_info(user_input_product)
