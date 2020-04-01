# nero-sftp-migration
A utility on nero to migrate files from a remote sftp server to localhost


This script on nero requires:

pip install --user paramiko
pip install --user requests
pip install --user pytz

It uses the REDCap Email api to push an email when new files are detected.

It also requires a file called creds.py in the format:
```
username=""
hostname=""
password=""
email_token=""
email_endpoint=""
email_to=""
email_from=""
dest_dir="Where to put them when pulled"
source_dir="Dir on sftp server where files are located"
```