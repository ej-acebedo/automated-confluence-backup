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
    
    account,username,token = parameter_values
    
    # Open new session for cookie persistence and auth.
    auth_header = urllib3.util.make_headers(basic_auth=f"{username}:{token}")
    headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                }
    headers.update(auth_header)
    
    # Create the full base url for the JIRA instance using the account name.
    url = 'https://' + account + '.atlassian.net/wiki'
    
    progress = get_backup_progress(url,headers)
    
    return progress

def get_backup_progress(url,headers):
    file_name = 'None'
    # If no file name match in JSON response keep outputting progress every 10 seconds
    
    progress = http.request('GET', url + '/rest/obm/1.0/getprogress', headers=headers)
    
    return json.loads(progress.data)
            
def get_parameter(parameter):
    
    response = ssm.get_parameter(Name=parameter)
    parameter_value = response['Parameter']['Value']
    
    return parameter_value