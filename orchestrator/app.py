from flask import Flask, request, jsonify
import requests
import threading
import json
import time

app= Flask(__name__)
lock = threading.Lock()
request_queue = []

def send_request_to_container(container_id, container_info):
    # code to call instance, should get the ip, port, send the request to it
    ip_address =container_info['ip']
    port = container_info['port']
    url = f"http://{ip_address}:{port}/run_model"
    print(url)
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("Request was successful.")
            print("Response content:")
            print(response.text)
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed with an error: {e}")

def update_container_status(container_id, status):
    with lock:
        with open('workers.json', 'r') as f:
            data = json.load(f)
        data[container_id]['status'] = status
        with open('workers.json', 'w') as f:
            json.dump(data, f)


def process_request():
    with lock:
        with open('workers.json', 'r') as f:
            data = json.load(f)
    free_container = None
    for container_id, container_info in data.items():
        if container_info['status'] == 'free':
            free_container = container_id
            break
    if free_container:
        update_container_status(free_container, 'busy')
        send_request_to_container(free_container, data[free_container])
        update_container_status(free_container, 'free')
    else:
        request_queue.append("incoming_request_data")


@app.route('/mew_request', methods=['GET'])
def new_request():
    threading.Thread(target=process_request, args=()).start()
    return jsonify({"message": "Request received and processing started."})


if __name__ == "__main__":
    app.run(port=80)