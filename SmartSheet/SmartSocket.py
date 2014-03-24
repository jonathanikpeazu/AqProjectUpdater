from util.ColumnTools import columnPrint

from config import *

# HTTP requests
import requests
from requests import get
from requests import post
from requests import put

# JSON formatting
import simplejson as json
import math

from SmartObjects import SmartObjectBase

class SmartSocket:
    api_base = "https://api.smartsheet.com/1.1/"
    MAX_WIDTH = 40
        
    def __init__(self, api_key):
        self.api_key = api_key
        self.auth = dict(Authorization="Bearer " + api_key)
        self.sheets = self.get_sheets()
    
    def send_request(self, method, endpoint, headers = None, data = None):
        
        requestParams = {}
        
        # Grab the url
        requestParams['url'] = SmartSocket.api_base + endpoint
        
        # Compose the header
        requestParams['headers'] = self.auth # Authorization
        if headers:
            # Custom header
            requestParams['headers'] = dict(requestParams['headers'], **headers)
        
        if data:
            requestParams['data'] = json.dumps(data)
            
        r = method(**requestParams)
        
        return json.loads(str(r.text))
            
        
    def get_sheets(self):
        ''' Fetch information about all sheets in the form of an array of json
        objects, then load these to python dictionaries.'''
        
        # Array of sheet dictionaries
        sheet_dicts = self.send_request(method = get, endpoint = 'sheets')
        
        # Sort sheets in order of name
        sheet_dicts.sort(key = lambda s: s['name'].lower())
        
        return sheet_dicts
    
    def refresh(self):
        '''Fetch a new list of available sheets'''
        
        fresh_sheets = self.get_sheets()
        
        align_key = lambda s1, s2: dict(s1)['id'] == s2['id']
        
        # Line up new sheets with old sheets, discarding old ones if not present
        updates = align.align_right(self.sheets, fresh_sheets, align_key)
         
        
        '''Make the updates. Refresh smartsheet instances and merge 
        dictionaries.'''
        sheets = map(lambda s1, s2: \
                     s1.refresh() if isinstance(s1, SmartSheet) else s2,
                     updates)
        
        self.sheets = sheets
        
    def display(self, refresh=False, \
                maxWidth = MAX_WIDTH, padding = CELL_PADDING):
        '''
        Display overview of all available sheets, formatted in the following
        way:
           name:  id:  access_level:
        ---------------------------
        1. name1  id1  al1
        2. name2  id2  al2
        
        PARAMETERS:
        
        refresh: If True, fetch the latest information about sheets belonging
        to the user.
        
        maxWidth: The maximum allowable width of a column.
        
        padding: How much space is left between columns
        '''
        
        # Fetch latest sheet overview
        if refresh:
            self.refresh()
        
        # Normalize all the sheets to dictionaries and place them in the array.
        sheet_dicts = map(lambda s: s if isinstance(s, dict)
                          else s.__dict__, self.sheets)
                         
        '''Convert sheets from an array of dictionaries to an array of rows,
        each representing info about a single sheet.
        [{'name': 'name1', 'id': 'id1', 'access_level': 'al1'},
         {'name': 'name2', 'id': 'id2', 'access_level': 'al2}]
          -> [['name1', id1, al1], ['name2', 'id2', 'al2']]'''
        sheets = \
            map(lambda sheet_dict: \
                map(str, [sheet_dict['name'], sheet_dict['id'], \
                          sheet_dict['accessLevel']]), \
                sheet_dicts)     
            
        # Enumerate the sheets and add column headers.
        sheets = map(lambda (i, s): [str(i + 1) + '.'] + s, 
                     enumerate(sheets))
        
        header = ['', 'name', 'id', 'access_level']     
        
        # Display the info.
        columnPrint(data = sheets, header = header, maxWidth = maxWidth)
        
    def _query_internal_sheets(self, query, query_field):
        try:
            
            sheet = next(s for s in self.sheets \
                         if dict(s)[query_field] == query)
            
            return sheet
        except StopIteration:
            raise SheetError(query, self)
         
    def get_sheet(self, query, \
                 include_discussions=False, include_attachments=False):
        '''Fetches internal representation of SmartSheet object referred to by 
        the given query. The query can be a sheet ID or the string name of the 
        sheet.'''  
        
        # Search by ID if int, name if string
        if isinstance(query, int):
            query_field = 'id'   
        elif isinstance(query, str):
            query_field = 'name'
        else:
            raise TypeError('Get sheets by name or ID.')
            
        ss = self._query_internal_sheets(query, query_field)
        
        # If the sheet is already initialized, just return it.
        if isinstance(ss, SmartSheet):
            return ss
        else:
            attr_dict = self.get_sheet_info(ss['id'], include_discussions, 
                                         include_attachments)
            
            return SmartSheet(socket = self, sheet_id = ss['id'],
                              include_discussions = include_discussions,
                              include_attachments = include_attachments)
    
    def get_sheet_info(self, sheetId,
                       include_discussions = False, include_attachments = False):
        '''Fetch info about a given sheet in the form of a Py dictionary.'''
        
        endpoint = 'sheet/' + str(sheetId)
        
        '''if the user has specified to include attachments or discussions,
        the include parameter will reflect this information.'''        
        include = []
        if include_attachments:
            include.append('attachments')
        if include_discussions:
            include.append('discussions')
        if include:
            include = ','.join(include)
            include = '?include=' + include
            endpoint += include
               
        # Make the API request. r holds the response.
        sheet_dict = self.send_request(method = get, endpoint = endpoint)
        return sheet_dict
    
from Sheet import SmartSheet