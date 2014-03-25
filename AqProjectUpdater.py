#!/usr/bin/python

import sys
try:
    reload(sys)
except:
    pass
sys.setdefaultencoding('UTF-8')

import logging

import sys
import csv

import os
import sys

import logging

import requests
from datetime import datetime

__DEBUG = 0
    
__DEBUG_ARGS = ['--api_key', '2fbborrg7dwqegs40t4gacfg14', 
                '--db_address','http://66.172.13.75/pas/pasql/select?s=select%20%2A%20from%20proj_master%20where%20started%3E1330000000&db=asi.db',
                '--sheet_id', '5835894021220228',  
                '--column_id', '5804094553122692']

__LOG_FORMAT = '''%(asctime)-15s \n \
    Message: %(message)s \n \n \
    Old Options: %(old_options)s \n \n  \
    New Options: %(new_options)s \n \n \n \n'''

def __make_parser():
    
    parser = OptionParser(usage = "usage: %prog [options]")
        
    # Group of required parameters
    required = OptionGroup(parser, 'Required Parameters')    
    required.add_option('--api_key',
         type = 'string',
         help = 'The SmartSheet API key to use to fetch the documents')

    required.add_option('--sheet_id',
         type = 'int',
         help = 'The ID of the sheet you wish to update.')
    
    required.add_option('--column_id',
         type = 'int',
         help = '''The ID of the column you wish to update. Must be a dropdown list type.''')
    
    required.add_option('--db_address',
         type = 'string',
         help = '''The address of the database you wish to pull from, \
         enclosed in quotes. This database must return a file in CSV format.''')
    
    required.add_option('--smartsheet_path',
                        type = 'string',
                        default = os.getcwd(),
                        help = '''The absolute path to the directory containing your SmartSheet Python package directory.''')
    
    # add the options to the list.
    parser.add_option_group(required)

    # Optional parameters
    optional = OptionGroup(parser, 'More Parameters (Optional)')
     
    optional.add_option('--delimiter',
             type = 'string',
             default = '-',
             help = '''The character that will be used to separate the values \
             in "fields"''')   
    
    optional.add_option('--home_dir',
        type = 'string',
        default = os.getcwd(),
        help = '''The directory that will be used to store temp and log files. \n
        Defaults to the current working directory.''')
    
    optional.add_option('--fields',
         type = 'string',
         default = ['id', 'projcode', 'subno', 'name'],
         action = 'append',
         help = '''The field names that will be used to construct the column \
         options.''')
    
    parser.add_option_group(optional)
    
    # Scheduling options
    sched_opt = OptionGroup(parser, 'Scheduling Parameters (optional)')
        
    sched_opt.add_option('-x', '--run_scheduler',
            action = 'store_true',
            default = False,
            help = '''Set this flag if you want to run recurring updates in \
            the background. Defaults to false.''')
        
    sched_opt.add_option('--interval',
            type = 'int',
            default = 24,
            help = '''The interval on which the scheduler will run, in number \
            of hours. \n
            Default: 24.''')
    
    parser.add_option_group(sched_opt)
    
    # Logging options
    log_opt = OptionGroup(parser, 'Logging Options (optional)')
    
    log_opt.add_option('--no_log',
                       action = 'store_false',
                       default = True,
                       dest = 'log_enabled',
                       help = '''Disable logging for the project updater.
                       Logging is enabled by default.''')
    
    log_opt.add_option('--log_dir',
                       type = 'string',
                       default = '',
                       help = '''Custom logging directory.
                       Defaults to %s''' % os.path.join('home_dir', 'log'))
    
    return parser

