import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px

# =========================
# UI СТИЛЬ
# =========================
st.set_page_config(page_title="ELJUR Analytics", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0a0f1c, #0f172a);
    color: white;
}
.card {
    background: #11182b;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0 0 15px rgba(0,255,255,0.15);
}
.avg { color: #00f7ff; font-weight: bold; }
.good { color: #00ff88; }
.bad { color: #ff4d6d; }
.title {
    text-align: center;
    font-size: 36px;
    color: #00f7ff;
    text-shadow: 0 0 10px #00f7ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">⚡ ELJUR ANALYTICS ⚡</div>', unsafe_allow_html=True)

# =========================
# ФУНКЦИИ
# =========================
def login(session, url, login, password):
    try:
        session.get(url)

        payload = {
            "login": login,
            "password": password
        }

        r = session.post(url, data=payload)

        return r.status_code == 200
    except:
        return False

def parse_grades(session, url):
    data = {}

    try:
        page = session.get(url)
        soup = BeautifulSoup(page.text, "lxml")

        # ⚠️ ОБЯЗАТЕЛЬНО поменять под ЭлЖур
        subjects = soup.select(".subject")

        for sub in subjects:
            name = sub.text.strip()

            grades = [
                int(g.text)
                for g in sub.select(".grade")
                if g.text.isdigit()
            ]

            data[name] = grades

    except:
        pass

    return data

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

def calc_goal(grades, target):
    total = sum(grades)
    count = len(grades)

    n = 0
    while True:
        if (total + 5*n)/(count+n) >= target:
            return n
        n += 1

# =========================
# UI ВВОД
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    url = st.text_input("🌐 URL ЭлЖура")

with col2:
    login_user = st.text_input("👤 Логин")

with col3:
    password = st.text_input("🔒 Пароль", type="password")

# =========================
# ЗАПУСК
# =========================
if st.button("🚀 Запустить анализ"):

    with st.spinner("Подключение..."):
        session = requests.Session()

        if not login(session, url, login_user, password):
            st.error("❌ Ошибка входа")
            st.stop()

        data = parse_grades(session, url)

        if not data:
            st.error("❌ Не удалось получить оценки (нужно поменять селекторы)")
            st.stop()

        result = analyze(data)

    st.success("✅ Данные загружены")

    # =========================
    # ЦЕЛИ
    # =========================
    st.subheader("🎯 Цели")

    targets = {}
    for subject in result:
        targets[subject] = st.slider(
            f"{subject}",
            2.0, 5.0, 4.0, 0.1
        )

    # =========================
    # РЕЗУЛЬТАТЫ
    # =========================
    st.subheader("📊 Анализ")

    for subject, info in result.items():
        needed = calc_goal(info["grades"], targets[subject])

        st.markdown(f"""
        <div class="card">
            <h3>{subject}</h3>
            <p>📌 Оценки: {info['grades']}</p>
            <p class="avg">📊 Средний: {info['avg']}</p>
            <p class="good">✅ Хорошие: {info['good']}</p>
            <p class="bad">⚠️ Плохие: {info['bad']}</p>
            <p>🎯 Нужно пятёрок: {needed}</p>
        </div>
        """, unsafe_allow_html=True)

    # =========================# ГРАФИК
    # =========================
    df = pd.DataFrame([
        {"Предмет": k, "Средний балл": v["avg"]}
        for k, v in result.items()
    ])

    fig = px.bar(df, x="Предмет", y="Средний балл")
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # EXCEL
    # =========================
    st.download_button(
        "💾 Скачать CSV",
        df.to_csv(index=False),
        file_name="grades.csv"
    )