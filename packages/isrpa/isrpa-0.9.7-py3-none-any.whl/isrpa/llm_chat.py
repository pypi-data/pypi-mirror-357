from volcenginesdkarkruntime import Ark
#暂不统计消耗的token，后续要统计再改，无法传递token没法用dify的大模型，先保证这个功能能用起来

def ai_talk(input_str):
    """使用方舟SDK调用大模型API"""
    try:
        # 初始化客户端
        client = Ark(api_key="f0f8b460-c4ea-42a4-a951-5e2e454022ee")

        # 调用聊天补全API
        completion = client.chat.completions.create(
            model="deepseek-v3-250324",
            messages=[
                {"role": "user", "content": input_str}
            ],
            max_tokens=512,  # 最大生成token数
            temperature=0.5  # 温度参数
        )

        # 返回AI生成的内容
        return completion.choices[0].message.content

    except Exception as e:
        return f"ai_talk调用时出错: {str(e)}"