import streamlit as st
import requests
import hashlib

# ================================
# СТИЛЬ (ФУТУРИСТИЧЕСКИЙ)
# ================================
st.markdown("""
<style>
body {
    background-color: #0f172a;
    color: white;
}

.stButton button {
    background: linear-gradient(90deg, #00f5ff, #7c3aed);
    color: white;
    border-radius: 10px;
    border: none;
}

.stTextInput input {
    background-color: #1e293b;
    color: white;
}

h1, h2, h3 {
    color: #00f5ff;
}
</style>
""", unsafe_allow_html=True)

# ================================
# API
# ================================
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

# ================================
# USER SYSTEM
# ================================
if "users" not in st.session_state:
    st.session_state.users = {"admin": hashlib.sha256("admin123".encode()).hexdigest()}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================================
# AUTH UI
# ================================
st.title("⚽ FUTURE FOOTBALL APP")

menu = ["Вход", "Регистрация"]
choice = st.sidebar.selectbox("Меню", menu)

if choice == "Регистрация":
    st.subheader("Создать аккаунт")
    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Зарегистрироваться"):
        st.session_state.users[username] = hash_password(password)
        st.success("Аккаунт создан")

if choice == "Вход":
    st.subheader("Вход")
    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        if username in st.session_state.users and \
           st.session_state.users[username] == hash_password(password):
            st.session_state.current_user = username
            st.success("Вы вошли!")
        else:
            st.error("Ошибка входа")

# ================================
# ОСНОВНОЙ ИНТЕРФЕЙС
# ================================
if st.session_state.current_user:

    st.sidebar.success(f"Вы вошли как {st.session_state.current_user}")

    tab1, tab2 = st.tabs(["📊 Матчи", "📝 Статьи"])

    # ============================
    # API FUNCTIONS
    # ============================
    def get_leagues():
        return requests.get(f"{BASE_URL}/leagues", headers=HEADERS).json()["response"]

    def get_matches(league_id):
        return requests.get(f"{BASE_URL}/fixtures?league={league_id}&season=2023",
                            headers=HEADERS).json()["response"]

    def get_stats(fixture_id):
        return requests.get(f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}",
                            headers=HEADERS).json()["response"]

    # ============================
    # TAB 1
    # ============================
    with tab1:
        st.header("Лиги")

        leagues = get_leagues()
        league_dict = {l["league"]["name"]: l["league"]["id"] for l in leagues[:15]}

        selected_league = st.selectbox("Выбери лигу", list(league_dict.keys()))

        if selected_league:
            matches = get_matches(league_dict[selected_league])

            for m in matches[:20]:
                match_name = f'{m["teams"]["home"]["name"]} vs {m["teams"]["away"]["name"]}'

                with st.expander(f"⚡ {match_name}"):

                    fixture_id = m["fixture"]["id"]
                    stats = get_stats(fixture_id)

                    if stats:
                        team1 = stats[0]
                        team2 = stats[1]

                        st.subheader("📊 Сравнение")

                        labels = []
                        values1 = []
                        values2 = []

                        for i in range(len(team1["statistics"])):
                            labels.append(team1["statistics"][i]["type"])
                            values1.append(team1["statistics"][i]["value"] or 0)
                            values2.append(team2["statistics"][i]["value"] or 0)

                        st.write(f"### {team1['team']['name']}")
                        st.bar_chart(values1)

                        st.write(f"### {team2['team']['name']}")
                        st.bar_chart(values2)

    # ============================
    # TAB 2 (СТАТЬИ)
    # ============================
    if "articles" not in st.session_state:
        st.session_state.articles = []

    with tab2:
        st.header("Статьи")

        if st.session_state.current_user == "admin":
            title = st.text_input("Заголовок")
            content = st.text_area("Контент")

            if st.button("Опубликовать"):
                st.session_state.articles.append({
                    "title": title,
                    "content": content,
                    "likes": 0,
                    "comments": []
                })

        for article in st.session_state.articles:
            st.subheader(article["title"])
            st.write(article["content"])

            if st.button("👍", key=article["title"]):
                article["likes"] += 1

            st.write(f"Лайки: {article['likes']}")

            comment = st.text_input("Комментарий", key=article["title"]+"c")

            if st.button("Отправить", key=article["title"]+"b"):
                article["comments"].append(comment)

            for c in article["comments"]:
                st.write("💬", c)