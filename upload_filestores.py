import json
import requests
import os
import sys
import csv
import subprocess
import getpass
import pathlib

import argparse
import time
from typing import NamedTuple
from datetime import timedelta



class Args(NamedTuple):
    """ Command-line arguments """
    url: str
    deploy: str


def get_args() -> Args:

    """ Get command-line arguments """

    parser = argparse.ArgumentParser(
        description='Script for generating backups',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)


    parser.add_argument('url',
                        metavar='url',
                        help='url of the service')

    parser.add_argument('deploy',
                        metavar='deploy',
                        help='name of the deploy')

    args = parser.parse_args()


    return Args(args.url, args.deploy)


def get_list_db(url):
    action_url = "http://{}/web/database/list".format(url)
    data = {"params": {}}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(action_url, data=json.dumps(data), headers=headers)
        db = response.json()
    except Exception as e:
        print("URL:", url)
        print("Connection establishment failed!")
        print(e)
        print("------------------------------")
        db = {"error": e}

    return db


def filestore_db_odoo(deployment_name, db_name):

    try:
        subprocess.check_output('sh generate_filestore.sh {} {}'.format(deployment_name, db_name),shell=True).decode('utf-8')

    except Exception as e:
        print("Error generating filestores files: ")
        print(e)




def upload_filestore_to_s3(list_db, data):
    deploy = data['deploy']
    for db in list_db:
        print('DATABASE:', db)
        filestore_db_odoo(deploy,db)
        print('Successfully uploaded to s3')
        print('-'*20)



def generate_filestore(url, deploy):

    current_user = getpass.getuser()
    file_route = "/home/{0}/backup/".format(current_user)

    if not pathlib.Path(file_route).exists():
        os.system("mkdir /home/{0}/backup/".format(current_user))

    data = {
        'deploy': deploy,
        'directory': '/home/{0}/backup/'.format(current_user)
    }

    db = get_list_db(url)
    if db.get('error'):
        print('¡CONNECTION PROBLEM!\n Review data and try again.')
    else:
        list_db = db['result']
        print('DEPLOY:', data['deploy'])
        upload_filestore_to_s3(list_db, data)



def main():

    args = get_args()
    url, deploy = args.url, args.deploy


    try:

        generate_filestore(url,deploy)

    except Exception as e:
        print("Error: ")
        print(e)
        print('-------------------------------------')


if __name__ == '__main__':
    main()
