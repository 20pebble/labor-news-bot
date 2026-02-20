import requests
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

NAVER_EMAIL = "20pebble@naver.com"
NAVER_PASSWORD = os.getenv("NAVER_APP_PASSWORD")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

KEYWORDS = [
    "보건의료노조",
    "병원 노사",
    "단체교섭",
    "노란봉투법",
    "노동위원회",
    "의료 파업"
]

def get_news():
    query = " OR ".join(KEYWORDS)
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    res = requests.get(url)
    return res.text[:6000]

def summarize(news):
    import requests
    import os

    api_key = os.environ["OPENAI_API_KEY"]

    prompt = f"""
    아래 최근 노동계 동향 뉴스를
    노사관계, 정책, 파업, 노조 중심으로
    핵심만 간결하게 5줄 요약해줘.
    
    뉴스:
    {news}
    """

    r = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4.1-mini",
            "input": prompt
        },
        timeout=60
    )

    data = r.json()
    print(data)  # 디버깅용 로그

    try:
        return data["output"][0]["content"][0]["text"]
    except Exception:
        return f"요약 실패 / API 응답:\n{data}"

def send_email(content):
    today = datetime.datetime.now().strftime("%Y.%m.%d")
    subject = f"[일일 노동계 동향 브리핑] {today} (보건의료·단체교섭)"

    msg = MIMEMultipart()
    msg["From"] = NAVER_EMAIL
    msg["To"] = NAVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(content, "plain"))

    server = smtplib.SMTP("smtp.naver.com", 587)
    server.starttls()
    server.login(NAVER_EMAIL, NAVER_PASSWORD)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    news = get_news()
    summary = summarize(news)
    send_email(summary)
