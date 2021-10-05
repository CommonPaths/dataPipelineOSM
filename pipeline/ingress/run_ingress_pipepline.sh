#!/bin/bash
DATABASE=openstreetmap
TEMP_DATABASE=openstreetmap_v2 # this needs to be removed and updated where refrenced to DATABASE once the actual database has been updated to include this table
USERNAME=postgres
HOSTNAME=test-osm2pgsql-pipeline.clxd7sj5dotc.us-east-1.rds.amazonaws.com
export PGPASSWORD=osmsecret
WORKOSM_DIR=/home/ubuntu/osmosis_working_dir2
S3_BUCKET=s3://mvt-test-bucket
BBOX_MIN_LAT=47.070017
BBOX_MAX_LAT=47.794933
BBOX_MIN_LON=-122.549826
BBOX_MAX_LON=-121.044524

var_update=`psql -h $HOSTNAME -U $USERNAME $TEMP_DATABASE -t -c "SELECT manual_update FROM manual_update WHERE id=1"`
current_time=$(date "+%Y%m%d-%H_%M_%S")
source read_ts_state_env.sh

echo 'INFO: retrieved value from db: $var_update'
cp $WORKOSM_DIR/state.txt previous_state.txt

if [[ $var_update == " t" ]]
then
  echo 'Manual Update Required'
  exit 1;
else
  echo 'INFO: pulling public changeset using osmosis'
  osmosis --read-replication-interval workingDirectory="${WORKOSM_DIR}" --simplify-change \
          --write-xml-change file=$WORKOSM_DIR/current_public_changeset.osc
  python /$WORKOSM_DIR/remove_nodes.py -f Trial.osc -latmin $BBOX_MIN_LAT -latmax $BBOX_MAX_LAT \
	  				            -lonmin $BBOX_MIN_LON -lonmax $BBOX_MAX_LON -o $WORKOSM_DIR/public_with_bbox_applied.osc
  echo 'INFO: pulling private changeset based on the last date reconciliation was run'
  osmosis --read-apidb-change host=$HOSTNAME database=$DATABASE user=$USERNAME password=$PGPASSWORD intervalBegin=$last_timestamp \
          --write-xml-change file=$WORKOSM_DIR/current_private_changeset.osc
  echo 'INFO: pushing changesets to s3'
  aws s3 cp /$WORKOSM_DIR/current_public_changeset.osc $S3_BUCKET/${current_time}_current_public_changeset.osc
  aws s3 cp /$WORKOSM_DIR/public_with_bbox_applied.osc $S3_BUCKET/${current_time}_public_with_bbox_applied.osc
  aws s3 cp /$WORKOSM_DIR/current_private_changeset.osc $S3_BUCKET/${current_time}_current_private_changeset.osc
  echo 'INFO: running reconciliation script'
  recon_out=$(python private_to_public_parser.py -r $WORKOSM_DIR/current_private_changeset.osc -u $WORKOSM_DIR/bounded_public_changeset.osc 2>&1 /dev/null/)
  if [[ $recon_out == '33' ]]
  then
    var_update=`psql -h $HOSTNAME -U $USERNAME $TEMP_DATABASE -t -c "UPDATE manual_update SET manual_update = true WHERE id=1"`
    echo 'INFO: Manual Update Required'
  else
    echo 'INFO: no reconciliation needed - proceeding to apply changeset to KCMs database'
    osmosis --read-xml-change file=<$WORKOSM_DIR/public_with_bbox_applied.osc --write-apidb-change host=$HOSTNAME database=$DATABASE user=$USERNAME password=$PGPASSWORD
  fi

fi
