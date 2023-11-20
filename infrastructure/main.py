import boto3
import os
import json
import base64

# Initialize Boto3 EC2 resource and client
ec2_resource = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
iam = boto3.client('iam')

# Create a VPC
vpc = ec2_resource.create_vpc(CidrBlock='10.0.0.0/16')
vpc.wait_until_available()
print(f"VPC Created: {vpc.id}")
# Enable DNS hostnames and support for the VPC
vpc.modify_attribute(EnableDnsHostnames={'Value': True})
vpc.modify_attribute(EnableDnsSupport={'Value': True})

# Create a subnet
subnet = ec2_resource.create_subnet(CidrBlock='10.0.1.0/24', VpcId=vpc.id)
print(f"Subnet Created: {subnet.id}")
# Modify subnet to assign public IPs by default
ec2_client.modify_subnet_attribute(
    SubnetId=subnet.id,
    MapPublicIpOnLaunch={'Value': True}
)
print(f"Modified Subnet to Assign Public IPs by Default: {subnet.id}")

# Create an Internet Gateway and attach to the VPC
igw = ec2_resource.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=igw.id)
print(f"Internet Gateway Created and Attached: {igw.id}")

# Create a Route Table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=igw.id)
print(f"Route Table Created: {route_table.id}")

# Associate the Route Table with the subnet
route_table.associate_with_subnet(SubnetId=subnet.id)

# Create a Security Group
security_group = ec2_resource.create_security_group(
    GroupName='MySecurityGroup',
    Description='My security group',
    VpcId=vpc.id
)
security_group.authorize_ingress(
    IpPermissions=[
        {
            'IpProtocol': '-1',
            'FromPort': -1,
            'ToPort': -1,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)
print(f"Security Group Created: {security_group.id}")

# Create a key pair
key_pair = ec2_client.create_key_pair(KeyName='MyKeyPair')
private_key = key_pair['KeyMaterial']

# Save the private key to a file
with open('MyKeyPair.pem', 'w') as file:
    file.write(private_key)
print("Key Pair Created and Saved: MyKeyPair.pem")

# Set file permissions (Linux/Mac OS)
os.chmod('MyKeyPair.pem', 0o400)

images = ec2_client.describe_images(
    Filters=[
        {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*']},
        {'Name': 'architecture', 'Values': ['x86_64']},
        {'Name': 'root-device-type', 'Values': ['ebs']}
    ],
    Owners=['099720109477']
)

# Sort the images by creation date and pick the latest
images = sorted(images['Images'], key=lambda x: x['CreationDate'], reverse=True)
latest_ubuntu_ami = images[0]['ImageId'] if images else None

if latest_ubuntu_ami:
    print(f"Latest Ubuntu AMI ID: {latest_ubuntu_ami}")
else:
    print("No Ubuntu AMI found")
    exit(1)  # Exit if no AMI found

# Describe the AMI to find the correct DeviceName for Block Device Mapping
ami_info = ec2_client.describe_images(ImageIds=[latest_ubuntu_ami])
block_device_mappings = ami_info['Images'][0]['BlockDeviceMappings']

# Assuming the first block device mapping is for the root device
root_device_name = block_device_mappings[0]['DeviceName']

# User data script to ensure SSM Agent is installed and running (in order to use .send_command on ubuntu instances)
user_data_script = """#!/bin/bash
sudo snap install amazon-ssm-agent --classic
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
"""
# Encode user data script
user_data_encoded = base64.b64encode(user_data_script.encode()).decode()

# Fetch the ARN of the existing IAM role
role_arn = iam.get_role(RoleName='LabRole')['Role']['Arn']

# Launch an EC2 instance with a specified EBS volume size
instances = ec2_resource.create_instances(
    ImageId=latest_ubuntu_ami,
    InstanceType='m4.large',
    MaxCount=5,
    MinCount=1,
    KeyName='MyKeyPair',
    UserData=user_data_encoded,
    IamInstanceProfile={'Arn': 'arn:aws:iam::308167270751:instance-profile/LabInstanceProfile'},
    NetworkInterfaces=[{
        'SubnetId': subnet.id,
        'DeviceIndex': 0,
        'AssociatePublicIpAddress': True,
        'Groups': [security_group.group_id]
    }],
    BlockDeviceMappings=[
        {
            'DeviceName': root_device_name,
            'Ebs': {
                'VolumeSize': 32,  # Size in GB
                'DeleteOnTermination': True,
                'VolumeType': 'gp2',  # General Purpose SSD
            },
        },
    ],
)

instance_data = []

# Wait for instances to run, assign names, and collect their details
for i, instance in enumerate(instances, start=1):
    instance.wait_until_running()
    instance.load()

    if i <= 4:
        instance_name = f'worker{i}'
    else:
        instance_name = 'orchestrator'

    instance.create_tags(Tags=[{'Key': 'Name', 'Value': instance_name}])

    instance_info = {
        'Name': instance_name,
        'InstanceID': instance.id,
        'PublicDNS': instance.public_dns_name,
        'PublicIP': instance.public_ip_address
    }
    instance_data.append(instance_info)

    print(f"Instance {i} Created: {instance.id}")
    print(f"Instance {i} Public DNS: {instance.public_dns_name}")
    print(f"Instance {i} Public IP: {instance.public_ip_address}")

# Write the instance data to a JSON file
with open('instance_details.json', 'w') as file:
    json.dump(instance_data, file, indent=4)

print("Instance details saved to instance_details.json")

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)
def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

instance_details_data = load_json('instance_details.json')
workers_data = load_json('../orchestrator/workers.json')

for i, worker in enumerate(workers_data):
    dns = instance_details_data[i%4]['PublicDNS']
    container_i = f"container{i+1}"
    workers_data[container_i]['ip'] = dns
# Save the updated data back to workers.json
save_json(workers_data, '../orchestrator/workers.json')
print("Workers json file has been updated with infra PublicDNSs.")
