import psycopg2
from flask import Flask, render_template, request,redirect,url_for,session,jsonify
import datetime
from pprint import pprint

db_params = {
    'dbname': 'postgres', 
    'user': 'postgres',    
    'password': 'root1234',  
    'host': 'localhost',   
    'port': 5432        
}

connection = psycopg2.connect(**db_params)
cursor = connection.cursor()

if cursor:
    print("Connected to the database successfully!")
else:
    print("Failed to connect to the database.")


app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('student_data'))


@app.route('/submit_student_data', methods=['POST'])
def submit_student_data():
    # Collecting student data from the form
    SID = request.form['student_id']
    name = request.form['name']
    birthdate = request.form['bod']
    nrc = request.form['nrc']
    fname = request.form['fname']
    state = request.form['state']
    division = request.form['division']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']

    # Collecting details data (DID, year, mark1, mark2)
    details_data = []
    for key, value in request.form.items():
        if key.startswith('details[') and 'Details_id' in key:
            index = key.split('[')[1].split(']')[0]
            details_data.append({
                'DID': request.form[f'details[{index}][Details_id]'],
                'year': request.form[f'details[{index}][year]'],
                'mark1': request.form[f'details[{index}][mark1]'],
                'mark2': request.form[f'details[{index}][mark2]']
            })

    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Check if student already exists in the students table
        check_query = "SELECT EXISTS (SELECT 1 FROM students WHERE SID = %s)"
        cursor.execute(check_query, (SID,))
        student_exists = cursor.fetchone()[0]

        if student_exists:
            message = "Student already exists!"
        else:
            # Insert student data
            insert_student_query = """
                INSERT INTO students (SID, name, birthdate, nrc, fname, state, division, address, phone, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_student_query, (
                SID, name, birthdate, nrc, fname, state, division, address, phone, email
            ))

            # Insert details data for the student
            insert_details_query = """
                INSERT INTO student_details (SID, DID, year, mark1, mark2)
                VALUES (%s, %s, %s, %s, %s)
            """
            for detail in details_data:
                cursor.execute(insert_details_query, (
                    SID, detail['DID'], detail['year'], detail['mark1'], detail['mark2']
                ))

            connection.commit()
            message = "Student data successfully saved!"

    except (Exception, psycopg2.Error) as error:
        connection.rollback()
        print("Error while inserting data into PostgreSQL:", error)
        message = "An error occurred while saving student data."

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # After the operation, render the response (success message or error message)
    return redirect(url_for('student_data', message=message))

@app.route('/api/student_data', methods=['GET'])
def api_student_data():
    try:
        
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        
        
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        
        
        cursor.execute("SELECT * FROM student_details")
        details = cursor.fetchall()
        
        
        student_data = [{ 
            'SID': student[0],  
                'name': student[1],
                'birthdate': student[2],
                'nrc': student[3],
                'fname': student[4],
                'state': student[5],
                'division': student[6],
                'address': student[7],
                'phone': student[8],
                'email': student[9]
        } for student in students]

        details_data = [{
            'DID': detail[0], 
                'year': detail[1],
                'mark1': detail[2],
                'mark2': detail[3],
                'SID': detail[4]
        } for detail in details]
        
       
        return jsonify({'students': student_data, 'details': details_data})
    
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return jsonify({'error': 'An error occurred while fetching data'}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/student_data', methods=['GET'])
def student_data(): 
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()
        
        
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        
        
        cursor.execute("SELECT * FROM student_details")
        details = cursor.fetchall()
        
        
        student_data = [
            {
                'SID': student[0],  
                'name': student[1],
                'birthdate': student[2],
                'nrc': student[3],
                'fname': student[4],
                'state': student[5],
                'division': student[6],
                'address': student[7],
                'phone': student[8],
                'email': student[9]
                
            } for student in students
        ]
        details_data = [
            {
                'Details_id': detail[1], 
                'year': detail[2],
                'mark1': detail[3],
                'mark2': detail[4],
                'SID': detail[0]
            } for detail in details
        ]
        
       
        result = {
            'students': student_data,
            'details': details_data
        }
        
        return render_template(
            'student_data.html',
            students=student_data,
            details=details_data
        )
    
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return jsonify({'error': 'Database error occurred'}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/handle_action', methods=['POST'])
def handle_action():
    action = request.form.get('action')
    student_id = request.form.get('student')
    print(student_id)

    
    if action == "add":
        
        return render_template('student.html', student=None,detail=None)
    elif action == "delete":
        print("Delete student with ID:", student_id)
        if student_id:
            try:
                connection = psycopg2.connect(**db_params)
                cursor = connection.cursor()

                
                cursor.execute("DELETE FROM students WHERE SID = %s", (student_id,))
                connection.commit()

                return redirect(url_for('student_data'))
            except Exception as error:
                print("Error deleting student:", error)
                return "An error occurred while deleting the student."
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
        else:
            return "Please select a student !", 400
    else:
        return "Invalid action.", 400
    

@app.route('/update/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    student = None
    detail = None

    
    if request.method == 'GET':
        try:
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()

            if student_id:
                
                cursor.execute("SELECT * FROM students WHERE SID = %s", (student_id,))
                student = cursor.fetchone()

               
                cursor.execute("SELECT * FROM student_details WHERE SID = %s", (student_id,))
                detail = cursor.fetchall()
            else:
                return "Student not found"

        except (Exception, psycopg2.Error) as error:
            print("Error fetching student data:", error)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return render_template('update_student.html', student=student, detail=detail)

    
    if request.method == 'POST':
     
        student_id = request.form['student_id']
        name = request.form['name']
        bod = request.form['bod']
        nrc = request.form['nrc']
        fname = request.form['fname']
        state = request.form['state']
        division = request.form['division']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']

       
        details_data = []
        pprint(f"request {request.form}")
        for key, value in request.form.items():
            if key.startswith('details[') and 'Details_id' in key:
                index = key.split('[')[1].split(']')[0]
                details_data.append({
                    'DID': request.form[f'details[{index}][Details_id]'],
                    'year': request.form[f'details[{index}][year]'],
                    'mark1': request.form[f'details[{index}][mark1]'],
                    'mark2': request.form[f'details[{index}][mark2]']
                })

                pprint(details_data)

        try:
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()

            
            cursor.execute("""
                UPDATE students
                SET name = %s, birthdate = %s, nrc = %s, fname = %s, state = %s, 
                    division = %s, address = %s, phone = %s, email = %s
                WHERE SID = %s
            """, (name, bod, nrc, fname, state, division, address, phone, email, student_id))
            
            cursor.execute("DELETE FROM student_details WHERE SID = %s", (student_id,))
            
           
            for detail in details_data:
                cursor.execute("""
    INSERT INTO student_details (SID, DID, year, mark1, mark2)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (SID, DID)  -- Specify the composite key here
    DO UPDATE SET year = EXCLUDED.year, mark1 = EXCLUDED.mark1, mark2 = EXCLUDED.mark2
