import os # Paths
import sys
reload(sys)  # to enable `setdefaultencoding` again
sys.setdefaultencoding("UTF-8")
import logging
import requests
from datetime import datetime
import simplejson as json

# CSV tools
import csv
from util.unicodecsv import UnicodeDictReader, UnicodeWriter

__DEBUG = 0

# Japanese, Johno API
__DEBUG_ARGS = ['--api_key', '2fbborrg7dwqegs40t4gacfg14', 
                '--db_address','http://66.172.13.75/pas/pasql/select?s=select%20%2A%20from%20proj_master%20where%20started%3E1380000000&db=aqk.db', '--db_encoding', 'sjis',
                '--sheet_id', '5835894021220228',  
                '--column_id', '1294997367613316']

# English, Johno API
'''__DEBUG_ARGS = ['--api_key', '2fbborrg7dwqegs40t4gacfg14', 
                '--db_address','http://66.172.13.75/pas/pasql/select?s=select%20%2A%20from%20proj_master%20where%20started%3E1380000000&db=asi.db', '--db_encoding', 'utf-8',
                '--sheet_id', '5835894021220228',  
                '--column_id', '1294997367613316']'''

_LOG_FORMAT = '''%(asctime)-15s: %(message)s \n \n \
    Old Options: %(old_options)s \n \n  \
    New Options: %(new_options)s \n \n \n'''

if __name__ == '__main__':
    from AqProjectUpdater import AqProjectUpdater
    from parser import parser
    import signal # Persistent python process for scheduling
    
    if __DEBUG:
        parser.parse_args(args = sys.argv[1:] + __DEBUG_ARGS)
    else:
        parser.parse_args()
        
    settings = parser.values.__dict__
    
    # Import SmartSheet stuff
    sys.path.insert(0, settings.pop('smartsheet_path'))
    from SmartSheet.SmartObjects import *
    from SmartSheet.SmartSocket import SmartSocket
    from SmartSheet.util import align
    
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
    logging.raiseExceptions = False # Make logger not complain.
    log_file = os.path.join(log_dir, 'AqProjectUpdater.log')
    
    # File handler, formatter
    fh = logging.FileHandler(log_file, \
                             encoding = settings['db_encoding'])
    ff = logging.Formatter(_LOG_FORMAT)
    fh.setFormatter(ff)   
    
    # Add handlers to logger
    logger = logging.getLogger()
    logger.addHandler(fh)
    
    logger.setLevel(logging.INFO)
    
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
        
        '''def update_and_log():
            message, old_options, new_options = aqp.update_projects()
            logging.warn(message, extra = {
                'old_options' : \
                json.dumps(old_options, encoding = settings['db_encoding']),
                'new_options' : \
                json.dumps(new_options, encoding = settings['db_encoding'])})
        '''
            
        update_and_log()
        sched.add_interval_job(update_and_log, hours = interval)
        signal.pause()
    else:
        aqp.update_projects()  

class AqProjectUpdater:
    
    logger = logging.getLogger(__name__)
    
    # Stream handler, formatter
    sh = logging.StreamHandler(sys.stdout)
    sf = logging.Formatter('%(message)s')
    sh.setFormatter(sf)   

    logger.addHandler(sh)
    
    logger.propagate = True
    
    # Configure logging
    '''
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s \n')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.INFO) 
    '''
    
    def __init__(self, settings):
        self.__dict__.update(settings)
        
    def update_projects(self):
        
        message = '''Preparing to update column uptions.
        Sheet: "%(sheet)s"
        Column title: "%(col_title)s" \n''' \
            % {'sheet' : self.sheet.name, 
               'col_title' : self.sheet.get_column('id', self.column_id).title}  
        
        AqProjectUpdater.logger.info(message)
        
        old_options = self.get_sheet_options()        
        
        # Fetch the latest project info from the database.
        new_projects = self.pull_projects()        
        new_options = [self.stringify_project(proj) for proj in \
                                      new_projects]   
        
        # Send the new info to smartsheet
        resp = self.push_column_options(new_options)
        
        if 'errorCode' in resp:
            message = 'Column Option Update Not Made. \n Smartsheet Response: %s' % resp
            new_options = [None]
        else:
            message = 'Column Option Update Was Made.'
            
        AqProjectUpdater.logger.info(message, \
                extra = {'old_options' : \
                         json.dumps(old_options, encoding = self.db_encoding),
                         'new_options' : \
                json.dumps(new_options, encoding = self.db_encoding)})     
    
    def pull_projects(self):
        # TODO
        AqProjectUpdater.logger.info('Pulling new projects from DB.')
        # Open stream from DB
        r = requests.get(self.db_address)
        content = [line for line in r.iter_lines(decode_unicode = True)]
        
        dr = UnicodeDictReader((line for line in content), 
                               encoding = self.db_encoding,
                               fieldnames = self.fields)
        
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
        logging.info('Pushing new column options to Smartsheet.')
        request_body = {'type' : 'PICKLIST', 
                        'options' :  new_options[:100]} 
    
        resp = self.sheet.modify_column(self.column_id, **request_body)
        
        # TODO: Error handling
        return resp    
    
    def find_updates(self, old_projects, new_projects):
        # TODO: docstring
    
        # Line up the projects by ID
        updates = align.align_outer(old_projects, new_projects,
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
        AqProjectUpdater.logger.info('Pulling existing options from Smartsheet.')
        
        column = self.sheet.get_column('id', self.column_id)
        options = column.options if 'options' in column.__dict__ else [None]
        return options
    
    def dictify_project(self, project_string):
        field_values = project_string.split(self.delimiter)
        return dict((attr, val) \
                    for attr, val in zip(self.fields, field_values))
    
