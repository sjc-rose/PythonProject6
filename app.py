import streamlit as st
import requests
from openai import OpenAI

# ================= 配置区 =================
# 请填入你申请到的 Key
NEWS_API_KEY = "53374cc9663b416f873a41c8f5c40ead"
AI_API_KEY = "sk-24e4d894e6a749e8a20a79ad95374e46"
AI_BASE_URL = "https://api.deepseek.com"  # 如果是 Gemini，请更换对应的 URL 和模型名
# ==========================================

client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)


# --- 1. 强化版抓取函数（支持分页获取更多内容） ---
def fetch_massive_news(query):
    all_articles = []
    # 尝试抓取前 2 页，每页 100 条，总计上限 200 条
    for page in [1, 2]:
        url = f"https://newsapi.org/v2/everything?q={query}&pageSize=100&page={page}&sortBy=relevancy&apiKey={NEWS_API_KEY}"
        try:
            response = requests.get(url, timeout=15)
            data = response.json()
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                all_articles.extend(articles)
                # 如果第一页就没满 100 条，说明后面没新闻了，直接跳出
                if len(articles) < 100:
                    break
            else:
                st.error(f"NewsAPI 报错: {data.get('message')}")
                break
        except Exception as e:
            st.warning(f"第 {page} 页抓取异常: {e}")
            break
    return all_articles


# --- 2. 深度分析函数 ---
def generate_deep_report(news_list, topic):
    # 如果新闻太多，AI 的上下文窗口有限。我们提取前 100-150 条的标题和描述
    # 这样既保证了信息量，又不会导致请求失败
    context_items = []
    for i, n in enumerate(news_list[:150]):
        title = n.get('title', '无标题')
        desc = n.get('description', '无描述')
        context_items.append(f"[{i + 1}] {title}: {desc}")

    context_text = "\n".join(context_items)

    prompt = f"""
    你是一位拥有 20 年经验的资深行业分析师。
    我现在为你提供了关于“{topic}”的 {len(news_list)} 条最新原始情报。

    请完成以下深度的【情报分析报告】：

    1. **核心态势感知**：用专业语言概括当前该领域的整体发展阶段与舆论氛围。
    2. **关键趋势提取 (Top 5)**：从海量信息中识别出最具有影响力的 5 个趋势，并结合新闻内容进行深度解析。
    3. **关联性分析**：分析这些新闻之间是否存在某种潜在的联系（例如：政策导向、巨头布局等）。
    4. **风险与机遇研判**：基于现有情报，为相关从业者或投资者给出 3 条具操作性的建议。
    5. **情报源统计**：简述这些新闻的主要来源分布。

    注意：请保持行文专业、客观、辛辣。

    以下为情报原文：
    {context_text}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个精通大数据分析的 AI 智库专家。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,  # 调高输出上限，确保报告完整
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 总结出错啦: {str(e)}"


# --- 3. Streamlit UI 界面 ---
st.set_page_config(page_title="AI 智库情报站", layout="wide")

# 美化 UI
st.title("🛡️ AI 行业智库 - 自动化情报收集系统")
st.markdown(f"当前模式：**深度分析模式 (200条量级)**")

with st.sidebar:
    st.header("控制台")
    search_topic = st.text_input("输入追踪关键词", value="以太坊 2.0")
    st.info("提示：抓取 200 条新闻可能需要约 10-20 秒，请耐心等待。")
    start_btn = st.button("开始全量情报分析")

if start_btn:
    if not NEWS_API_KEY or "你的" in NEWS_API_KEY:
        st.error("❌ 还没填 NewsAPI Key 呢！")
    else:
        # 第一步：抓取
        with st.status("正在调取全球情报源...", expanded=True) as status:
            raw_news = fetch_massive_news(search_topic)
            st.write(f"✅ 已成功抓取到 {len(raw_news)} 条原始新闻。")

            # 第二步：总结
            st.write("🤖 AI 正在对海量数据进行语义对齐与趋势建模...")
            if raw_news:
                final_report = generate_deep_report(raw_news, search_topic)
                status.update(label="情报分析完成！", state="complete", expanded=False)

                # 展示报告
                st.success(f"### 📊 关于 “{search_topic}” 的深度分析报告")
                st.markdown("---")
                st.markdown(final_report)

                # 底部附录
                with st.expander("查看原始情报列表 (前 50 条)"):
                    for art in raw_news[:50]:
                        st.write(f"- **{art['title']}**")
                        st.caption(f"来源: {art['source']['name']} | [点击阅读原文]({art['url']})")
            else:
                st.error("未能获取到足够的情报，请尝试更换更通用的关键词。")