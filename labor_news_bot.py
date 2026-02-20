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
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    today = datetime.datetime.now()
    weekday = today.weekday()

    if weekday == 0:
        date_info = "주말 포함 최근 노동계 동향"
    else:
        date_info = "최근 1일 노동계 동향"

    prompt = f"""
    아래 뉴스 데이터를 기반으로 병원/보건의료 노동계 중심으로
    업무 브리핑 형식으로 요약해줘.

    형식:
    1. 보건의료노조 동향
    2. 병원 단체교섭/노사관계
    3. 노란봉투법 및 정책
    4. 주요 노동 분쟁 이슈
    5. 시사점 (임원 보고용 3줄, 매우 중요)

    뉴스:
    {news}
    """

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )

    result = r.json()

    # 🔥 에러 방지 안전 처리
    if "content" not in result:
        return f"요약 생성 실패 (API 응답): {result}"

    return result["content"][0]["text"]

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
