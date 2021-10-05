#/bin/bash

# Reading last_pr_export_ts.txt, running private changeset extract and saves last run timestamp 
# Make sure 'last_pr_export_ts.txt' file exists with the start date e.g. 2020-04-07_01:00:00 
# Make sure env. var.OSM_FOLDER, FOLDERNAME_PR_EXPORT. HOSTNAME, DATABASE, USERNAME and PASSWORD are set prior to running the script 
# Example using export set: OSM_FOLDER="/home/ubuntu/openstreetmap-website/" 
# Example using export set: FOLDERNAME_PR_EXPORT="/home/ubuntu/pr_export/"
# Example using export set: HOSTNAME="localhost" DATABASE="openstreetmap" USERNAME="ubuntu" PASSWORD="admin1234"

echo 'Running Fetch Changeset from Private OpenStreetMap'

EXPORT_CHANGESET_FILE_FOLDER_NAME="${FOLDERNAME_PR_EXPORT}pr_export.osc"
PII_REMOVER_FILE_FOLDER_NAME="${FOLDERNAME_PR_EXPORT}sanitize_PII.py"
NO_PII_CHANGESET_FILE_FOLDER_NAME="${FOLDERNAME_PR_EXPORT}pr_noPII_export.osc"
FILENAME="${FOLDERNAME_PR_EXPORT}last_pr_export_ts.txt"
REMOVE_TAGS_LIST="clientid compkey tripid"


if [ -n "$HOSTNAME" ] && [ -n "$DATABASE" ] && [ -n "$USERNAME" ] && [ -n "$PASSWORD" ] ; then
    echo "Env. Var. are Set, Proceeding"
else
    echo "ERROR: The Required Environment Variables are not Set, Please Set and Re-RUN"
    echo "Exiting Script"
    exit 1
fi

if [ -n "$FOLDERNAME_PR_EXPORT" ] ; then
    echo "Export Private OSM Working Folder Exists and Env. Var. is Set, Proceeding"
else
    echo "ERROR: The Required Export Folder Does not Exist or Env. Var. Not Set"
    echo "Please Set Env. Var., Create and Copy the Required Files as instructed in INSTALL.md"
    echo "Exiting Script"
    exit 1
fi

if [ -f "$FILENAME" ]; then
    echo "Last timestamp file exists"
else
    echo $(date '+%Y-%m-%d_%H:%M:%S') > $FILENAME
fi

while read -r line; do
# reading each line
echo "Line No. $n : $line"
LAST_PR_EXPORT_TS=$line
done < $FILENAME

echo "Last Export Date and Time : $LAST_PR_EXPORT_TS"
echo "Now running private osm changeset extract"
NOW_DATE=$(date '+%Y-%m-%d_%H:%M:%S')
osmosis --rdc host=$HOSTNAME database=$DATABASE user=$USERNAME password=$PASSWORD validateSchemaVersion=no readFullHistory=no intervalBegin=$LAST_PR_EXPORT_TS --wxc file=$EXPORT_CHANGESET_FILE_FOLDER_NAME
echo "Extract complete"
LAST_PR_EXPORT_TS=$NOW_DATE
echo "Saving current export Date and Time: $LAST_PR_EXPORT_TS ,to file: 'last_pr_export_ts.txt'"
echo $LAST_PR_EXPORT_TS > $FILENAME
echo 'Fetch completed'

echo 'Now initializing PII remover'
$PII_REMOVER_FILE_FOLDER_NAME -i $EXPORT_CHANGESET_FILE_FOLDER_NAME -o $NO_PII_CHANGESET_FILE_FOLDER_NAME -t $REMOVE_TAGS_LIST
cp $NO_PII_CHANGESET_FILE_FOLDER_NAME "${OSM_FOLDER}public/pr_noPII_export.osc"
echo "PII has been removed, download file"

