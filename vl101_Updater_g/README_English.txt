VL Event Updater

This tool is a CLI utility for maintaining event data in setting.json files used for web lecture systems.

The tool automates the following tasks:

・Removing expired events
・Adding new events
・Updating existing events
・Updating material metadata
・Generating notification text


【Features】
1. Expired Event Cleanup
Events whose contentsClose date has passed are automatically detected and removed.

Deletion is performed by sweep_close_contents()
vl101_final_sweeper.py


2. Event ID Input
Users enter event IDs to be added.

Example

Enter Event ID(s) to add
Enter each ID on a new line
Enter 'q' when finished

Input validation allows only A-Z a-z 0-9 _ -

Implemented in read_add_for_vl800_event_ids() in vl800_confirm_target_data


3. Extract Event Data

Event information is extracted from vl800/{eventId}/list/{region}/setting.json

Extracted values include

・eventId
・eventDate
・regionName
・materialsText
・materialsCreateDate

Implemented in get_values_from_vl800_setting_json() in vl800_confirm_target_data


4. Duplicate Check
The tool checks if the event already exists in the VL101 event list.

Duplicate Check Results

Implemented in check_event_duplicates() in vl101_event_checker.py


5. Update VL101 setting.json
New or updated events are written into vl101/{region}/json/setting.json

Processing includes:
・remove existing event
・insert new event
・maintain order

Implemented in final_updates_to_vl101_setting_json() in vl101_setting_json_writer.py


6. Material Metadata Update
The newest event (by eventDate) determines the material metadata.

Fields updated

materialsText
materialsCreateDate

Implemented in update_materials_for_new_only() in vl101_materials_updater.py


7. Notification Text Generation
Operation results are converted into notification text.

Output example

・Add
・Update
・Delete
・Materials

Saved in logs/

Implemented in save_notice_text() in get_text.py


【Run】
python tools/main.py or run_app.bat


【Requirements】
Python 3.10+

Standard libraries only

・json
・pathlib
・dataclasses
・collections