import os
import requests
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ==================== 配置区 ====================
NEWS_API_KEY = "53374cc9663b416f873a41c8f5c40ead"
AI_API_KEY = "sk-24e4d894e6a749e8a20a79ad95374e46"

# 强制使用你新给的 QQ 邮箱授权码
SENDER_EMAIL = "2586753019@qq.com"
RECEIVER_EMAIL = "2586753019@qq.com"
MAIL_AUTH = "zkanwqrhsqpoeaib"
# ===============================================

def fetch_and_analyze():
    print("第一步：开始抓取最新新闻...")
    topic = "AI 与 大数据"
    url = f"https://newsapi.org/v2/everything?q={topic}&pageSize=100&sortBy=relevancy&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])
        context = "\n".join([f"- {n['title']}" for n in articles[:100]])
        print(f"成功抓取到 {len(articles[:100])} 条标题，正在呼叫 AI 分析...")

        client = OpenAI(api_key=AI_API_KEY, base_url="https://api.deepseek.com")
        prompt = f"请根据以下最新新闻标题，整理一份深度行业分析简报：\n{context}"

        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"获取或分析失败: {e}"

def send_email(content):
    print("第二步：正在尝试发送邮件...")
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = Header("今日 AI 智库自动分析报告", 'utf-8')

    try:
        # QQ 邮箱在服务器上使用 587 端口最稳定
        server = smtplib.SMTP("smtp.qq.com", 587)
        server.starttls()  # 必须加上这一行
        server.login(SENDER_EMAIL, MAIL_AUTH)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], message.as_string())
        server.quit()
        print("✅ 报告已成功发送至 QQ 邮箱！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

if __name__ == "__main__":
    report_result = fetch_and_analyze()
    send_email(report_result)