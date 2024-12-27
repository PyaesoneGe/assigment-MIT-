import psycopg2


db_params = {
    'dbname': 'postgres',  
    'user': 'postgres',    
    'password': 'root1234',    
    'host': 'localhost', 
    'port': 5432        
}

create_table_query = '''
CREATE TABLE IF NOT EXISTS students (
    SID VARCHAR(10) PRIMARY KEY, 
    name VARCHAR(100) NOT NULL,
    birthdate DATE NOT NULL,
    nrc VARCHAR(50) NOT NULL,
    fname VARCHAR(20) NOT NULL,
    state VARCHAR(20) NOT NULL,
    division VARCHAR(20) NOT NULL,
    address VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100)
);
'''

create_student_details_query = '''
CREATE TABLE IF NOT EXISTS student_details (
    SID VARCHAR(10) NOT NULL,    
    DID VARCHAR(10) NOT NULL,    
    year VARCHAR(10) NOT NULL,   
    mark1 INT,                   
    mark2 INT,                   
    PRIMARY KEY (SID, DID),     
    FOREIGN KEY (SID) REFERENCES students(SID) ON DELETE CASCADE ON UPDATE CASCADE
);

'''



try:
   
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    
    cursor.execute(create_table_query)  
    cursor.execute(create_student_details_query)  
    connection.commit() 

    print("Table 'students' and 'student_details' created successfully!")

except psycopg2.Error as e:
    print(f"Error: {e}")

finally:
    
    if cursor:
        cursor.close()
    if connection:
        connection.close()
