import json
import sys
import logging
import pymysql
import rds_config


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# config db info
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

def lambda_handler(event, context):
    response = []
    with conn.cursor() as cur:
        cur.execute("SELECT * from Students")
        for row in cur:
            response.append(row)
    conn.commit()
    logger.info("SUCCESS: {} item(s) retrieved from DB".format(len(response)))
    
    return {
        'statusCode': 200,
        'body': json.dumps(str(response))
    }

'''
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(str(event))
    }
'''