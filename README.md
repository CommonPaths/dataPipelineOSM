# MVT--Project-1.0
Common Pathways Project 1.0 , OSM, Vespucci, geo-data import, processing and export.

# *Schedule Daily to Get Changeset Data from Private OSM*

Create bash script that gets a daily changeset 
additionally, the script timestamps file name and takes backup of previous day changeset 
```
#/bin/bash
# +++++daily_fetch_pr_osm.sh+++++
# Takes backup of previous output changeset and creates daily changeset
echo 'Running fetch script daily changeset from private osm'
today_date=$(date '+%Y_%m_%d_%H_%M_%S')
rm /home/ubuntu/daily_pr_osm_changeset/daily_pr_osm_*
cp /home/ubuntu/daily_pr_osm_changeset/daily_pr_osm.osc /home/ubuntu/daily_pr_osm_changeset/daily_pr_osm_$today_date.osc
fdate=$(date '+%Y-%m-%d_%H:%M:%S' -d "-1 days")
osmosis --read-apidb-change host="localhost" database="openstreetmap" user="ubuntu" password="admin1234" validateSchemaVersion=no readFullHistory=no intervalBegin=$fdate --write-xml-change file=/home/ubuntu/daily_pr_osm_changeset/daily_pr_osm.osc
echo 'Execution complete, check cronjlog.txt and cronjerr.txt'
```
Save bash script and apply file permissions
```
chmod 755 /home/ubuntu/daily_pr_osm_changeset/daily_fetch_pr_osm.sh
```
Create Cron job schedule to run the bash script daily at 1am
At every run, creates log files
```
sudo -i
crontab -e
```
Add the following
```
0 1 * * * /home/ubuntu/daily_pr_osm_changeset/daily_fetch_pr_osm.sh 1> /home/ubuntu/cronjlog.txt 2> /home/ubuntu/cronjerr.txt
```

```

```
# **Get Full History Changeset Data from Private OSM Between NOW and Specified Date

```
osmosis --read-apidb-change host="localhost" database="openstreetmap" user="ubuntu" password="" validateSchemaVersion=no readFullHistory=yes intervalBegin="2020-3-1_0:0:0" --write-xml-change file=recentchange.osc

```

Date and Time can be obtained and previous date for query can be calculated in bash scripting as:
```
#/bin/bash
q_date=$(date -d "-7 days")
echo $q_date
```

# **Building and using osmosis**
```
sudo apt-get update  
sudo apt-get upgrade -y  
sudo apt-get -y install curl unzip gdal-bin tar wget bzip2 build-essential clang  
sudo apt-get -y install default-jre default-jdk gradle  
git clone -b migurski/update-apidb-schema --single-branch https://github.com/openstreetmap/osmosis.git  
cd osmosis  
./gradlew assemble  
sudo ln -s "$PWD"/package/bin/osmosis /usr/bin/osmosis
```
```
# Additonal steps for yum
sudo yum -y install curl unzip gdal-bin tar wget bzip2 build-essential clang  
sudo yum -y install default-jre java-1.8.0-openjdk-devel gradle
```

to check please run the test osmosis 
(null write) command below and make sure you have 0.47 version

# **Download data from Public OSM and prep for loading**
```
wget http://download.geofabrik.de/north-america/us/washington-latest.osm.bz2
bzip2 -d washington-latest.osm.bz2

osmosis --read-xml enableDateParsing=no file=washington-latest.osm --bounding-box clipIncompleteEntities=true top=48.299180 left=-122.854352 bottom=46.7288337 right=-120.906710 --write-xml file=tricountysea.osm

osmosis --read-xml enableDateParsing=no file=washington-latest.osm --bounding-box clipIncompleteEntities=true top=47.794933 left=-122.549826 bottom=47.070017 right=-121.044524 --write-xml file=kcmonly.osm
```
in the above use clipIncompleteEntities=true and or completeWays=true swtich after the --bounding-box

# **Using osmosis to load data**
load inital data
```
osmosis --read-xml kcmonly.osm --write-apidb host="localhost" database="openstreetmap" user="ubuntu" password="" validateSchemaVersion="no"
```
flash/truck database (this will delete all data in the database)
```
osmosis --truncate-apidb host="localhost" database="openstreetmap" user="root" password=""  validateSchemaVersion=no 
```
test osmosis 
```
osmosis --read-xml file="map_sea_westlake.osm" --write-null
```
update data in to database with data
```
osmosis --read-xml file="map_sea_westlake.osm" --write-apidb-change host="localhost" database="openstreetmap" user="root" password="" dbType=postgresql populateCurrentTables=yes validateSchemaVersion=no
```
other use to access via api
```
osmosis --read-xml file="map_sea_westlake.osm" --upload-xml-change server=”http://192.168.0.9:3000/api/0.6” user=”mvt_test” password=”” populateCurrentTables=yes validateSchemaVersion=no

```
# *Prepare recent data extracts from private and derive changes compared to recent public extract*

```
osmosis --read-xml-change file=recentchange.osc --simplify-change --write-xml-change file=delta_recent_change.osc 
osmosis --read-xml file=delta_recent_change.osm --read-xml file=delta_recent_change_publc.osm --derive-change --write-xml-change file=derived_change.osc
```

recentchange.osc is the data file extract of recent changes from private OSM

delta_recent_change_publc.osm is the data file extract of recent changes from public OSM

derived_change.osc is the data file derived by comparing recent changes from private and puplic and vice versa 

# **Update previous KCM OSM with latest planet OSC and bbox filter KCM**

First Sort both OSM and OSC by type and ID
```
osmosis --read-xml file=kcmonly.osm --sort --write-xml file=kcmonly_sorted.osm
osmosis --read-xml-change file=planet_change.osc --sort-change --write-xml-change file=planet_change_sorted.osc
```
Second apply planet OSC to KCM OSM
```
osmosis --read-xml-change file=planet_change_sorted.osc --read-xml file=kcmonly_sorted.osm --apply-change --write-xml file=updated_kcm_planet_change.osm
```

Third bbox filter the resulting updated OSM to yield only KCM area
```
osmosis --read-xml enableDateParsing=no file=updated_kcm_planet_change.osm --bounding-box completeWays=true top=47.794933 left=-122.549826 bottom=47.070017 right=-121.044524 --write-xml file=kcm_only_updated_with_planet.osm
