import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from predict import predict_health
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



#Creating Database Tables 
class Patient(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100), nullable=False)

    dob = db.Column(db.String(20), nullable=False)

    email = db.Column(db.String(100), nullable=False)

    glucose = db.Column(db.Float, nullable=False)

    haemoglobin = db.Column(db.Float, nullable=False)

    cholesterol = db.Column(db.Float, nullable=False)

    remarks = db.Column(db.String(200))

# Home route 
@app.route("/")
def index():

    search = request.args.get("search")

    if search:

        patients = Patient.query.filter(
            Patient.fullname.ilike(f"%{search}%")
        ).all()

    else:

        patients = Patient.query.all()

    return render_template(
        "index.html",
        patients=patients
    )

@app.route("/add", methods=["GET", "POST"])
def add_patient():

    if request.method == "POST":

        fullname = request.form["fullname"]
        dob = request.form["dob"]
        email = request.form["email"]

        glucose = float(request.form["glucose"])
        haemoglobin = float(request.form["haemoglobin"])
        cholesterol = float(request.form["cholesterol"])

        # Email Validation
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, email):
            return "Invalid Email"

        # DOB Validation
        dob_date = datetime.strptime(dob, "%Y-%m-%d")

        if dob_date > datetime.now():
            return "DOB cannot be future date"

        # Numeric Validation
        if glucose <= 0:
            return "Invalid glucose value"

        if haemoglobin <= 0:
            return "Invalid haemoglobin value"

        if cholesterol <= 0:
            return "Invalid cholesterol value"

        prediction = predict_health(
            glucose,
            haemoglobin,
            cholesterol
        )

        patient = Patient(
            fullname=fullname,
            dob=dob,
            email=email,
            glucose=glucose,
            haemoglobin=haemoglobin,
            cholesterol=cholesterol,
            remarks=prediction
        )

        db.session.add(patient)
        db.session.commit()

        return redirect("/")

    return render_template("add_patient.html")



@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_patient(id):

    patient = Patient.query.get(id)

    if request.method == "POST":

        patient.fullname = request.form["fullname"]
        patient.dob = request.form["dob"]
        patient.email = request.form["email"]

        patient.glucose = float(request.form["glucose"])
        patient.haemoglobin = float(request.form["haemoglobin"])
        patient.cholesterol = float(request.form["cholesterol"])

        # Email Validation
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, patient.email):
            return "Invalid Email"

        # DOB Validation
        dob_date = datetime.strptime(patient.dob, "%Y-%m-%d")

        if dob_date > datetime.now():
            return "DOB cannot be future date"

        # Numeric Validation
        if patient.glucose <= 0:
            return "Invalid glucose value"

        if patient.haemoglobin <= 0:
            return "Invalid haemoglobin value"

        if patient.cholesterol <= 0:
            return "Invalid cholesterol value"

        patient.remarks = predict_health(
            patient.glucose,
            patient.haemoglobin,
            patient.cholesterol
        )

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit_patient.html",
        patient=patient
    )

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_patient(id):

    patient = Patient.query.get(id)

    if request.method == "POST":

        db.session.delete(patient)

        db.session.commit()

        return redirect("/")

    return render_template(
        "delete_patient.html",
        patient=patient
    )

@app.route("/pdf/<int:id>")
def patient_pdf(id):

    patient = Patient.query.get(id)

    filename = f"Patient_{patient.id}.pdf"

    pdf = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Patient Health Report",
            styles['Title']
        )
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(
            f"<b>Full Name:</b> {patient.fullname}",
            styles['Normal']
        )
    )

    content.append(
        Paragraph(
            f"<b>Date of Birth:</b> {patient.dob}",
            styles['Normal']
        )
    )

    content.append(
        Paragraph(
            f"<b>Email:</b> {patient.email}",
            styles['Normal']
        )
    )

    content.append(
        Paragraph(
            f"<b>Glucose:</b> {patient.glucose}",
            styles['Normal']
        )
    )

    content.append(
        Paragraph(
            f"<b>Haemoglobin:</b> {patient.haemoglobin}",
            styles['Normal']
        )
    )

    content.append(
        Paragraph(
            f"<b>Cholesterol:</b> {patient.cholesterol}",
            styles['Normal']
        )
    )

    content.append(
        Paragraph(
            f"<b>Prediction:</b> {patient.remarks}",
            styles['Normal']
        )
    )

    pdf.build(content)

    return send_file(
        filename,
        as_attachment=True
    )

#Creating Database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
     import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
