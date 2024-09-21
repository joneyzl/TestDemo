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
        print("请求错误，代码:", code)
        ws.close()
    else:
        choices = data["payload"]["choices"]
        content = choices["text"][0]["content"]
        print(content, end='')

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
    背景说明：你作为一个智能购物助手，请根据购买者的商品名称 " {example_item}" 具体说明可能出现的商品问题，并给出建议，200字左右

    我想买一个 {example_item}，但是 {example_problem}，我该怎么办？
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
            
            # 输出该类商品的购买信息
            print(f"商品类别: {category}")
            print(f"总购买次数: {total_count}")
            print(f"近期购买次数: {recent_count}")
            print(f"杀熟概率: {kill_risk:.2f}")
            
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
            print(f"未找到类别: {category} 的购买数据")
    else:
        print(f"未找到产品: {product_name} 的分类信息")

# Step 4: 用户输入想要购买的产品名称
user_input_product = input("请输入您想要购买的产品名称: ")

# 调用函数输出该产品对应类别的信息
output_category_info(user_input_product)
