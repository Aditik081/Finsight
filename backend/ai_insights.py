import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(__file__), ".env"),
    override=True
)


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


def generate_news_insights(articles):

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY missing from .env")

    if not articles:
        return "No news articles available for analysis."

    # Prepare news data
    news_text = ""

    for article in articles[:15]:
        news_text += (
            f"\nHeadline: {article.get('headline', '')}\n"
            f"Summary: {article.get('summary', '')}\n"
            f"Sentiment: {article.get('sentiment', 'Unknown')}\n"
        )

    prompt = f"""
    You are a financial news analyst.

    Analyze the following company news:

    {news_text}

    Provide:
    1. A short overall news summary.
    2. Positive developments.
    3. Potential risks.
    4. Overall news sentiment.
    5. A balanced business outlook.

    Use only the information provided.
    Do not invent facts or predict guaranteed stock returns.
    Clearly mention when information is insufficient.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=700
    )

    return response.choices[0].message.content