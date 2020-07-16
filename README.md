# nero-sftp-migration
A utility on nero to migrate files from a remote sftp server to localhost

This script will route files based on prefix to any supplied destination, creating a new folder based on timestamp with the matching files.

This script on nero requires:

- `pip install --user paramiko`
- `pip install --user requests`
- `pip install --user pytz`

It uses the REDCap Email api to push an email when new files are detected.

It also requires a file called creds.py in the format:
```python
# Example creds.py

# Remote server info
username="user1" 
password="test"
hostname="0.0.0.0"

# Email info
email_token="123456789"
email_endpoint="redcap.stanford.edu"
email_from="jmschult@stanford.edu"

# Directory to put items that do not match a given prefix
default_dir="shared" 

# Directory where files are going to be pulled from
source_dir="files/api"

# Default email that is used when no prefix matches are found
default_email='abc@gmail.com'

# Array that contains an Object entry for each prefix match case
prefix_list = [
    {
        "prefix": "kuth", #Route all files with this prefix to <destination>
        "destination": "kuth1253",
        "email": "kuth@gmail.com"
    },
    {
        "prefix": "rand",
        "destination": "randtab/var/shared/files",
        "email": "" # Leave email empty to prevent sending a request per check
    },
    ...
]
```
**Note: The prefix is case sensitive and should be separated from the filename by an underscore**
 - **E.g**: `kuth_apidoc.txt`

