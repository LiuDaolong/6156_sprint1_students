import json
import sys
import logging
from urllib import response
import pymysql
import rds_config


logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""
---------------------- Init DB Connection ----------------------------
"""
rds_host  = "sprint1studentsdb6156.cq0pqafrrlui.us-east-1.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

try:
    conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=20)
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded.")
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()


"""
---------------------- Request Handler -------------------------------
"""
def lambda_handler(event, context):
    logger.info(event)
    response = {
        'statusCode': 500,
        'body': 'invalid request',
        'request': event
    }
    
    # /students
    if len(event.keys()) == 0:
        response = get_all_students()
    elif "endpoint" not in event.keys():
        pass
    # /students/search
    elif event["endpoint"] == "search":
        response = {
            'statusCode': 200,
            'body': 'Search method not implemented yet',
            'request': event
        }
    # /students/{sid}
    elif event["endpoint"] == "student_sid":
        sid = event["pathParams"]["sid"]
        response = get_one_student(sid)
        if event["method"] == "GET":
            pass
        elif event["method"] == "PUT" or event["method"] == "POST":
            if response['statusCode'] == 200:
                delete_one_student(sid)
            response = insert_one_student(sid, event["body"])
        elif event["method"] == "DELETE":
            response = delete_one_student(sid)
    # /students/{sid}/courses
    elif event["endpoint"] == "student_sid_courses":
        sid = event["pathParams"]["sid"]
        crn = None
        # check if crn provided in url querry or body
        if "crn" in event["body"].keys():
            crn = event["body"]["crn"]
        if "crn" in event["queryParams"].keys():
            crn = event["queryParams"]["crn"]
        # perform db operation
        if event["method"] == "GET":
            response = get_courses(sid)
        elif event["method"] == "PUT" or event["method"] == "POST":
            try:
                response = insert_one_course(sid, crn)
            except Exception:
                pass
        elif event["method"] == "DELETE":
            if crn is None:
                response = delete_courses(sid)
            else:
                response = delete_courses(sid, crn)
    # /students/{sid}/projects
    elif event["endpoint"] == "student_sid_projects":
        sid = event["pathParams"]["sid"]
        crn, pid = None, None
        # check if crn / pid provided in url querry or body
        if "crn" in event["body"].keys():
            crn = event["body"]["crn"]
        if "crn" in event["queryParams"].keys():
            crn = event["queryParams"]["crn"]
        if "pid" in event["body"].keys():
            crn = event["body"]["pid"]
        if "pid" in event["queryParams"].keys():
            crn = event["queryParams"]["pid"]
        # perform db operation
        if event["method"] == "GET":
            if crn is None:
                response = get_projects(sid)
            else:
                response = get_projects(sid, crn)
        elif event["method"] == "PUT" or event["method"] == "POST":
            try:
                response = insert_one_project(sid, crn, pid)
            except Exception:
                pass
        elif event["method"] == "DELETE":
            if crn is None and pid is None:
                response = delete_projects(sid)
            elif crn is None:
                response = delete_projects(sid, pid=pid)
            elif pid is None:
                response = delete_projects(sid, crn)
    
    return response

"""
---------------------- Resource Endpoints ----------------------------
"""
def get_all_students():
    response = []
    with conn.cursor() as cur:
        cur.execute("SELECT studentID FROM Students")
        for row in cur:
            response.append(row)
    conn.commit()
    response = list( map(str, response) )
    logger.info("SUCCESS: {} item(s) retrieved from DB".format(len(response)))
    return {
        'statusCode': 200,
        'body': response
    }

def get_one_student(sid):
    sql = "SELECT * FROM Students WHERE studentID = %s"
    response = None
    with conn.cursor() as cur:
        cur.execute(sql, (sid,))
        for row in cur:
            response = str(row)
            break
    conn.commit()
    if response is None:
        return {
            'statusCode': 500,
            'body': "No student with sid={} found".format(sid)
        }
    return {
        'statusCode': 200,
        'body': response
    }

def insert_one_student(sid, data):
    response = None
    sql = "INSERT INTO Students VALUES (%s, %s, %s, %s, %s);"
    first_name, last_name, email, phone, major, interests = None, None, None, None, None, None
    if "FirstName" in data.keys():
        first_name = data["FirstName"]
    if "LastName" in data.keys():
        last_name = data["LastName"]
    if "email" in data.keys():
        email = data["email"]
    if "phone" in data.keys():
        phone = data["phone"]
    if "major" in data.keys():
        major = data["major"]
    if "interests" in data.keys():
        interests = data["interests"]
    with conn.cursor() as cur:
        try:
            cur.execute(sql, (sid, first_name, last_name, email, phone, major, interests,))
            response = "{} row(s) inserted into Students table".format(cur.rowcount)
            logger.info("SUCCESS: {} row(s) inserted into Students table".format(cur.rowcount))
        except Exception as e:
            response = "Cannot insert {} into Students table".format(sid)
            logger.error("ERROR: Cannot insert {} into Students table".format(sid))
            return {
                'statusCode': 500,
                'body': str(e)
            }
    conn.commit()
    return {
        'statusCode': 200,
        'body': response
    }

def delete_one_student(sid):
    sql1 = "DELETE FROM SelectProject WHERE studentID = %s;"
    sql2 = "DELETE FROM EnrollCourse WHERE studentID = %s;"
    sql3 = "DELETE FROM Students WHERE studentID = %s;"
    with conn.cursor() as cur:
        try:
            cur.execute(sql1, (sid,))
            logger.info("SUCCESS: {} row(s) deleted from SelectProject table".format(cur.rowcount))
            cur.execute(sql2, (sid,))
            logger.info("SUCCESS: {} row(s) deleted from EnrollCourse table".format(cur.rowcount))
            cur.execute(sql3, (sid,))
            logger.info("SUCCESS: {} row(s) deleted from EnrollCourse table".format(cur.rowcount))
            response = "{} deleted from Students table".format(sid)
        except Exception as e:
            logger.error("ERROR: Cannot delete {} from Students table".format(sid))
            return {
                'statusCode': 500,
                'body': str(e)
            }
    conn.commit()
    return {
        'statusCode': 200,
        'body': response
    }

def get_courses(sid):
    sql = "SELECT CRN from EnrollCourse WHERE studentID = %s;"
    response = []
    with conn.cursor() as cur:
        cur.execute(sql, (sid,))
        for row in cur:
            response.append(row)
    conn.commit()
    logger.info("SUCCESS: {} item(s) retrieved from DB".format(len(response)))
    response = list( map(str, response) )
    return {
        'statusCode': 200,
        'body': response
    }

def insert_one_course(sid, crn):
    sql = "INSERT INTO EnrollCourse VALUES (%s, %s);"
    response = None
    with conn.cursor() as cur:
        try:
            cur.execute(sql, (sid, crn,))
            logger.info("SUCCESS: {} row(s) inerted into EnrollCourse table".format(cur.rowcount))
            response = "({}, {}) inserted into EnrollCourse table".format(sid, crn)
        except Exception as e:
            logger.error("ERROR: Cannot insert ({}, {}) into EnrollCourse table".format(sid, crn))
            return {
                'statusCode': 500,
                'body': str(e)
            }
    conn.commit()
    return {
        'statusCode': 200,
        'body': response
    }

def delete_courses(sid, crn=None):
    if crn is None:
        sql = "DELETE FROM EnrollCourse WHERE studentID = %s;"
    else:
        sql = "DELETE FROM EnrollCourse WHERE studentID = %s and CRN = %s;"
    response = None

    response = delete_projects(sid, crn)
    if response['statusCode'] == 500:
        return response

    with conn.cursor() as cur:
        try:
            if crn is None:
                cur.execute(sql, (sid,))
            else:
                cur.execute(sql, (sid, crn,))
            logger.info("SUCCESS: {} row(s) deleted from EnrollCourse table".format(cur.rowcount))
            response = "{} deleted from EnrollCourse table".format(sid)
        except Exception as e:
            logger.error("ERROR: Cannot delete {} from EnrollCourse table".format(sid))
            return {
                'statusCode': 500,
                'body': str(e)
            }
    conn.commit()
    return {
        'statusCode': 200,
        'body': response
    }

def get_projects(sid, crn=None):
    if crn is None:
        sql = "SELECT projectID from SelectProject WHERE studentID = %s;"
    else:
        sql = "SELECT projectID from SelectProject WHERE studentID = %s and CRN = %s;"
    response = []
    with conn.cursor() as cur:
        if crn is None:
            cur.execute(sql, (sid,))
        else:
            cur.execute(sql, (sid, crn,))
        for row in cur:
            response.append(row)
    conn.commit()
    logger.info("SUCCESS: {} item(s) retrieved from DB".format(len(response)))
    response = list( map(str, response) )
    return {
        'statusCode': 200,
        'body': response
    }

def insert_one_project(sid, crn, pid):
    sql = "INSERT INTO SelectProject VALUES (%s, %s, %s);"
    response = None
    with conn.cursor() as cur:
        try:
            cur.execute(sql, (sid, crn, pid,))
            logger.info("SUCCESS: {} row(s) inerted into SelectProject table".format(cur.rowcount))
            response = "({}, {}, {}) inserted into SelectProject table".format(sid, crn, pid)
        except Exception as e:
            logger.error("ERROR: Cannot insert ({}, {}, {}) into SelectProject table".format(sid, crn, pid))
            return {
                'statusCode': 500,
                'body': str(e)
            }
    conn.commit()
    return {
        'statusCode': 200,
        'body': response
    }

def delete_projects(sid, crn=None, pid=None):
    response = None
    with conn.cursor() as cur:
        try:
            if crn is None and pid is None:
                cur.execute("DELETE FROM SelectProject WHERE studentID = %s;", (sid,))
            elif pid is None:
                cur.execute("DELETE FROM SelectProject WHERE studentID = %s and CRN = %s;", (sid, crn,))
            elif crn is None:
                cur.execute("DELETE FROM SelectProject WHERE studentID = %s and projectID = %s;", (sid, pid,))
            else:
                cur.execute("DELETE FROM SelectProject WHERE studentID = %s and CRN = %s and projectID = %s;", (sid, crn, pid,))
            logger.info("SUCCESS: {} row(s) deleted from EnrollCourse table".format(cur.rowcount))
            response = "{} deleted from EnrollCourse table".format(sid)
        except Exception as e:
            logger.error("ERROR: Cannot delete {} from EnrollCourse table".format(sid))
            return {
                'statusCode': 500,
                'body': str(e)
            }
    conn.commit()
    return {
        'statusCode': 200,
        'body': response
    }