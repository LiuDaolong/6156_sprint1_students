# 6156_sprint1_students
microservice of students 

## Contributors
Daolong Liu
Yuming Tian

## RESTful API
- /students
  - GET: list all student ids in the database
- /students/{sid}
  - GET: get the detailed information of a student
  - POST: modify the student's profile
  - DELETE: remove the student from the database
- /students/search
  - POST: search students with the given query/filter
