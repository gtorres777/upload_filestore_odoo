#!/bin/bash


deployment_name="$1"
if [ -z "$deployment_name" ]; then
    echo "ERROR: No clients directory passed" exit 1
fi


### Database name parameter that must be given to the script to generate the filestore backup of the database given ###
database="$2"
if [ -z "$database" ]; then
    echo "ERROR: No database"
    exit 1
fi

echo $deployment_name
echo $database

### Enviroment Variables needed to run the odoo-backup script ###
### that most of them are found in the .env file of the project ###
if [ -z "$HOME" ]; then
    echo "ERROR: Instalation error, HOME is not defined"
    exit 1
fi


### Placing us on the backup directory and sending data to the logfile ###
mkdir -p $HOME/backup
cd $HOME/backup




### Generating the filestore backup file for the given database name ###
echo -n "Backup filestore: $ODOO_DATA_DIR/filestore/$database ... "
/bin/tar -C "$ODOO_DATA_DIR/filestore/" -czf "$HOME/backup/${database}_filestore.tar.gz" $database
error=$?
if [ $error -eq 0 ]; then echo "OK"; else echo "ERROR: $error"; fi


### uploading the compressed filestore backup files  to the filestores-odoo-prod s3 bucket in AWS ###
aws s3 cp *.gz s3://filestores-odoo-prod/$deployment_name/$database/ --acl public-read
error=$?
if [ $error -eq 0 ]; then echo "Successfully uploaded to S3"; else echo "ERROR: $error"; fi

### uploading the compressed filestore backup files  to the filestores-odoo-prod s3 bucket in AWS ###
rm *
error=$?
if [ $error -eq 0 ]; then echo "clean up"; else echo "ERROR: $error"; fi
