from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

# 星火认知大模型Spark Max的URL值
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v4.0/chat'
# 星火认知大模型调用秘钥信息
SPARKAI_APP_ID = '060a6068'
SPARKAI_API_SECRET = 'NGZmZGQ2MTE3YzFkOWEzMzQxNzdhNmZj'
SPARKAI_API_KEY = '29ef4f525b229c060cd059f3b13bd023'
# 星火认知大模型Spark Max的domain值
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
    
    # 生成对话响应
    response = spark.generate([messages], callbacks=[handler])
    
    # 提取并打印生成的文本内容
    for generation in response['generations']:
        print(generation['text'])

