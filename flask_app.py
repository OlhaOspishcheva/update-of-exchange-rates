from flask import Flask, request, jsonify
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Дозволяємо відображення кирилиці
app.config['JSON_AS_ASCII'] = False

# Шлях до файлу ключа
JSON_KEY_FILE = "new-project-api-481614-bafd0d733d8e.json"

# 1. Налаштування Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_google_sheet():
    """Отримати доступ до Google Sheets"""
    creds = Credentials.from_service_account_file(JSON_KEY_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open("currency_rates").sheet1
    return sheet

def daterange(start_date, end_date):
    """Генератор діапазону дат"""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

@app.route("/")
def index():
    """Головна сторінка"""
    return jsonify({
        "service": "NBU Currency Rates API",
        "endpoints": {
            "/update_rates": "GET - Оновити курси валют",
            "parameters": "?update_from=YYYY-MM-DD&update_to=YYYY-MM-DD"
        }
    })

@app.route("/update_rates", methods=["GET"])
def update_rates():
    """Оновлення курсів валют з API НБУ"""
    # Поточна дата для замовчування
    today = datetime.now().strftime("%Y-%m-%d")

    # Отримуємо параметри update_from та update_to
    u_from = request.args.get("update_from") or today
    u_to = request.args.get("update_to") or today

    # Валідація дат
    try:
        start = datetime.strptime(u_from, "%Y-%m-%d")
        end = datetime.strptime(u_to, "%Y-%m-%d")
    except ValueError:
        return jsonify({
            "error": "Неправильний формат дати. Використовуйте YYYY-MM-DD"
        }), 400

    # Перевірка логіки дат
    if start > end:
        return jsonify({
            "error": "Дата 'update_from' не може бути пізніше 'update_to'"
        }), 400

    rows = []
    errors = []

    # Отримання даних з API НБУ
    for single_date in daterange(start, end):
        date_str_api = single_date.strftime("%Y%m%d")
        date_str_display = single_date.strftime("%Y-%m-%d")

        # API НБУ
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=" + date_str_api + "&json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Шукаємо USD
            usd_data = next((x for x in data if x.get("cc") == "USD"), None)

            if usd_data:
                rows.append([
                    date_str_display,
                    "USD",
                    usd_data.get("rate")
                ])
            else:
                errors.append("USD не знайдено для " + date_str_display)
        except requests.exceptions.Timeout:
            errors.append("Timeout для " + date_str_display)
        except requests.exceptions.RequestException as e:
            errors.append("Помилка запиту для " + date_str_display + ": " + str(e))
        except Exception as e:
            errors.append("Невідома помилка для " + date_str_display + ": " + str(e))
    # Збереження в Google Sheets
    if rows:
        try:
            sheet = get_google_sheet()
            sheet.append_rows(rows, value_input_option="RAW")

            return jsonify({
                "status": "success",
                "rows_added": len(rows),
                "period": u_from + " - " + u_to,
                "errors": errors if errors else None
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": "Помилка запису в Google Sheets: " + str(e)
                }), 500
    return jsonify({
        "status": "error",
        "message": "Дані не знайдено",
        "errors": errors
    }), 404

@app.route("/test_nbu")
def test_nbu():
    """Тест API НБУ"""
    today = datetime.now().strftime("%Y%m%d")
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=" + today + "&json"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        usd = next((x for x in data if x.get("cc") == "USD"), None)

        return jsonify({
            "status": "success",
            "date": today,
            "usd_rate": usd.get("rate") if usd else None,
            "total_currencies": len(data)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
