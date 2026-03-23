import json
import requests
import re

def handler(request):
    try:
        body = request.get_json()
        url = body.get("url")
        login = body.get("login")
        password = body.get("password")

        session = requests.Session()

        # =========================
        # ЛОГИН
        # =========================
        payload = {
            "login": login,
            "password": password
        }

        session.post(url, data=payload)

        # =========================
        # ПОЛУЧАЕМ СТРАНИЦУ
        # =========================
        response = session.get(url)
        html = response.text

        # =========================
        # ПАРСИНГ БЕЗ BS4
        # =========================
        # ⚠️ УПРОЩЁННЫЙ regex (нужно адаптировать)
        subjects = re.findall(r'data-subject="(.*?)".*?data-grades="(.*?)"', html)

        result = {}

        for subject, grades_str in subjects:
            grades = [int(x) for x in re.findall(r'\d', grades_str)]

            if not grades:
                continue

            avg = sum(grades) / len(grades)

            result[subject] = {
                "grades": grades,
                "avg": round(avg, 2)
            }

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }