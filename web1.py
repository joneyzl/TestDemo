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
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 商品名称与类别映射
with open('D://Contest//华为云//购物小助手//product_to_category.json', 'r', encoding='utf-8') as f:
    product_to_category = json.load(f)

# 加载购物数据，计算购买统计信息
with open('D://Contest//华为云//购物小助手//shopping_data.json', 'r', encoding='utf-8') as f:
    shopping_data = json.load(f)

current_date = datetime.now()
recent_days_threshold = 100

# 初始化类别购买统计字典
category_data = defaultdict(lambda: {'total_count': 0, 'total_time_diff': 0, 'recent_count': 0, 'items': 0})

# 计算每个类别的统计信息
for item in shopping_data:
    product_date = datetime.strptime(item['购买日期'], "%Y-%m-%d")
    time_diff = (current_date - product_date).days
    category = item['商品类别']

    category_data[category]['total_count'] += 1
    category_data[category]['total_time_diff'] += time_diff
    category_data[category]['items'] += 1

    if time_diff <= recent_days_threshold:
        category_data[category]['recent_count'] += 1

# 计算类别的杀熟风险
category_kill_risk = {}
for category, data in category_data.items():
    avg_time_diff = data['total_time_diff'] / data['items']
    kill_risk = data['total_count'] / (avg_time_diff + 1)
    category_kill_risk[category] = kill_risk

# WebSocket参数类
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
        
        # 调用回调并拼接内容，确保内容为完整一段
        if not hasattr(ws, "complete_message"):
            ws.complete_message = ""
        
        ws.complete_message += content.strip()  # 累积消息，去除每个内容的多余换行
        if ws.complete_message.endswith("。"):  # 根据标点符号判断消息是否完整结束
            ws.response_callback(ws.complete_message)  # 返回完整消息


def on_open(ws):
    thread.start_new_thread(run, (ws,))

def run(ws):
    ws.send(ws.query)

# WebSocket主函数
def main(appid, api_secret, api_key, gpt_url, domain, query, response_callback):
    wsParam = Ws_Param(appid, api_key, api_secret, gpt_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()

    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_open=on_open)
    ws.appid = appid
    ws.complete_message = ""  # 初始化完整消息变量
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
    ws.response_callback = response_callback
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# 生成查询模型的query
def generate_query(product_type, example_item, example_problem):
    query_template = """
    背景说明：你作为一个智能购物助手，请根据购买者的商品名称 "{example_item}"，详细说明该商品可能遇到的常见问题，并给出相应的解决办法，内容大概包括两部分：1. 商品可能遇到的问题；2. 解决这些问题的建议。字数控制在200字左右。

    用户问题：
    我想买一个 {example_item}，但是 {example_problem}，我该怎么办？

    模型回复：
    1. 根据您选择的产品 "{example_item}"，常见问题可能包括：
    问题1: [描述具体问题]
    问题2: [描述具体问题]
    问题3: [描述具体问题]
    
    2. 针对上述问题，以下是一些建议：
    建议1: [提供针对问题1的解决方案]
    建议2: [提供针对问题2的解决方案]
    建议3: [提供针对问题3的解决方案]
    

    """
    return query_template.format(product_type=product_type, example_item=example_item, example_problem=example_problem)

# 输出类别信息
@app.route('/get_product_info', methods=['POST'])
def output_category_info():
    data = request.get_json()
    product_name = data.get("product_name")

    if product_name in product_to_category:
        category = product_to_category[product_name]

        if category in category_data:
            data = category_data[category]
            total_count = data['total_count']
            recent_count = data['recent_count']
            kill_risk = category_kill_risk[category]

            response = {
                "category": category,
                "total_count": total_count,
                "recent_count": recent_count,
                "kill_risk": f"{kill_risk:.2f}",
                "model_response": ""  # 模型的完整响应占位符
            }

            query = generate_query(
                product_type=category,
                example_item=product_name,
                example_problem="质量问题和售后服务"
            )

            def response_callback(content):
                response["model_response"] = content  # 更新模型响应
                print(content)

            main(
                appid="060a6068",
                api_secret="NGZmZGQ2MTE3YzFkOWEzMzQxNzdhNmZj",
                api_key="29ef4f525b229c060cd059f3b13bd023",
                gpt_url="wss://spark-api.xf-yun.com/v4.0/chat",
                domain="4.0Ultra",
                query=query,
                response_callback=response_callback
            )

            return jsonify(response)
        else:
            return jsonify({"error": f"未找到类别: {category} 的购买数据"})
    else:
        return jsonify({"error": f"未找到产品: {product_name} 的分类信息"})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