if __name__ == '__main__':
    from AqProjectUpdater import AqProjectUpdater
    
    import signal # Scheduling
    import os # Paths
    import sys 
    from optparse import OptionParser, \
         OptionGroup             
        
    parser = __make_parser()
    
    if __DEBUG:
        parser.parse_args(args = sys.argv[1:] + __DEBUG_ARGS)
    else:
        parser.parse_args()
        
    settings = parser.values.__dict__
    
    # Import SmartSheet stuff
    sys.path.insert(0, settings.pop('smartsheet_path'))
    from SmartSheet.SmartObjects import *
    from SmartSheet.SmartSocket import SmartSocket
    from SmartSheet.util import Align
    
    # Set up directories
    home_dir = os.path.join(settings.pop('home_dir'), 'AqProjectUpdater-files')
    work_dir = os.path.join(home_dir, 'temp')
    
    if settings.pop('log_enabled'):
        if settings['log_dir']:
            log_dir = os.path.join(settings.pop('log_dir'), 'log')
        else:
            log_dir = os.path.join(home_dir, 'log')
    
    # Create the paths if they do not exist.
    for directory in [home_dir, work_dir, log_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    
    # Configure working directory
    settings['work_file'] = os.path.join(work_dir, \
                                         'AqProjectUpdater-temp.csv')  
    
    # Configure logging
    logging.basicConfig(format = __LOG_FORMAT, \
                        filename = os.path.join(log_dir, 'AqProjectUpdater.log'))
    
    
    # Set up smartsheet objects
    socket = SmartSocket(settings.pop('api_key'))
    sheet = socket.get_sheet(settings.pop('sheet_id'))
    settings['sheet'] = sheet
    
    sched_on = settings.pop('run_scheduler')
    interval = settings.pop('interval')
            
    aqp = AqProjectUpdater(settings)
    
    if sched_on:
        from apscheduler.scheduler import Scheduler        
        # Start the scheduler
        sched = Scheduler()
        
        sched.start()
        
        def update_and_log():
            message, old_options, new_options = aqp.update_projects()
            logging.warn(message, extra = {'old_options' : old_options,
                                           'new_options' : new_options})
            
        update_and_log()
        sched.add_interval_job(update_and_log, hours = interval)
        signal.pause()
    else:
        message, old_options, new_options = aqp.update_projects()
        logging.warn(message, extra = {'old_options' : old_options,
                                        'new_options' : new_options})  

class AqProjectUpdater:
    
    def __init__(self, settings):
        self.__dict__.update(settings)
        
    def update_projects(self):
        update_time = datetime.now()
        
        old_options = self.get_sheet_options()
        
        # Fetch the latest project info from the database.
        new_projects = self.pull_projects()        
        new_options = [self.stringify_project(proj) for proj in \
                                      new_projects]    
        
        # Send the new info to smartsheet
        resp = self.push_column_options(new_options)
        
        if 'errorCode' in resp:
            err = resp['errorCode']
            message = 'Project Update Not Made. Smartsheet Error Code %d' % err
        else:
            message = 'Project Update Was Made.'
        
        # Return info for logging.
        return (message, old_options, new_options)        
    
    def pull_projects(self):
        # TODO
        
        # Open stream from DB
        r = requests.get(self.db_address, stream = True)
        
        # Create temporary work file
        work_file = self.work_file
        
        # Overwrite existing work file
        open(work_file, 'w').close()
        
        # Write the data to a temporary work file.
        with open(work_file, 
                  'wb',          # write binary
                  1) as wf:      # line buffering
            for chunk in r.iter_content(1024):
                wf.write(chunk)
            
        # Load the projects from the temp file into Py dictionaries.
        with open(work_file, 
                  'rU',          # Universal newline-read
                  1) as wf: 
            dr = csv.DictReader(wf, fieldnames = self.fields)
            projects = [p for p in dr]
        
        # Remove unnecessary values from project dictionaries
        for p in projects:
            if None in p: # Key assigned to columns not in "fields"
                p.pop(None) 
        
        projects = [p for p in projects \
                    if all([field in p for field in self.fields])]
            
        return projects
    
    def push_column_options(self, new_options):
        # TODO: Docstring
        
        request_body = {'type' : 'PICKLIST', 
                        'options' :  new_options} 
        
        resp = self.sheet.modify_column(self.column_id, **request_body)
        
        # TODO: Error handling
        return resp    
    
    def find_updates(self, old_projects, new_projects):
        # TODO: docstring
    
        # Line up the projects by ID
        updates = Align.align_outer(old_projects, new_projects,
                                    key = lambda p1, p2: p1['id'] == p2['id'])
        
        # Keep only the projects that have changed.
        updates = filter(lambda (old_proj, new_proj): old_proj != new_proj,
                         updates)
        
        # Put into string format.
        updates = map(lambda (old_proj, new_proj): \
                      (self._stringify_project(old_proj),
                       self._stringify_project(new_proj)),
                      updates)
        
        return updates
            
        
    def stringify_project(self, project_dict):
        # TODO: Docstring
        
        fields = self.fields
        delimiter = self.delimiter
        
        values = [project_dict[field] for field in fields]
        string = delimiter.join(values)
        
        return string
    
    def get_sheet_options(self):
        old_projects = self.sheet.get_column('id', self.column_id).options
        return old_projects
        
    
    def dictify_project(self, project_string):
        field_values = project_string.split(self.delimiter)
        return dict((attr, val) \
                    for attr, val in zip(self.fields, field_values))