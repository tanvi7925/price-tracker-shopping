# app.py
from flask import Flask, render_template, request, redirect
import csv
import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

CSV_FILE = "products.csv"

EMAIL_ADDRESS = "phoenix2016.in@google.com"
EMAIL_PASSWORD = "yourpassword"  # App password
TO_EMAIL = "youremail@example.com"

def scrape_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    # Example for Amazon
    price_tag = soup.find("span", {"class": "a-price-whole"})
    if price_tag:
        price = price_tag.get_text(strip=True).replace(",", "").replace("₹", "")
        return float(price)
    return None

def send_email(product_name, price, url):
    subject = f"Price Alert: {product_name}"
    body = f"Price dropped to ₹{price}! Check here: {url}"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())

def check_prices():
    products = []
    updated = False
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            current_price = scrape_price(row["url"])
            if current_price:
                row["current_price"] = current_price
                if current_price <= float(row["target_price"]):
                    send_email(row["name"], current_price, row["url"])
            products.append(row)
    return products

@app.route("/")
def index():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "url", "target_price"])
            writer.writeheader()
    products = check_prices()
    return render_template("index.html", products=products)

@app.route("/add", methods=["POST"])
def add_product():
    name = request.form["name"]
    url = request.form["url"]
    target_price = request.form["target_price"]
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, url, target_price])
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
