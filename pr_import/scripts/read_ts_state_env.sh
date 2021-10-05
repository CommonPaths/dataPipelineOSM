#!/bin/bash
PR_IMPORT_SCRIPTS_DIR=/home/ubuntu/pr_import/scripts # bash and python scripts
echo "Reads state.txt from osmosis, formats and saves timestamp to env variable"
filename=$PR_IMPORT_SCRIPTS_DIR/state.txt
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
echo $last_timestamp > last_timestamp.txt
echo "Done, please run script as 'source ./read_ts_state_env.sh' to retain variable"
