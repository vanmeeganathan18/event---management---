import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # your mysql password
        database="event_db"
    )

    cursor = db.cursor(dictionary=True)
    print("✅ Connected to MySQL successfully")

except Exception as e:
    print("❌ DB Error:", e)