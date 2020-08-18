
import mysql.connector
from flask import escape

mydb = mysql.connector.connect(
        host="35.240.247.84",
        user="cloudfunction",
        password="Pa$$w0rd"
        )

mycursor = mydb.cursor(buffered = True)

mycursor.execute("USE ip")

def post_db(request):
    content_type = request.headers['content-type']

    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

        return ('', 204, headers)

    elif content_type == 'application/json':
        request_json = request.get_json(silent=True)
        if request_json and 'device_id' and 'registry_id' and'ip' in request_json:
            device_id = request_json['device_id']
            registry_id = request_json['registry_id']
            ip = request_json['ip']

            status = execute_db(device_id, registry_id, ip)    
            
            if status == True:
                return "OK", 200
            
            else:
                return "Error", 500

        else:
            raise ValueError("JSON is invalid, missing device_id and/or ip properties")
            return "Error", 500
    else:
        raise ValueError("Unknown content type. Please send in JSON.")
        return "Error", 500
        
def execute_db(device_id, registry_id, ip):
    sql = "SELECT * FROM ip WHERE device_id = %s AND registry_id = %s"
    val = (device_id, registry_id)
    mycursor.execute(sql, val)

    if mycursor.rowcount == 0:
        try:
            sql = "INSERT INTO ip (device_id, registry_id, ip) VALUES (%s, %s, %s)"
            val = (device_id, registry_id, ip)

            mycursor.execute(sql,val)
            mydb.commit()

            return True
        
        except:
            return False

    else:
        try:
            sql = "UPDATE ip SET ip = %s WHERE device_id = %s AND registry_id = %s"
            val = (ip, device_id, registry_id)

            mycursor.execute(sql,val)
            mydb.commit()
        
            return True

        except:
            return False

