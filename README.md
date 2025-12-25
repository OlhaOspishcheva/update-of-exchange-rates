# NBU Currency Rates API Service
This is a Flask-based microservice designed to automatically fetch official currency exchange rates (USD) from the National Bank of Ukraine (NBU) for a specified period and save the data directly into Google Sheets.

## 🚀 Key Features
Automated Data Collection: Seamless integration with the official NBU API.

Direct Export: Automatically records the date, currency code, and exchange rate into a Google Spreadsheet.

Flexible Date Filtering: Supports custom date ranges via URL query parameters.

Robust Error Handling: Includes date format validation and detailed logging for connection or API timeouts.

## 🛠 Tech Stack
Python 3.x

Flask: Web framework for the API endpoints.

Gspread: Library for interacting with Google Sheets API.

Requests: For executing HTTP calls to the NBU server.

Google OAuth 2.0: Secure authentication using service account credentials.

## 📋 Setup and Installation Guide

1. Google Cloud Configuration
Create a project in the Google Cloud Console.

Enable the Google Sheets API and Google Drive API.

Create a Service Account, generate a key, and download the JSON file.

Rename the downloaded file to new-project-api-481614-bafd0d733d8e.json (or update the filename in the code).

Create a Google Spreadsheet named currency_rates.

Important: "Share" your Google Spreadsheet by adding the Service Account's email (found in the JSON file) with Editor permissions.

2. Install Dependencies
Bash

pip install flask requests gspread google-auth
3. Run the Application
Bash

python your_file_name.py
The service will be available at: http://127.0.0.1:5000

## 📑 API Endpoints
1. Index
GET / Returns a list of available endpoints and service information.

2. NBU Connection Test
GET /test_nbu Verifies the connection to the NBU API and returns the current USD rate without saving it to the spreadsheet.

3. Update Rates
GET /update_rates The primary method for collecting data and writing it to the spreadsheet.

Parameters:

update_from (optional): Start date in YYYY-MM-DD format. Defaults to today.

update_to (optional): End date in YYYY-MM-DD format. Defaults to today.

Example Request: http://127.0.0.1:5000/update_rates?update_from=2023-01-01&update_to=2023-01-10

## 🗃 Google Sheets Data Structure
The application appends rows in the following format:

Date (e.g., 2023-12-25)

Currency Code (USD)

Exchange Rate (e.g., 37.55)

## 🛡 Exception Handling
400 Bad Request: Returned for invalid date formats or if the "from" date is later than the "to" date.

500 Internal Server Error: Returned if there is a failure while writing to Google Sheets.

Error Logging: If the NBU API fails for specific dates within a range, the error is logged in the JSON response, but the service continues processing the remaining dates.
