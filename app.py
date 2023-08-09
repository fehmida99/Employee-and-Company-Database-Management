from flask import Flask, request,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from urllib.parse import quote_plus
import os
import pandas as pd

app = Flask(__name__)

@app.route("/")
def hellow():
    return "Hello Fehmida"

@app.route('/favicon.ico')
def favicon():
    return '', 204


password = quote_plus('Fehmida@123#') 
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{password}@localhost:3306/Company_Employee'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    founded_year = db.Column(db.Integer)
    employees = db.relationship("Employee", backref="company")

class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    designation = db.Column(db.String(255))
    salary = db.Column(db.Integer)
    company_id = db.Column(db.Integer, db.ForeignKey("company.company_id"))


with app.app_context():
    db.create_all()

def process_excel(file_path):
    df = pd.read_excel(file_path)

    with app.app_context():
        for _, row in df.iterrows():
            company_name = row['company_name']
            location = row['location']
            founded_year = row['founded_year']
            emp_name = row['emp_name']
            designation = row['designation']
            salary = row['salary']

            company = Company.query.filter_by(company_name=company_name).first()
            if not company:
                company = Company(company_name=company_name, location=location, founded_year=founded_year)
                db.session.add(company)
                db.session.commit()

            employee = Employee(name=emp_name, designation=designation, salary=salary, company=company)
            db.session.add(employee)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    print("Data inserted successfully....")

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and file.filename.endswith('.xlsx'):
        
        
        file_path = os.path.join(app.root_path, 'uploads', 'emp_details.xlsx')
        target_dir = os.path.join(app.root_path, 'uploads')
        os.makedirs(target_dir, exist_ok=True)
        file.save(file_path)
        process_excel(file_path)
        return "File uploaded and Moved Successfully...."
    return "Invalid file format...."



@app.route('/upload-form', methods=['GET'])
def upload_form():
    return render_template('form.html')




if __name__ == '__main__':
    app.run(port=8080)