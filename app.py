from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import json
from config import Config
from data.departments import DEPARTMENTS
from data.employees import EMPLOYEES
from data.calendar import ProductionCalendar


app = Flask(__name__)
app.config.from_object(Config)


# Хранилище данных 
timesheets_data = {}


def generate_timesheet_id():
    return len(timesheets_data) + 1



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/create', methods=['GET', 'POST'])
def create_timesheet():
    if request.method == 'POST':
        department_id = int(request.form.get('department'))
        has_vacation = 'has_vacation' in request.form
        has_sick_leave = 'has_sick_leave' in request.form

        vacations = {}
        sick_leaves = {}
        
        if has_vacation:
            vacation_dates = request.form.getlist('vacation_date[]')
            vacation_employees = request.form.getlist('vacation_employee[]')
            for i, emp_id in enumerate(vacation_employees):
                if i < len(vacation_dates):
                    vacations[int(emp_id)] = vacation_dates[i]
        
        if has_sick_leave:
            sick_dates = request.form.getlist('sick_date[]')
            sick_employees = request.form.getlist('sick_employee[]')
            for i, emp_id in enumerate(sick_employees):
                if i < len(sick_dates):
                    sick_leaves[int(emp_id)] = sick_dates[i]
        
        timesheet_id = generate_timesheet_id()
        start_date = datetime.now().date()
        
        department_employees = [emp for emp in EMPLOYEES if emp['department_id'] == department_id]
        
        work_days = ProductionCalendar.get_two_week_period(start_date)
        
        timesheet = {
            'id': timesheet_id,
            'department_id': department_id,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'period': f"{work_days[0]} - {work_days[-1]}",
            'has_vacation': has_vacation,
            'has_sick_leave': has_sick_leave,
            'vacations': vacations,
            'sick_leaves': sick_leaves,
            'work_days': [day.strftime('%Y-%m-%d') for day in work_days],
            'employees': [],
            'status': 'created'
        }
        
        for emp in department_employees:
            employee_data = {
                'id': emp['id'],
                'name': emp['name'],
                'position': emp['position'],
                'attendance': {}
            }
            
            for day in work_days:
                day_str = day.strftime('%Y-%m-%d')
                status = 'работа'
                
                if emp['id'] in vacations:
                    vac_date = datetime.strptime(vacations[emp['id']], '%Y-%m-%d').date()
                    if day == vac_date:
                        status = 'отпуск'
                
                if emp['id'] in sick_leaves:
                    sick_date = datetime.strptime(sick_leaves[emp['id']], '%Y-%m-%d').date()
                    if day == sick_date:
                        status = 'больничный'
                
                employee_data['attendance'][day_str] = status
            
            timesheet['employees'].append(employee_data)
        
        timesheets_data[timesheet_id] = timesheet
        
        return redirect(url_for('view_timesheet', timesheet_id=timesheet_id))
    
    return render_template('create_timesheet.html', 
                         departments=DEPARTMENTS, 
                         employees=EMPLOYEES)



@app.route('/timesheet/<int:timesheet_id>')
def view_timesheet(timesheet_id):
    timesheet = timesheets_data.get(timesheet_id)
    if not timesheet:
        return "Табель не найден", 404
    
    department = next((dept for dept in DEPARTMENTS if dept['id'] == timesheet['department_id']), None)
    
    return render_template('view_timesheet.html', 
                         timesheet=timesheet,
                         department=department)



@app.route('/api/employees/<int:department_id>')
def get_employees_by_department(department_id):
    department_employees = [emp for emp in EMPLOYEES if emp['department_id'] == department_id]
    return jsonify(department_employees)



@app.route('/api/workdays')
def get_work_days():
    start_date_str = request.args.get('start_date')
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = None
    
    work_days = ProductionCalendar.get_two_week_period(start_date)
    return jsonify([day.strftime('%Y-%m-%d') for day in work_days])



if __name__ == '__main__':
    app.run(debug=True)