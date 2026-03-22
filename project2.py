import streamlit as st
import requests

# ================================
# CONFIG
# ================================
API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": dddaaf8a535c054da52d0afe43b15af2
}

OWNER_PASSWORD = "admin123"  # доступ к созданию статей

# ================================
# API FUNCTIONS
# ================================
def get_leagues():
    url = f"{BASE_URL}/leagues"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", [])

def get_matches(league_id):
    url = f"{BASE_URL}/fixtures?league={league_id}&season=2023"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", [])

def get_match_stats(fixture_id):
    url = f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("response", [])

# ================================
# SESSION STATE (CMS)
# ================================
if "articles" not in st.session_state:
    st.session_state.articles = []

if "comments" not in st.session_state:
    st.session_state.comments = {}

if "likes" not in st.session_state:
    st.session_state.likes = {}

# ================================
# UI
# ================================
st.title("⚽ Football Analytics App")

tab1, tab2 = st.tabs(["📊 Матчи", "📝 Статьи"])

# ================================
# TAB 1 — FOOTBALL DATA
# ================================
with tab1:

    st.header("Выбор лиги")

    leagues = get_leagues()
    league_options = {l["league"]["name"]: l["league"]["id"] for l in leagues[:20]}

    selected_league = st.selectbox("Лига", list(league_options.keys()))

    if selected_league:
        league_id = league_options[selected_league]

        matches = get_matches(league_id)

        match_dict = {
            f'{m["teams"]["home"]["name"]} vs {m["teams"]["away"]["name"]}':
            m["fixture"]["id"]
            for m in matches[:50]
        }

        selected_match = st.selectbox("Матч", list(match_dict.keys()))

        if selected_match:
            fixture_id = match_dict[selected_match]

            stats = get_match_stats(fixture_id)

            st.subheader("📊 Статистика матча")

            for team in stats:
                st.write(f'### {team["team"]["name"]}')
                for s in team["statistics"]:
                    st.write(f'{s["type"]}: {s["value"]}')

# ================================
# TAB 2 — CMS
# ================================
with tab2:

    st.header("📝 Статьи")

    password = st.text_input("Пароль владельца", type="password")

    # СОЗДАНИЕ СТАТЬИ
    if password == OWNER_PASSWORD:
        st.subheader("Создать статью")

        title = st.text_input("Заголовок")
        content = st.text_area("Контент")

        if st.button("Опубликовать"):
            article = {
                "id": len(st.session_state.articles),
                "title": title,
                "content": content
            }
            st.session_state.articles.append(article)
            st.success("Статья опубликована")

    # СПИСОК СТАТЕЙ
    for article in st.session_state.articles:
        st.subheader(article["title"])
        st.write(article["content"])

        article_id = article["id"]

        # ЛАЙКИ
        if article_id not in st.session_state.likes:
            st.session_state.likes[article_id] = 0

        if st.button(f"👍 Like ({st.session_state.likes[article_id]})", key=f"like_{article_id}"):
            st.session_state.likes[article_id] += 1

        # КОММЕНТАРИИ
        if article_id not in st.session_state.comments:
            st.session_state.comments[article_id] = []

        comment = st.text_input(f"Комментарий", key=f"comment_{article_id}")

        if st.button("Отправить", key=f"send_{article_id}"):
            st.session_state.comments[article_id].append(comment)

        for c in st.session_state.comments[article_id]:
            st.write(f"💬 {c}")