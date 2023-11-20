import requests

# Endpoint URL
url = 'http://ec2-44-197-199-40.compute-1.amazonaws.com:80/new_request'

# Number of requests to send
num_requests = 500

def send_requests(url, num_requests):
    for i in range(num_requests):
        response = requests.get(url)
        print(f'Request {i+1}: Status Code: {response.status_code}, Response: {response.text}')

# Calling the function to send requests
send_requests(url, num_requests)
