import json
import requests
import re

def handler(request):
    try:
        # получаем данные
        body = request.get_json()
        url = body.get("url")
        login = body.get("login")
        password = body.get("password")

        session = requests.Session()

        # =========================
        # ПОПЫТКА ЛОГИНА
        # =========================
        session.get(url)

        payload = {
            "login": login,
            "password": password
        }

        session.post(url, data=payload)

        # =========================
        # ПОЛУЧАЕМ HTML
        # =========================
        response = session.get(url)
        html = response.text

        # =========================
        # ПАРСИНГ (regex)
        # =========================
        result = {}

        # ⚠️ универсальный поиск оценок (пример)
        subjects = re.findall(r'([А-Яа-яA-Za-z ]+)</td>.*?(\d(?:,\d)*)', html)

        for subject, grades_str in subjects:
            grades = [int(x) for x in re.findall(r'\d', grades_str)]

            if not grades:
                continue

            avg = sum(grades) / len(grades)

            result[subject.strip()] = {
                "grades": grades,
                "avg": round(avg, 2)
            }

        # fallback (если не нашли)
        if not result:
            result = {
                "Ошибка": {
                    "grades": [],
                    "avg": 0,
                    "message": "Не удалось распарсить — нужен кастомный селектор"
                }
            }

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }