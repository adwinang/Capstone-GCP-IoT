import mysql.connector
from flask import escape
from flask import jsonify

mydb = mysql.connector.connect(
        host="35.240.247.84",
        user="cloudfunction",
        password="Pa$$w0rd"
        )

mycursor = mydb.cursor(buffered=True)
mycursor.execute("USE ip")

def get_db(request):
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
        if request_json and 'device_id' and 'registry_id' in request_json:
            device_id = request_json['device_id']
            registry_id = request_json['registry_id']
            ip = execute_db(device_id, registry_id)

            response = jsonify(ip)
            headers = {
                'Access-Control-Allow-Origin': '*'
            }

            return response, 200, headers

        else:
            return 500
    
    else:
        return 500

def execute_db(device_id, registry_id):
    sql = "SELECT * FROM ip WHERE device_id = %s AND registry_id = %s"
    val = (device_id, registry_id)
    mycursor.execute(sql, val)
    
    ip = ""

    for row in mycursor.fetchall():
        ip = row[2]

    return ip

