import os
import requests
import json
from openai import OpenAI

# ==================== 配置区 ====================
# 优先从环境变量读取，如果没有则使用本地默认值（方便调试）
NEWS_API_KEY = os.getenv("NEWS_KEY") or "53374cc9663b416f873a41c8f5c40ead"
AI_API_KEY = os.getenv("AI_KEY") or "sk-24e4d894e6a749e8a20a79ad95374e46"
FEISHU_WEBHOOK = os.getenv(
    "FEISHU_WEBHOOK") or "https://open.feishu.cn/open-apis/bot/v2/hook/fa1e64a2-a57e-48ac-9a58-8f0747ff2033"


# ===============================================

def fetch_and_analyze():
    print("第一步：正在从 NewsAPI 抓取 AI 行业新闻...")
    topic = "AI 与 大数据"
    url = f"https://newsapi.org/v2/everything?q={topic}&pageSize=100&sortBy=relevancy&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])
        if not articles:
            return "未能抓取到今日相关新闻。"

        # 整理前 100 条新闻标题
        context = "\n".join([f"- {n['title']}" for n in articles[:100]])
        print(f"成功获取 {len(articles[:100])} 条标题，正在由 AI 进行深度分析...")

        # 调用 DeepSeek API
        client = OpenAI(api_key=AI_API_KEY, base_url="https://api.deepseek.com")
        prompt = f"你是一个专业的 AI 行业分析师。请根据以下最新的新闻标题，整理一份深度行业分析简报，包括：\n1. 核心趋势总结\n2. 重点动态梳理\n3. 简短的行业点评\n内容请使用中文。\n\n新闻数据：\n{context}"

        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"自动化流程出错: {e}"


def send_to_feishu(content):
    print("第二步：正在通过 Webhook 推送到飞书...")

    # 构建飞书消息格式
    payload = {
        "msg_type": "text",
        "content": {
            "text": f"📊 今日 AI 行业深度简报 (自动推送)\n----------------------------\n{content}"
        }
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(FEISHU_WEBHOOK, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print("✅ 飞书推送成功！")
        else:
            print(f"❌ 飞书推送失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"❌ 网络连接异常：{e}")


if __name__ == "__main__":
    report = fetch_and_analyze()
    send_to_feishu(report)