# **Export Control Ruby on Rails Page for Changeset from the Private OpenStreetMap **
MTN-104: Finalize Export pipeline.
Instruction to setup the export control page as an extension to the OSM website (Rails Port).

Edit appropriately and copy the file "osm_set_var.sh" (see below) to "/etc/profile.d/" and set the file attribute to executable.
This will set the env. variables for all users system wide
```
	# set env. var. for system wide
	# place this file osm_set_env_var.sh in /etc/profile.d and set exec attribute
	export OSM_FOLDER="/home/ubuntu/openstreetmap-website/" 
	export FOLDERNAME_PR_EXPORT="/home/ubuntu/pr_export/"
	export HOSTNAME="localhost" 
	export DATABASE="openstreetmap" 
	export USERNAME="hased" 
	export PASSWORD="hased"
```

Execute the following command from with in the $OSM_FOLDER directory:
```
    cd $OSM_FOLDER
	rails generate controller export_ctrl export_page
```
Add the following two lines to the file: "/config/routes.rb/"
```
	get 'export_ctrl/export_page'
	get '/button', to: 'export_ctrl#button', as: 'button'
	get 'export_ctrl/download_osc'

```
Create the export directory:
```
	mkdir $FOLDERNAME_PR_EXPORT
```
Copy the export bash script file export_pr_chanageset.sh to $FOLDERNAME_PR_EXPORT and set the executable file attribute:
```
	cp <download_location>/export_pr_changeset.sh "${FOLDERNAME_PR_EXPORT}export_pr_changeset.sh"
	chmod 755 "${FOLDERNAME_PR_EXPORT}export_pr_changeset.sh"
```
Copy the PII remover python code file, sanitize_PII.py to $FOLDERNAME_PR_EXPORT and set the executable file attribute:
```
	cp <download_location>/sanitize_PII.py "${FOLDERNAME_PR_EXPORT}sanitize_PII.py"
	chmod 755 "${FOLDERNAME_PR_EXPORT}sanitize_PII.py"
```
    Please make sure to check and copy the latest version of the PII remover python code file from the repo.

Copy the following controller and views, ruby files to the indicated locations:
```
	cp <download_location>/export_ctrl_controller.rb  "${OSM_FOLDER}export_ctrl_controller.rb"
	cp <download_location>/export_page.html.erb "${OSM_FOLDER}app/views/export_ctrl/export_page.html.erb"
	cp <download_location>/button.html.erb "${OSM_FOLDER}app/views/export_ctrl/button.html.erb"
```
If the file "${FOLDERNAME_PR_EXPORT}last_pr_export_ts.txt" does not exist the bash script checks and creates the file and, initializes it with the current timestamp.
However, for custom start timestamp create or edit the file "${FOLDERNAME_PR_EXPORT}last_pr_export_ts.txt" with timestamp formated as (YYYY-MM-DD_hh_mm_ss), for example: 
```
    2020-04-06_14:19:22
```
The URL to access the export control pages are listed below, use browser navigation button for going back:
-Main export control page:
```
    http://<ip or url of private osm>/export_ctrl/export_page
```
-After the export button has been pressed, the progress status page with the download link:
```
    http://<ip or url of private osm>/button?
```
-The download file link page:
```
    http://<ip or url of private osm>/export_ctrl/download_osc
```
Happy Exporting.
