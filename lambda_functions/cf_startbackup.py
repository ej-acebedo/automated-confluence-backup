import urllib3
import json
import os
import boto3


CF_SITENAME = os.environ["CF_SITENAME"]
CF_EMAIL = os.environ["CF_EMAIL"]
CF_TOKEN = os.environ["CF_TOKEN"]
attachments = "y"

ssm = boto3.client('ssm')
http = urllib3.PoolManager()

def lambda_handler(event, context):
    
    parameter_names = [CF_SITENAME, CF_EMAIL, CF_TOKEN]
    
    parameter_values = map(get_parameter, parameter_names)
    
    site,user_name,api_token = parameter_values
    
    #Run backup
    conf_backup(account=site, 
            username=user_name, 
            token=api_token, 
            attachments=attachments
            )

def conf_backup(account, username, token, attachments):

    
    auth_header = urllib3.util.make_headers(basic_auth=f"{username}:{token}")
    headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                }
    headers.update(auth_header)
    
    # Create the full base url for the JIRA instance using the account name.
    url = 'https://' + account + '.atlassian.net/wiki'

    # Set json data to determine if backup to include attachments.
    if attachments in ('Y', 'y'):
        json_data = {"cbAttachments": "true", "exportToCloud": "true"}
    elif attachments in ('N', 'n'):
        json_data = {"cbAttachments": "false", "exportToCloud": "true"}
        
    # Start backup
    backup_response = http.request('POST', url + '/rest/obm/1.0/runbackup', 
                                   body=json.dumps(json_data).encode('utf-8'), 
                                   headers=headers
                                  )
    # Check backup startup response is 200 if not print error and exit.
    if backup_response.status != 200:
        print(backup_response.data)
        print("err")
        exit(1)
    else:
        print('Backup starting...')

def get_parameter(parameter):
    
    response = ssm.get_parameter(Name=parameter)
    parameter_value = response['Parameter']['Value']
    
    return parameter_value