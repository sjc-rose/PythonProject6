import os
import requests
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ================= 配置区 (GitHub Actions 会自动填入这些环境变量) =================
# 这里的 getenv 会去寻找你在 GitHub Settings 里设置的 Secrets
NEWS_API_KEY = os.getenv("53374cc9663b416f873a41c8f5c40ead")
AI_API_KEY = os.getenv("sk-24e4d894e6a749e8a20a79ad95374e46")
MAIL_AUTH = os.getenv("wxyhwaikuajmeajj")  # 邮箱授权码

# 邮件基础信息（直接写你的即可）
SENDER_EMAIL = "2586753019@qq.com"
RECEIVER_EMAIL = "2586753019@qq.com"


# ===========================================================================

def fetch_and_analyze():
    # 抓取 100 条新闻
    topic = "AI 与 大数据"
    url = f"https://newsapi.org/v2/everything?q={topic}&pageSize=100&sortBy=relevancy&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])

        # 提取标题给 AI
        context = "\n".join([f"- {n['title']}" for n in articles[:100]])

        # AI 深度总结
        client = OpenAI(api_key=AI_API_KEY, base_url="https://api.deepseek.com")
        prompt = f"请根据以下100条最新新闻标题，整理一份深度行业分析简报：\n{context}"

        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"获取或分析失败: {e}"


def send_email(content):
    # 邮件发送逻辑
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = Header("今日 AI 智库自动分析报告", 'utf-8')

    try:
        # --- 这里是修改后的部分 ---
        # 改用 587 端口并启用 TLS 加密，这种方式在 GitHub Actions 环境下最稳定
        server = smtplib.SMTP("smtp.qq.com", 587)
        server.starttls()
        # -----------------------

        server.login(SENDER_EMAIL, MAIL_AUTH)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], message.as_string())
        server.quit()
        print("✅ 报告已成功发送至邮箱！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
    send_email(report)