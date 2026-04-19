import os
import requests
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 修改配置区，使用这种“二选一”写法
# 它会优先找 GitHub 的秘密变量，找不到（比如在本地）就用你写的这个字符串
NEWS_API_KEY = os.getenv("NEWS_KEY") or "53374cc9663b416f873a41c8f5c40ead"
AI_API_KEY = os.getenv("AI_KEY") or "sk-24e4d894e6a749e8a20a79ad95374e46"
MAIL_AUTH = os.getenv("MAIL_AUTH") or "wxyhwaikuajmeajj"

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

# 确保这两行在文件的最底部，且前面没有空格
if __name__ == "__main__":
    fetch_and_analyze()