import requests
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

NAVER_EMAIL = "20pebble@naver.com"
NAVER_PASSWORD = os.getenv("NAVER_APP_PASSWORD")


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

def summarize(news_list):
    if not news_list:
        return "오늘 주요 노동계 뉴스가 없습니다."

    summary = "[오늘의 노동계 주요 동향 요약]\n\n"

    for i, news in enumerate(news_list[:5], 1):
        title = news.get("title", "").replace("<b>", "").replace("</b>", "")
        link = news.get("link", "")
        summary += f"{i}. {title}\n- 기사링크: {link}\n\n"

    summary += "※ 자동 수집된 최신 노동계 뉴스 요약입니다."
    return summary

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