""", (student_id, detail['DID'], detail['year'], detail['mark1'], detail['mark2']))


            connection.commit() 
            print("Student data updated successfully")

           
            return redirect(url_for('student_data'))

        except (Exception, psycopg2.Error) as error:
            print("Error updating student data:", error)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return "Error updating student information."



@app.route('/search', methods=['GET'])
def search_students():
    query = request.args.get('query', '').strip()  
    print(query)

    if not query:
        return redirect(url_for('student_data')) 

    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        
        search_query = """
        SELECT * FROM students
        WHERE SID ILIKE %s OR name ILIKE %s
        """
        search_pattern = f"%{query}%"
        cursor.execute(search_query, (search_pattern, search_pattern))
        search_results = cursor.fetchall()
        students = [
            {
                'SID': student[1],  
                'name': student[2],
                'birthdate': student[3],
                'nrc': student[4],
                'fname': student[5],
                'state': student[6],
                'division': student[7],
                'address': student[8],
                'phone': student[9],
                'email': student[10]
                
            } for student in search_results
        ]
        
        details = []
        if students:
            student_ids = [student["SID"] for student in students]
            print(student_ids) #debug
            details_query = """
            SELECT * FROM student_details
            WHERE SID = ANY(%s)
            """
            cursor.execute(details_query, (student_ids,))
            details_results = cursor.fetchall()
            pprint(details_results) #debug
            details = [
                {
                    "Details_id": detail[1], 
                    "year": detail[2],
                    "mark1": detail[3],
                    "mark2": detail[4],
                    "SID": detail[5]   
                }
                for detail in details_results
            ]

        return render_template('student_data.html', students=students,details= details)
    except Exception as error:
        print("Error during search:", error)
        return "An error occurred while searching for students."
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    with app.app_context():
        app.run(host='0.0.0.0', port=5001, debug=True)
