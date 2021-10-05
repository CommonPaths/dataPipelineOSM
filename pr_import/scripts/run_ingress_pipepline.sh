#/bin/bash
PR_IMPORT_SCRIPTS_DIR=/home/ubuntu/pr_import/scripts # bash and python scripts
PR_IMPORT_PLANET_REP=/home/ubuntu/pr_import/planet_rep # all .osc files and state.txt
S3_BUCKET=s3://mvt-test-bucket
BBOX_MIN_LAT=47.070017
BBOX_MAX_LAT=47.794933
BBOX_MIN_LON=-122.549826
BBOX_MAX_LON=-121.044524

var_update=`psql -h $HOSTNAME -U $USERNAME $DATABASE -t -c "SELECT setting_value FROM reconciliation_settings WHERE setting_name='manual_update'"`
current_time=$(date "+%Y%m%d-%H_%M_%S")
# source ./read_ts_state_env.sh

### beginning of the pain
echo "INFO: Reads state.txt from osmosis, formats and saves timestamp to env variable"
filename=$PR_IMPORT_PLANET_REP/state.txt
while read -r line; do
# reading each line
#echo "Line No. $n : $line"
last_timestamp=$line
done < $filename
echo $last_timestamp
echo Formating timestamp
last_timestamp=${last_timestamp#t*=}
last_timestamp=${last_timestamp/T/_}
last_timestamp=${last_timestamp%Z}
last_timestamp=$(echo $last_timestamp | sed 's@[\\]@@g')
echo $last_timestamp
echo "Saving to var 'last_timestamp' and file 'last_timestamp.txt'"
echo $last_timestamp > $PR_IMPORT_PLANET_REP/last_timestamp.txt

echo $last_time_stamp
### end of the pain

echo 'INFO: retrieved value from db: $var_update'
cp $PR_IMPORT_PLANET_REP/state.txt $PR_IMPORT_PLANET_REP/previous_state.txt

if [[ $var_update == " true" ]]
then
  echo 'INFO: Manual Update Required'
  exit 1;
else
  echo 'INFO: Manual Update NOT Required'
  echo 'INFO: Pulling Public Changeset Using Osmosis'
  osmosis --read-replication-interval workingDirectory="${PR_IMPORT_PLANET_REP}" --simplify-change \
          --write-xml-change file=$PR_IMPORT_PLANET_REP/current_public_changeset.osc
  python3 /$PR_IMPORT_SCRIPTS_DIR/remove_nodes.py -f $PR_IMPORT_PLANET_REP/current_public_changeset.osc -latmin $BBOX_MIN_LAT -latmax $BBOX_MAX_LAT \
	  				            -lonmin $BBOX_MIN_LON -lonmax $BBOX_MAX_LON -o $PR_IMPORT_SCRIPTS_DIR/public_with_bbox_applied.osc
  echo 'INFO: Pulling Private Changeset Based On The Last Date Reconciliation Was Run'
  osmosis --read-apidb-change host=$HOSTNAME database=$DATABASE user=$USERNAME password=$PASSWORD validateSchemaVersion="no" intervalBegin=$last_timestamp \
          --write-xml-change file=$PR_IMPORT_PLANET_REP/current_private_changeset.osc
#  echo 'INFO: pushing changesets to s3'
#  # aws s3 cp /$PR_IMPORT_SCRIPTS_DIR/current_public_changeset.osc $S3_BUCKET/${current_time}_current_public_changeset.osc
#  # aws s3 cp /$PR_IMPORT_SCRIPTS_DIR/public_with_bbox_applied.osc $S3_BUCKET/${current_time}_public_with_bbox_applied.osc
#  # aws s3 cp /$PR_IMPORT_SCRIPTS_DIR/current_private_changeset.osc $S3_BUCKET/${current_time}_current_private_changeset.osc
  echo 'INFO: Running Reconciliation Script'
  # recon_out=$(python3 $PR_IMPORT_SCRIPTS_DIR/private_to_public_parser.py -r $PR_IMPORT_PLANET_REP/current_private_changeset.osc -u $PR_IMPORT_PLANET_REP/bounded_public_changeset.osc 2>&1 /dev/null/)
  recon_out=$(python3 $PR_IMPORT_SCRIPTS_DIR/private_to_public_parser.py -r $PR_IMPORT_PLANET_REP/test_private_data.osc -u $PR_IMPORT_PLANET_REP/test_public_data.osc 2>&1 /dev/null/)
  # if recon_out is equal to 33 it indicates that a reconciliation is needed, the below code will update the database flag and exit out. Otherwise the public changeset with a bounding box \
  # applied will be applied to the private osm database through Osmosis.
  if [[ $recon_out == '33' ]]
  then
    var_update=`psql -h $HOSTNAME -U $USERNAME $DATABASE -t -c "UPDATE reconciliation_settings SET setting_value = 'true' WHERE setting_name='manual_update'"`
    echo 'INFO: Manual Update Required'
  else
    echo 'INFO: No Reconciliation Needed - Proceeding To Apply Changeset To KCMs Database'
    # osmosis --read-xml-change file=$PR_IMPORT_SCRIPTS_DIR/public_with_bbox_applied.osc --write-apidb-change host=$HOSTNAME database=$DATABASE user=$USERNAME password=$PASSWORD
  fi
fi
