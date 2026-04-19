import os
import requests
import json
from openai import OpenAI

# ==================== 配置区 ====================
# 环境变量读取逻辑：
# 在 GitHub Actions 运行时会读取 Secrets；本地运行如果没有 Secrets，则使用默认值
NEWS_API_KEY = os.getenv("NEWS_KEY") or "53374cc9663b416f873a41c8f5c40ead"
AI_API_KEY = os.getenv("AI_KEY") or "sk-24e4d894e6a749e8a20a79ad95374e46"

# 你的飞书机器人地址
FEISHU_WEBHOOK = os.getenv(
    "FEISHU_WEBHOOK") or "https://open.feishu.cn/open-apis/bot/v2/hook/fa1e64a2-a57e-48ac-9a58-8f0747ff2033"


# ===============================================

def fetch_and_analyze():
    print("第一步：正在抓取最新 AI 新闻标题...")
    topic = "AI 与 大数据"
    url = f"https://newsapi.org/v2/everything?q={topic}&pageSize=100&sortBy=relevancy&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])
        # 提取前 100 条标题
        context = "\n".join([f"- {n['title']}" for n in articles[:100]])
        print(f"成功抓取到 {len(articles[:100])} 条标题，正在呼叫 DeepSeek 分析...")

        client = OpenAI(api_key=AI_API_KEY, base_url="https://api.deepseek.com")
        prompt = f"请根据以下最新新闻标题，整理一份深度行业分析简报，包含趋势总结和关键动态：\n{context}"

        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"获取或分析失败: {e}"


def send_to_feishu(content):
    print("第二步：正在将报告推送到飞书机器人...")

    # 构造飞书消息体
    payload = {
        "msg_type": "text",
        "content": {
            "text": f"📊 今日 AI 行业深度分析报告\n----------------------------\n{content}"
        }
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(FEISHU_WEBHOOK, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print("✅ 报告已成功推送到飞书群！")
        else:
            print(f"❌ 飞书推送失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"❌ 飞书连接异常：{e}")


# ==================== 启动 ====================
if __name__ == "__main__":
    report_result = fetch_and_analyze()
    send_to_feishu(report_result)