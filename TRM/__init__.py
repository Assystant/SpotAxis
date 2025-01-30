import pymysql

# Install pymysql as MySQLdb to maintain compatibility with legacy code
pymysql.install_as_MySQLdb()

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}

connection = None  # Initialize the connection variable

# Establish a connection to the database
try:
    connection = pymysql.connect(**db_config)
    print("Connection successful!")

    # Create a cursor object using the connection
    with connection.cursor() as cursor:
        # Example query: Create a table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS employees (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100),
            age INT,
            department VARCHAR(100)
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table created successfully!")

        # Example query: Insert a new employee record
        insert_employee_query = """
        INSERT INTO employees (name, age, department)
        VALUES (%s, %s, %s);
        """
        cursor.execute(insert_employee_query, ('John Doe', 28, 'Engineering'))
        connection.commit()
        print("Employee record inserted successfully!")

        # Example query: Fetch all employees
        fetch_employees_query = "SELECT * FROM employees;"
        cursor.execute(fetch_employees_query)
        employees = cursor.fetchall()

        for employee in employees:
            print(employee)

except pymysql.MySQLError as e:
    print(f"Error: {e}")

finally:
    # Close the connection if it was successfully established
    if connection:
        connection.close()
        print("Connection closed.")
    else:
        print("No connection was made.")
