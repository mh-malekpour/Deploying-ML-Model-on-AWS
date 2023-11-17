import boto3
import json
import time


# Initialize the SSM client
ssm_client = boto3.client('ssm')

# Specify the instance IDs
with open('instance_details.json', 'r') as file:
    instance_details = json.load(file)

instance_ids = []
for instance in instance_details:
    if instance['Name'] != 'orchestrator':
        instance_ids.append(instance['InstanceID'])

# Function to read a script file
def read_script(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# # Read your bash scripts
# script1 = read_script('./scripts/install_docker.sh')
# script2 = read_script('./scripts/deploy_worker_app.sh')

commands = [
    # Install docker
    'sudo apt-get update',
    'sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common',
    'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -',
    'sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"',
    'sudo apt-get update',
    'apt-cache policy docker-ce',
    'sudo apt-get install -y docker-ce',
    'sudo usermod -aG docker ubuntu',
    'sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose',
    'sudo chmod +x /usr/local/bin/docker-compose',
    # Deploy worker
    'cd /home/ubuntu && git clone https://github.com/mh-malekpour/Deploying-ML-Model-on-AWS.git',
    'cd /home/ubuntu/Deploying-ML-Model-on-AWS/worker && sudo docker-compose up --build'
]

def send_command(instance_ids, command):
    response = ssm_client.send_command(
        InstanceIds=instance_ids,
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [command]},
    )
    return response['Command']['CommandId']

def check_command_status(command_id, instance_id):
    for _ in range(10):  # Try up to 10 times with a delay in between
        try:
            response = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )
            if response['Status'] != 'InProgress':
                return response
        except ssm_client.exceptions.InvocationDoesNotExist:
            print(f"Waiting for command {command_id} to be registered in SSM...")
        time.sleep(10)  # Wait for 10 seconds before checking again

    return {"Status": "Failed", "StatusDetails": "Invocation does not exist or check exceeded retries"}


# Flag to track if any command fails
any_command_failed = False

# Execute each command and check its status
for command in commands:
    if any_command_failed:
        break  # Stop executing further commands if one has already failed

    command_id = send_command(instance_ids, command)
    if 'docker-compose up' in command:
        print("running docker-compose up on instances")
        break

    for instance_id in instance_ids:
        status = check_command_status(command_id, instance_id)
        print(f"Status for instance {instance_id} on command '{command}': {status['Status']}, {status['StatusDetails']}")
        if status['Status'] != 'Success':
            print(f"Command execution failed on instance {instance_id} for command '{command}'")
            any_command_failed = True
            break  # Stop executing further commands on this instance