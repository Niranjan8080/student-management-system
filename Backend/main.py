from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from db import conn

app = FastAPI()


class StudentLogin(BaseModel):
    roll_no: int = Field(..., gt=0)
    name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=4)


class TeacherLogin(BaseModel):
    password: str

class AddStudent(BaseModel):
    name: str = Field(..., min_length=2)
    fees: float = Field(..., gt=0)
    password: str = Field(..., min_length=4)

class UpdateStudent(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    fees: Optional[float] = Field(None, gt=0)
    password: Optional[str] = Field(None, min_length=4)

class ChangePassword(BaseModel):
    roll_no: int = Field(..., gt=0)
    old_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=4)

@app.post("/student")
def student_login(student: StudentLogin):

    cursor = conn.cursor()

    query = """
    SELECT Roll_No, Name, Fees, Password
    FROM student
    WHERE Roll_No=%s
    AND Name=%s
    AND Password=%s
    """

    cursor.execute(
        query,
        (student.roll_no, student.name, student.password)
    )

    data = cursor.fetchone()

    cursor.close()

    if data is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Roll Number, Name or Password"
        )

    return {
        "Roll_No": data[0],
        "Name": data[1],
        "Fees": float(data[2]),
        "Password": data[3]
    }


@app.post("/teacher/login")
def teacher_login(teacher: TeacherLogin):

    if teacher.password != "NSB@8080":
        raise HTTPException(status_code=401, detail="Wrong Password")

    return {
        "message": "Login Successful",
        "options": [
            "Check Student List",
            "Add New Student"
        ]
    }
@app.get("/teacher/students")
def student_list():

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM student")

    rows = cursor.fetchall()

    cursor.close()

    students = []

    for row in rows:
        students.append({
            "Roll_No": row[0],
            "Name": row[1],
            "Fees": float(row[2]),
            "Password": row[3]
        })

    return students

@app.post("/teacher/add")
def add_student(student: AddStudent):

    cursor = conn.cursor()

    # Generate next Roll Number
    cursor.execute("SELECT COALESCE(MAX(roll_no),100)+1 FROM student")
    roll_no = cursor.fetchone()[0]

    query = """
    INSERT INTO student(Roll_No, Name, Fees, Password)
    VALUES(%s,%s,%s,%s)
    """

    cursor.execute(
        query,
        (
            roll_no,
            student.name,
            student.fees,
            student.password
        )
    )

    conn.commit()

    cursor.close()

    return {
        "message": "Student Added Successfully",
        "Roll_No": roll_no,
        "Name": student.name,
        "Fees": student.fees
    }

@app.put("/teacher/update/{roll_no}")
def update_student(roll_no: int, student: UpdateStudent):

    cursor = conn.cursor()

    # Check if student exists
    cursor.execute(
        "SELECT * FROM student WHERE roll_no = %s",
        (roll_no,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        raise HTTPException(
            status_code=404,
            detail="Student Not Found"
        )

    # Update student details
    cursor.execute(
        """
        UPDATE student
        SET
            name = COALESCE(%s, name),
            fees = COALESCE(%s, fees),
            password = COALESCE(%s, password)
        WHERE roll_no = %s
        """,
        (
            student.name,
            student.fees,
            student.password,
            roll_no
        )
    )

    conn.commit()

    cursor.close()

    return {
        "message": "Student Updated Successfully",
        "Roll_No": roll_no
    }

@app.delete("/teacher/delete/{roll_no}")
def delete_student(roll_no: int):

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM student WHERE Roll_No=%s",
        (roll_no,)
    )

    if cursor.fetchone() is None:
        cursor.close()
        raise HTTPException(status_code=404, detail="Student Not Found")

    cursor.execute(
        "DELETE FROM student WHERE Roll_No=%s",
        (roll_no,)
    )

    conn.commit()
    cursor.close()

    return {"message": "Student Deleted Successfully"}

@app.get("/teacher/student/{roll_no}")
def get_student(roll_no: int):

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM student WHERE Roll_No=%s",
        (roll_no,)
    )

    row = cursor.fetchone()

    cursor.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Student Not Found")

    return {
        "Roll_No": row[0],
        "Name": row[1],
        "Fees": float(row[2]),
        "Password": row[3]
    }

@app.put("/student/change-password")
def change_password(data: ChangePassword):

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM student
        WHERE Roll_No=%s
        AND Password=%s
        """,
        (data.roll_no, data.old_password)
    )

    if cursor.fetchone() is None:
        cursor.close()
        raise HTTPException(
            status_code=401,
            detail="Incorrect Roll Number or Password"
        )

    cursor.execute(
        """
        UPDATE student
        SET Password=%s
        WHERE Roll_No=%s
        """,
        (data.new_password, data.roll_no)
    )

    conn.commit()
    cursor.close()

    return {"message": "Password Changed Successfully"}



