from flask import Flask, render_template, request, redirect, send_file
from db import db, cursor
import smtplib
from email.mime.text import MIMEText

# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# 🔹 EMAIL
def send_email(to_email, event):
    sender_email = "kv0939169@gmail.com"
    sender_password = "uuhemfxmumxqozks"

    msg = MIMEText(f"""
Registered Successfully 🎉
                   THANK YOU FOR REGISTRATION 
             
Event: {event['name']}
Date: {event['date']}
Time: {event['time']}
Venue: {event['venue']}
""")

    msg['Subject'] = "Event Registration"
    msg['From'] = sender_email
    msg['To'] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()


# 🔹 LOGIN
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username']=="admin" and request.form['password']=="admin123":
            return redirect('/dashboard')
    return render_template("login.html")


# 🔹 DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


# 🔹 ADD EVENT
@app.route('/add_event_page')
def add_event_page():
    return render_template("add_event.html")

@app.route('/add_event', methods=['POST'])
def add_event():
    cursor.execute("INSERT INTO events (name,date,time,venue) VALUES (%s,%s,%s,%s)",
                   (request.form['name'],request.form['date'],request.form['time'],request.form['venue']))
    db.commit()
    return redirect('/dashboard')


# 🔹 USER PAGE
@app.route('/user')
def user():
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    return render_template("user.html", events=events)


# 🔹 REGISTER
@app.route('/user_register', methods=['POST'])
def user_register():
    cursor.execute("""
    INSERT INTO participants (name,email,department,year,phone)
    VALUES (%s,%s,%s,%s,%s)
    """,(request.form['name'],request.form['email'],
         request.form['dept'],request.form['year'],request.form['phone']))
    db.commit()

    pid = cursor.lastrowid

    cursor.execute("INSERT INTO registrations (event_id,participant_id) VALUES (%s,%s)",
                   (request.form['event_id'], pid))
    db.commit()

    cursor.execute("SELECT * FROM events WHERE id=%s",(request.form['event_id'],))
    event = cursor.fetchone()

    send_email(request.form['email'], event)

    return render_template("success.html")


# 🔹 VIEW EVENTS
@app.route('/view_events')
def view_events():
    cursor.execute("""
    SELECT e.name AS event_name,p.name AS participant,p.email,p.department,p.year,p.phone
    FROM registrations r
    JOIN events e ON r.event_id=e.id
    JOIN participants p ON r.participant_id=p.id
    """)
    data = cursor.fetchall()
    return render_template("view_events.html", events=data)


# 🔹 PDF
@app.route('/export_pdf')
def export_pdf():
    cursor.execute("""
    SELECT e.name AS event_name,p.name,p.email,p.department,p.year,p.phone
    FROM registrations r
    JOIN events e ON r.event_id=e.id
    JOIN participants p ON r.participant_id=p.id
    """)

    data = cursor.fetchall()

    doc = SimpleDocTemplate("report.pdf")
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Event Report", styles['Title']))

    table_data = [["Event","Name","Email","Dept","Year","Phone"]]

    for row in data:
        table_data.append([
            row['event_name'],row['name'],row['email'],
            row['department'],row['year'],row['phone']
        ])

    table = Table(table_data)
    table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,colors.black)]))

    elements.append(table)
    doc.build(elements)

    return send_file("report.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True,port=5001)