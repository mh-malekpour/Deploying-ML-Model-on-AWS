# import boto3
# import json
# import time
#
# # Initialize the SSM Client
# ssm_client = boto3.client('ssm')
#
# # Specify the instance IDs
# with open('instance_details.json', 'r') as file:
#     instance_details = json.load(file)
#
# instance_ids = []
# for instance in instance_details:
#     if instance['Name'] != 'orchestrator':
#         instance_ids.append(instance['InstanceID'])
#
# # Example command - replace with your actual command
# my_command = "echo Hello World"
#
# # Sending command to each instance
# for instance_id in instance_ids:
#     response = ssm_client.send_command(
#         InstanceIds=[instance_id],
#         DocumentName="AWS-RunShellScript",
#         Parameters={'commands': [my_command]}
#     )
#
#     # Getting the command ID
#     command_id = response['Command']['CommandId']
#
#     # Adding a delay
#     time.sleep(5)  # Adjust the delay as needed
#
#     try:
#         # Fetching the output
#         output = ssm_client.get_command_invocation(
#             CommandId=command_id,
#             InstanceId=instance_id
#         )
#         print(output)
#     except botocore.exceptions.ClientError as error:
#         if error.response['Error']['Code'] == 'InvocationDoesNotExist':
#             print(f"Invocation does not exist for CommandId: {command_id}, InstanceId: {instance_id}")
#         else:
#             raise
#
# # import boto3
# #
# # # Initialize the IAM client
# # iam = boto3.client('iam')
# #
# # # Fetch the ARN of the role
# # role_arn = iam.get_role(RoleName='LabRole')
# #
# # # Print the ARN
# # print(f"The ARN of the role is: {role_arn}")
#
# #
# # role_name = 'LabRole'
# # instance_profile_name = 'LabInstanceProfile'
# #
# # # Check if the instance profile exists, create if it doesn't
# # try:
# #     iam.get_instance_profile(InstanceProfileName=instance_profile_name)
# #     print("Instance profile already exists.")
# # except iam.exceptions.NoSuchEntityException:
# #     iam.create_instance_profile(InstanceProfileName=instance_profile_name)
# #     iam.add_role_to_instance_profile(
# #         InstanceProfileName=instance_profile_name,
# #         RoleName=role_name
# #     )
# #     print("Instance profile created and role added.")
# #
# # # Fetch the instance profile ARN
# # instance_profile_arn = iam.get_instance_profile(InstanceProfileName=instance_profile_name)['InstanceProfile']['Arn']
# # print(instance_profile_arn)
#


for i in range(5):
    if i > 3:
        pass
    print(i)
#
