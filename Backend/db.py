import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="Student_Data",
    user="postgres",
    password="Barbole@8080",
    port="5432"
)

cursor = conn.cursor()



