import urllib3
import json
import os

site = os.environ["CF_SITENAME"]
username = os.environ["CF_EMAIL"]
token = os.environ["CF_TOKEN"]
attachments = "y"
folder = "./"
http=urllib3.PoolManager()
url = 'https://' + site + '.atlassian.net'
#Build headers
auth_header = urllib3.util.make_headers(basic_auth=f"{username}:{token}")
headers = {
              "Accept": "application/json",
              "Content-Type": "application/json",
            }
headers.update(auth_header)

def download_backup():
    confluence_backup_path = _get_backup_location()
    filename = site + '_conf_backup' + '.zip'
    #Start download
    with http.request('GET', url + '/wiki/download/' + confluence_backup_path , headers=headers, preload_content=False) as response:
    # print(file.headers)
      total_size = int(response.headers.get('Content-Length', 0))
      print(total_size)
      block_size = 4096
      bytes_written = 0

      with open(folder + filename, 'wb') as out_file:
         while True:
          data = response.read(block_size)
          if not data:
            break
          out_file.write(data)   
          bytes_written += len(data)
          progress = bytes_written / total_size * 100
          
          print(f'Progress: {progress:.2f}%')

      return filename

def _get_backup_location():
  response = http.request('GET', url + '/wiki/rest/obm/1.0/getprogress', headers=headers)
  progress_req = _http_response_to_json(response.data)

  try:
    backup_location = progress_req['fileName']
    print(backup_location)
  except KeyError:
    print(progress_req)
    exit(1)

  return backup_location

def _http_response_to_json(http_response):
  response_string = http_response.decode('utf-8')
  http_response_json = json.loads(response_string)
  return http_response_json

download_backup()