import os
from optparse import OptionParser, OptionGroup 

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

optional.add_option('--db_encoding',
                    type = 'string',
                    default = 'utf-8',
                    help = '''The encoding to expect from the database result. \
                    Defaults to 'utf-8'.''')
 
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

parser.add_option_group(log_opt)