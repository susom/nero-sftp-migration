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
import requests
import datetime
import pytz
from paramiko.py3compat import input

# Get the credentials - expecting username, password, and hostname
from creds import username, password, hostname, \
    email_token, email_endpoint, email_from, \
    default_dir, source_dir, prefix_list

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
    sftp.chdir(source_dir)
    
    # List of files on server
    files = sftp.listdir(".")
    
    
    # Log file to determine most recent check
    check_file_name = "last_check.txt"
    log_file_name = "sftp_checks.log"

    # Create current time in format yyyy-mm-dd_hh_mm
    # Server is currently returning UTC
    pst = pytz.timezone('US/Pacific')
    current_datetime = datetime.datetime.now(pst).strftime("%Y-%m-%d_%H_%M")

    # save single file with date/ts of last check of remote server
    with open(check_file_name, "w+") as fp:
        fp.write(current_datetime+"\n")

    #update check_file with newest date in each destination dir
    folders = list(map(lambda x: x['destination'], prefix_list)) + [default_dir]
    
    for folder in folders:
        if not os.path.isdir(folder):
            os.makedirs(folder)
        with open(folder + "/" + check_file_name, "w+") as fp:
            fp.write(current_datetime+"\n")

    if len(files) != 0:
        # iterate through files, add and remove
        for filename in files:
            #check if match in prefix list
            tokenize = filename.split("_")[0]
            
            #get destination path if token matches one of the prefixes
            prefix_strings = list(map(lambda x: x['destination'] if tokenize == x['prefix'] else None, prefix_list))
            
            #filter all Nonetypes from map
            filtered_path = [x for x in prefix_strings if x is not None]


            if filtered_path:
                dest_path = filtered_path[0] + "/" + current_datetime
                email = next((x['email'] for x in prefix_list if x['destination'] == filtered_path[0]), None)
            else:
                dest_path = default_dir + "/" + current_datetime
                email = None
            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)
            
            sftp.get("./" + filename, dest_path + "/" + filename)
            sftp.remove("./"+filename)

            # Notify someone that new data exists
            if(email):
                r = requests.post(email_endpoint, data={
                    "email_token": email_token,
                    "to": email,
                    "from_name": "Nero Batch Script",
                    "from_email": email_from,
                    "subject": "New Files Available: " + current_datetime,
                    "body": "New files were just obtained for your project.  They can be found at " +
                            "https://nero.compute.stanford.edu in the directory:\n\n\t" + dest_path
                })

    # also save a log
    with open("./" + log_file_name, "a+") as fp:
        fp.write("[" + current_datetime + "] Found " + str(len(files)) + " files" + "\n")

    t.close()
except Exception as e:
    print("*** Caught exception: %s: %s" % (e.__class__, e))
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)

    