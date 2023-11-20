from flask import Flask, request, jsonify
import requests
import threading
import json
import time
import uuid

app = Flask(__name__)
lock = threading.Lock()
request_queue = []
responses = {}  # Dictionary to store responses

def send_request_to_container(container_id, container_info, request_id):
    # Code to call instance, get the IP and port, send the request to it
    ip_address = container_info['ip']
    port = container_info['port']
    url = f"http://{ip_address}:{port}/run_model"
    print(url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Request was successful.")
            print("Response content:")
            print(response.text)
            with lock:
                responses[request_id] = response.text  # Store the response
        else:
            print(f"Request failed with status code: {response.status_code}")
            with lock:
                responses[request_id] = f"Request failed with status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        print(f"Request failed with an error: {e}")
        with lock:
            responses[request_id] = f"Request failed with an error: {e}"

def update_container_status(container_id, status):
    with lock:
        with open('workers.json', 'r') as f:
            data = json.load(f)
        data[container_id]['status'] = status
        with open('workers.json', 'w') as f:
            json.dump(data, f)

def process_request(request_id):
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
        send_request_to_container(free_container, data[free_container], request_id)
        update_container_status(free_container, 'free')
    else:
        request_queue.append("incoming_request_data")

@app.route('/new_request', methods=['GET'])
def new_request():
    request_id = str(uuid.uuid4())  # Generate a unique request ID
    threading.Thread(target=process_request, args=(request_id,)).start()

    # Wait for the response to be available
    while request_id not in responses:
        time.sleep(0.1)

    # Retrieve and return the response
    response = responses.pop(request_id)  # Remove the response from the dictionary
    return jsonify({"message": "Request processed.", "response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)