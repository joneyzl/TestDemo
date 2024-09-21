# import json
# from datetime import datetime
# from collections import defaultdict

# # 读取 JSON 数据
# with open('D://Contest//华为云//购物小助手//shopping_data.json', 'r', encoding='utf-8') as f:
#     shopping_data = json.load(f)

# # 获取当前时间
# current_date = datetime.now()

# # 初始化字典来存储商品类别的购买次数和时间差
# category_data = defaultdict(lambda: {'total_count': 0, 'total_time_diff': 0, 'items': 0})

# # 计算每个商品类别的购买次数和距离现在的时间差
# for item in shopping_data:
#     product_date = datetime.strptime(item['购买日期'], "%Y-%m-%d")
#     time_diff = (current_date - product_date).days
#     category = item['商品类别']

#     category_data[category]['total_count'] += 1
#     category_data[category]['total_time_diff'] += time_diff
#     category_data[category]['items'] += 1

# # 计算每个商品类别被杀熟的概率
# # 假设概率与购买次数正相关，与购买时间差的反比相关
# category_kill_risk = {}
# for category, data in category_data.items():
#     avg_time_diff = data['total_time_diff'] / data['items']
#     # 定义杀熟概率为购买次数/平均时间差的倒数
#     kill_risk = data['total_count'] / (avg_time_diff + 1)
#     category_kill_risk[category] = kill_risk

# # 打印每类商品的杀熟概率
# for category, probability in category_kill_risk.items():
#     print(f"商品类别: {category}, 被杀熟的概率: {probability:.2f}")


import json
from datetime import datetime
from collections import defaultdict

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
    # 可以继续添加其他产品到类别的映射
}

# Step 1: 读取购物数据并计算商品类别的购买次数、杀熟概率和近期购买次数
with open('D://Contest//华为云//购物小助手//shopping_data.json', 'r', encoding='utf-8') as f:
    shopping_data = json.load(f)

# 获取当前时间
current_date = datetime.now()
# 定义“近期”的天数，比如最近60天
recent_days_threshold = 60

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
    # 定义杀熟概率为购买次数/平均时间差的倒数
    kill_risk = data['total_count'] / (avg_time_diff + 1)
    category_kill_risk[category] = kill_risk

# Step 2: 根据用户输入的商品名称输出对应的分类信息
def output_category_info(product_name):
    # 查找商品名称对应的类别
    if product_name in product_to_category:
        category = product_to_category[product_name]
        
        if category in category_data:
            data = category_data[category]
            total_count = data['total_count']
            recent_count = data['recent_count']
            kill_risk = category_kill_risk[category]
            
            # 输出该类商品的购买信息
            print(f"商品类别: {category}, 总购买次数: {total_count}, 近期购买次数: {recent_count}, 被杀熟的概率: {kill_risk:.2f}")
        else:
            print(f"未找到类别: {category} 的购买数据")
    else:
        print(f"未找到产品: {product_name} 的分类信息")

# Step 3: 用户输入想要购买的商品名称
user_input_product = input("请输入您想要购买的产品名称: ")

# 调用函数输出该产品对应类别的信息
output_category_info(user_input_product)
