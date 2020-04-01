#!/usr/bin/env python
# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.
# based on code provided by raymond mosteller (thanks!)
import base64
import getpass
import os
import socket
import sys
import traceback
import paramiko
import datetime
from paramiko.py3compat import input
# Get the credentials - expecting username, password, and hostname
from creds import username, password, hostname
# setup logging
paramiko.util.log_to_file("sftp.log")
# Paramiko client configuration
Port = 22
# get hostname
if hostname == "":
    hostname = input("Hostname: ")
if len(hostname) == 0:
    print("*** Hostname required.")
    sys.exit(1)
# get username
if username == "":
    username = input("Username: ")
if len(username) == 0:
    print("*** Username required.")
    sys.exit(1)
# Set port
if hostname.find(":") >= 0:
    hostname, portstr = hostname.split(":")
    Port = int(portstr)
# now, connect and use paramiko Transport to negotiate SSH2 across the connection
try:
    hostkey = None
    t = paramiko.Transport((hostname, Port))
    t.connect(
        hostkey,
        username,
        password
    )
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.chdir("OUTBOUND");
    
    # List of files on server
    files = sftp.listdir(".")
    
    # Log file to determine most recent check
    check_file_name = 'checks.txt'
    
    # Create current time in format yyyy-mm-dd_hh_mm
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M')
    
    # save single file with date/ts of last check of remote server
    with open(check_file_name, 'a+') as fp:
        fp.write(current_datetime+'\n')

    if len(files) != 0:
        #There are new files, Create directory to store data
        if(not os.path.isdir('./'+current_datetime)):
            os.mkdir('./'+current_datetime)

        #iterate through files, add and remove
        for filename in files:
            sftp.get('./' + filename, './' +current_datetime + '/' + filename)
            #sftp.remove('./'+filename)
        
    t.close()
except Exception as e:
    print("*** Caught exception: %s: %s" % (e.__class__, e))
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)
