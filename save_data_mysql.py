from flask import Flask, request
from flask_cors import CORS
import webbrowser
import subprocess
import pymysql

app = Flask(__name__)
CORS(app)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print(data)
    currentTime = data['currentTime']
    temperature = data['temperature']
    humidity = data['humidity']

# 先创建一个数据库和表，你可以使用以下的SQL命令来创建一个名为weather_data的数据库：
# CREATE DATABASE weather_data;

# 你可以使用以下的SQL命令来创建一个包含currentTime、temperature和humidity字段的表：
# CREATE TABLE temp_table (
#     currentTime VARCHAR(255),
#     temperature FLOAT,
#     humidity FLOAT
# );

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='pofice',
                                 password='your_password',
                                 db='weather_data')

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `temp_table` (`currentTime`, `temperature`, `humidity`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (currentTime, temperature, humidity))

        # connection is not autocommit by default. So you must commit to save your changes.
        connection.commit()

    finally:
        connection.close()

    return 'OK'

if __name__ == '__main__':
    subprocess.Popen(["python", "-m", "http.server", "4090"])
    url = "http://localhost:4090/tf.html"
    webbrowser.open(url)
    app.run(port=5000)