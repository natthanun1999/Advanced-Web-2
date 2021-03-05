from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join, and_, or_, asc
from sqlalchemy.sql import select
import sqlite3

app = Flask(__name__)
app.secret_key = "SecretKey"

#SqlAlchemy Database Configuration With sqlite3
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database/employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

###### Table Employees ######
class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname   = db.Column(db.String(30), nullable=False)
    lastname    = db.Column(db.String(30), nullable=False)
    phone       = db.Column(db.String(20), nullable=False)
    pos_id      = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)

    def __init__(self, firstname, lastname, phone, pos_id):
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.pos_id = pos_id

###### Table Positions ######
class Positions(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100))
    
    def __init__(self, name):
        self.name = name

###### Table View ######
'''
class Employees_View(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name_Emp = db.Column(db.Integer, db.ForeignKey('employees.id'))
    name_Pos = db.Column(db.Integer, db.ForeignKey('positions.id'))
   
    def __init__(self, name_Emp, name_Pos):
        self.name_Emp = name_Emp
        self.name_Pos = name_Pos
'''

@app.route('/')
def Index():
    views = db.session.query(
        Employees.id, Employees.firstname, Employees.lastname, Positions.name
    ).outerjoin(Employees, Employees.pos_id == Positions.id)\
    .order_by(asc(Employees.id))\
    .all()

    return render_template('views/index.html', data = views)

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        pos_id = request.form['pos_id']

        newEmp = Employees(firstname, lastname, phone, pos_id)
        db.session.add(newEmp)
        db.session.commit()

        flash("Employee Inserted Successfully.")
        return redirect(url_for('Index'))
    
    return render_template("views/insert.html", positions = Positions.query.all())

@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        employee = Employees.query.get(request.form.get('id'))
        employee.firstname = request.form['firstname']
        employee.lastname = request.form['lastname']
        employee.phone = request.form['phone']
        employee.pos_id = request.form['pos_id']

        db.session.commit()

        flash("Employee Updated Successfully.")
        return redirect(url_for('Index'))
    
    return render_template("views/update.html", employee = Employees.query.get(id), positions = Positions.query.all())

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    Employees.query.filter(Employees.id == id).delete()

    db.session.commit()

    flash("Employee Deleted Successfully.")
    return redirect(url_for('Index'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)