import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px

# =========================
# СТИЛЬ
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0a0f1c;
    color: white;
}
.card {
    background: #11182b;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
}
.avg { color: #00f7ff; }
.good { color: #00ff88; }
.bad { color: #ff4d6d; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ ELJUR ANALYTICS (LIGHT VERSION)")

# =========================
# ЛОГИН
# =========================
def login(session, url, login, password):
    try:
        # Получаем страницу логина (для cookies)
        session.get(url)

        payload = {
            "login": login,
            "password": password
        }

        response = session.post(url, data=payload)

        return response.status_code == 200
    except:
        return False

# =========================
# ПАРСИНГ
# =========================
def parse_grades(session, url):
    data = {}

    try:
        page = session.get(url)
        soup = BeautifulSoup(page.text, "lxml")

        subjects = soup.select(".subject")  # ⚠️ менять!

        for sub in subjects:
            name = sub.text.strip()
            grades = [int(g.text) for g in sub.select(".grade") if g.text.isdigit()]
            data[name] = grades

    except:
        pass

    return data

# =========================
# АНАЛИЗ
# =========================
def analyze(data):
    result = {}

    for subject, grades in data.items():
        if not grades:
            continue

        avg = sum(grades) / len(grades)

        result[subject] = {
            "grades": grades,
            "avg": round(avg, 2),
            "good": [g for g in grades if g >= 4],
            "bad": [g for g in grades if g <= 3]
        }

    return result

# =========================
# ЦЕЛИ
# =========================
def calc_goal(grades, target):
    total = sum(grades)
    count = len(grades)

    n = 0
    while True:
        if (total + 5*n)/(count+n) >= target:
            return n
        n += 1

# =========================
# UI
# =========================
url = st.text_input("🌐 URL ЭлЖура")
login_user = st.text_input("👤 Логин")
password = st.text_input("🔒 Пароль", type="password")

if st.button("🚀 Запустить"):
    session = requests.Session()

    if not login(session, url, login_user, password):
        st.error("Ошибка входа")
        st.stop()

    data = parse_grades(session, url)

    if not data:
        st.error("Не удалось получить оценки (измени селекторы)")
        st.stop()

    result = analyze(data)

    st.success("Данные загружены")

    targets = {}
    for subject in result:
        targets[subject] = st.number_input(
            f"Цель для {subject}",
            2.0, 5.0, 4.0
        )

    for subject, info in result.items():
        needed = calc_goal(info["grades"], targets[subject])

        st.markdown(f"""
        <div class="card">
            <h3>{subject}</h3>
            <p>Оценки: {info['grades']}</p>
            <p class="avg">Средний: {info['avg']}</p>
            <p class="good">Хорошие: {info['good']}</p>
            <p class="bad">Плохие: {info['bad']}</p>
            <p>🎯 Нужно пятёрок: {needed}</p>
        </div>
        """, unsafe_allow_html=True)

    # график
    df = pd.DataFrame([
        {"Subject": k, "Average": v["avg"]}
        for k, v in result.items()
    ])

    fig = px.bar(df, x="Subject", y="Average")
    st.plotly_chart(fig)

    # Excel
    st.download_button(
        "💾 Скачать CSV",
        df.to_csv(index=False),
        file_name="grades.csv"
    )