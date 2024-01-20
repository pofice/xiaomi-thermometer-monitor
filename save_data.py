from flask import Flask, request
from flask_cors import CORS
import matplotlib.pyplot as plt
import webbrowser
import time
import subprocess
import json
app = Flask(__name__)
CORS(app)

data_list = []

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print(data)
    currentTime = data['currentTime']
    temperature = data['temperature']
    humidity = data['humidity']
    
    data_list.append({'currentTime': currentTime, 'temperature': temperature, 'humidity': humidity})

    # Save data to file
    with open('data.json', 'a') as file:
        json.dump(data_list[-1], file)
        file.write('\n')

    return 'OK'

if __name__ == '__main__':
    subprocess.Popen(["python", "-m", "http.server", "4090"])
    url = "http://localhost:4090/tf.html"
    webbrowser.open(url)
    app.run(port=5000)
