from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Course Management System")

# The VIP Bouncer Rulebook: Every course MUST have an ID, Name, and Price
class Course(BaseModel):
    id: int
    name: str
    price: int

# Our short-term memory (Database)
courses = []

# ------------------ GET: View Courses ------------------
@app.get("/courses")
def get_courses():
    return {"message": "Available courses", "courses": courses}

# ------------------ POST: Add Course ------------------
# Notice there is no {course_name} in the URL anymore!
@app.post("/add_course")
def add_course(new_course: Course):
    # .dict() converts the Pydantic model back into a standard Python dictionary
    courses.append(new_course.dict())
    return {"message": f"Course added: {new_course.name}"}

# ------------------ PUT: Update Course ------------------
# We use the ID in the URL to find it, but the new data comes in the body
@app.put("/update_course/{course_id}")
def update_course(course_id: int, updated_course: Course):
    for i, course in enumerate(courses):
        if course["id"] == course_id:
            courses[i] = updated_course.dict()
            return {"message": f"Course ID {course_id} updated successfully!"}
            
    return {"message": f"Course ID {course_id} not found."}

# ------------------ DELETE: Remove Course ------------------
@app.delete("/delete_course/{course_id}")
def delete_course(course_id: int):
    for i, course in enumerate(courses):
        if course["id"] == course_id:
            del courses[i]
            return {"message": f"Course ID {course_id} deleted successfully!"}
            
    return {"message": f"Course ID {course_id} not found."}
