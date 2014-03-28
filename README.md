AqProjectUpdater
================

1. Obtain a SmartSheet API key.
2. Find the sheet ID and column ID of the column you want to update.
$ cd /path/to/smartsheet/

# Open a Python interpreter
$ python
# Open a connection to your SmartSheet account and display your sheets.
>>> s = SmartSocket(<api_key>)
>>> s.display()

# Find the ID of the sheet you want and display its contents.
# Find the ID of the column you want and make note of it.
>>> ss = s.get_sheet(<sheet_id>)
>>> ss.display()
# Exit Python
>>> exit()

3. Run the updater.
$ cd /path/to/AqProjectUpdater/
# View full list of options
$ python AqProjectUpdater.py -h
$ python AqProjectUpdater.py --api_key=<api_key> --sheet_id=<sheet_id> \
--column_id=<column_id> --db_address=<db_address>