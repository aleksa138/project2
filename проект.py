import streamlit as st
import pandas as pd
import plotly.express as px
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================
# СТИЛЬ (НЕОН)
# =========================
st.markdown("""
<style>
body {
    background-color: #0a0f1c;
}

.stApp {
    background-color: #0a0f1c;
    color: white;
}

.card {
    background: #11182b;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    box-shadow: 0 0 15px rgba(0,255,255,0.2);
}

.good { color: #00ff88; }
.bad { color: #ff4d6d; }
.avg { color: #00f7ff; font-weight: bold; }

.title {
    text-align: center;
    font-size: 32px;
    color: #00f7ff;
    text-shadow: 0 0 10px #00f7ff;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SELENIUM
# =========================
def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)

# =========================
# LOGIN
# =========================
def login_eljur(driver, url, login, password):
    driver.get(url)
    wait = WebDriverWait(driver, 20)

    try:
        login_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))
        password_input = driver.find_element(By.NAME, "password")

        login_input.send_keys(login)
        password_input.send_keys(password)
        password_input.submit()

        time.sleep(5)
        return True
    except:
        return False

# =========================
# PARSE (нужно адаптировать!)
# =========================
def parse_grades(driver):
    data = {}

    try:
        subjects = driver.find_elements(By.CLASS_NAME, "subject")

        for subject in subjects:
            name = subject.text
            grades_elements = subject.find_elements(By.CLASS_NAME, "grade")
            grades = [int(g.text) for g in grades_elements if g.text.isdigit()]
            data[name] = grades

    except:
        pass

    return data

# =========================
# ANALYZE
# =========================
def analyze(data):
    result = {}

    for subject, grades in data.items():
        if not grades:
            continue

        avg = sum(grades) / len(grades)
        good = [g for g in grades if g >= 4]
        bad = [g for g in grades if g <= 3]

        result[subject] = {
            "grades": grades,
            "avg": round(avg, 2),
            "good": good,
            "bad": bad
        }

    return result

# =========================
# GOALS
# =========================
def calculate_goal(grades, target):
    total = sum(grades)
    count = len(grades)

    needed = 0
    while True:
        new_avg = (total + 5 * needed) / (count + needed)
        if new_avg >= target:
            return needed
        needed += 1

# =========================
# EXCEL
# =========================
def to_excel(result):
    df_summary = pd.DataFrame([
        {"Subject": k, "Average": v["avg"]}
        for k, v in result.items()
    ])
    return df_summary

# =========================
# UI
# =========================
st.markdown('<div class="title">⚡ ELJUR ANALYTICS ⚡</div>', unsafe_allow_html=True)

url = st.text_input("🌐 Ссылка на ЭлЖур")
login = st.text_input("👤 Логин")
password = st.text_input("🔒 Пароль", type="password")

if st.button("🚀 Запустить"):
    with st.spinner("Загрузка..."):
        driver = setup_driver()

        success = login_eljur(driver, url, login, password)

        if not success:
            st.error("Ошибка входа")
            st.stop()

        data = parse_grades(driver)

        if not data:
            st.error("Не удалось получить оценки (нужно поменять селекторы)")
            st.stop()

        result = analyze(data)

        st.success("Данные загружены!")

        # ВВОД ЦЕЛЕЙ
        targets = {}
        for subject in result:
            targets[subject] = st.number_input(
                f"Цель для {subject}",
                min_value=2.0,
                max_value=5.0,
                step=0.1
            )

        # ВЫВОД
        for subject, info in result.items():
            needed = calculate_goal(info["grades"], targets[subject])

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

        # ГРАФИК
        df = pd.DataFrame([
            {"Subject": k, "Average": v["avg"]}
            for k, v in result.items()
        ])

        fig = px.bar(df, x="Subject", y="Average", title="Средний балл")
        st.plotly_chart(fig)

        # EXCEL
        excel = to_excel(result)
        st.download_button(
            "💾 Скачать Excel",
            excel.to_csv(index=False),
            file_name="grades.csv"
        )

        driver.quit()