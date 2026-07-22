from fastapi import FastAPI

app = FastAPI(title="Course Management System")
l=[]

#get
@app.get("/")
def home():
    return {"message": "The following are the courses available", "courses": l}   

#get
@app.get("/courses")
def home():
    return {"message": "The following are the courses available", "courses": l}   
#post
@app.post("/add_course/{course_name}")
def add_course(course_name: str):
    l.append(course_name)
    return {"message": f"Course added: {course_name}"}

#put

@app.put("/update_course/{old_course_name}/{new_course_name}")
def update_course(old_course_name: str, new_course_name: str):
    if old_course_name in l:
        index = l.index(old_course_name)
        l[index] = new_course_name
        return {"message": f"Course updated: {old_course_name} to {new_course_name}"}
    else:
        return {"message": f"Course not found: {old_course_name}"}

#delete

@app.delete("/delete_course/{course_name}")
def delete_course(course_name: str):
    if course_name in l:
        l.remove(course_name)
        return {"message": f"Course deleted: {course_name}"}
    else:
        return {"message": f"Course not found: {course_name}"}
