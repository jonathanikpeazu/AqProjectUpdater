# Base classes
from SmartObjects import *

class SmartSheet(Rowed, Columned):

    def __init__(self, socket, sheet_id = None,
                 include_attachments = False, include_discussions = False,
                 attr_dict = None):
        
        # Make sure a proper identifier was given.
        if not any([attr_dict, sheet_id]):
            raise TypeError('Sheet must be instantiated with either sheet ID \
            or pre-fetched attribute dictionary.')
        
        # If only sheet ID was provided, fetch attr_dict manually.
        if sheet_id:
            attr_dict = socket.get_sheet_info(sheet_id, include_attachments,
                                                include_discussions)
        
        self.socket = socket
        self.__dict__.update(attr_dict)
        
        # Initialize rows and columns.
        self.initialize_rows()
        self.initialize_columns()
        
    def __getattr__(self, name):
        if name == 'sheet':
            return self
        
        return SmartObjectBase.__getattr__(self, name)
        
    def refresh(self, include_attachments = False, 
                include_discussions = False, force = True):
        # Fetch the latest version of this sheet from the server.
        
        new_dict = self.socket.get_sheet_info(self.id, include_discussions,
                                          include_attachments)
        
        if force or new_dict['version'] > self.version:
            self.update_rows(new_dict.pop('rows'))
            self.update_columns(new_dict.pop('columns'))
            self.__dict__.update(new_dict)        
    
    def display(self, row_query = None, col_query = None, refresh = False,
                max_width = MAX_WIDTH):
        
        if refresh:
            self.refresh()
        
        # Grab just the column objects we need.    
        if col_query is None:
            columns = self.columns
        else:
            if not isinstance(col_query, list):
                col_query = [col_query]
            '''If col_query argument contains things that are not ints or 
            strings, raise a TypeError''' 
            if not all([isinstance(q, str) or isinstance(q, int) \
                        for q in col_query]):
                raise TypeError('Columns must be referred to by title or \
                1-based index.')            
            # Search by title if string, or index if int.
            columns = [self.get_column(query = q, 
                                       field = 'index' if isinstance(q, int) \
                                       else 'title') for q in col_query]
    
        # Grab just the row objects we need.    
        if row_query is None:
            rows = self.rows          
        else:
            if not isinstance(row_query, list):
                row_query = [row_query]
                
            # Rows should only be referred to by row number.
            if not all([isinstance(q, int) for q in row_query]):
                raise TypeError('Rows must be referenced by rowNumber.')
            
            rows = [self.get_row(query = q, field = 'rowNumber') \
                    for q in row_query]        
        
        # Sort rows and columns
        columns.sort(key = lambda c: c.index)
        rows.sort(key = lambda r: r.rowNumber)
        
        # Make print headers and data
        header = self.make_header(columns)
        data = [row.make_data(columns) for row in rows]
        
        column_print(data, header, max_width = max_width, \
                    delimiter = '|', padding = 2)
     
    def add_column(self, index = 0, title = 'New Column', 
                   col_type = 'TEXT_NUMBER', **kwargs):
        '''Insert a column into the sheet.
                
        Arguments:
        -title (default 'New Column')
        -index (zero-based, default 0)
        -col_type  (default 'TEXT_NUMBER')
        
        Keyword arguments:
        -symbol
        -options
        -systemColumnType
        -autoNumberFormat'''       
        
        '''The API request arguments are the same as those of this
        method, so we can just take those and feed them to the request's
        'data' parameter'''
        
        request_body = dict([('index', index), 
                             ('title', title), 
                             ('type', col_type)])
        
        request_body.update(kwargs)
        
        # The API endpoint for an add column request.
        endpoint = 'sheet/%d/columns' % self.id
        
        # Compose the header
        header = {'Content-Type': 'application/json'}        
        
        # Remove None values from the request body
        request_body = dict((key, val) for key, val in request_body.iteritems() \
                           if val is not None)
        
        # Hand the information off to the socket. Return True if the request
        response = self.socket.send_request(method = post, endpoint = endpoint, \
                                data = request_body, headers = header)
            
    def modify_column(self, col_id, **request_body):
        '''Modify an existing column within the sheet. Columns must be referred
        to Title or ID.'''
        
        ''' Request must include the following params. If they're missing,
        find them using the column ID.'''
        required_params = ['title', 'index']
        if not all(param in request_body for param in required_params):
            col = self.get_column('id', col_id)
            request_body.update(dict((param, getattr(col, param)) \
                                     for param in required_params \
                                     if param not in request_body))
            
        
        # Prepare the socket request
        endpoint = 'column/%d' % col_id
        
        request_body.update({'sheetId' : self.id})
        
        header = {'content-type' : 'application/json'}
        
        # Hand off the request to the socket
        response = self.socket.send_request(method = put, endpoint = endpoint,
                                            data = request_body, 
                                            headers = header)
        return response
    
    def share(self, email, accessLevel, notify = True):
        '''Invites an email recipient to share the desired spreadsheet with a
        given access_level. If the notify flag is set, the user will receive an
        invitation via email.
        
        Possible access levels:
        
        VIEWER:       The user has read-only access to the resource.
        
        EDITOR:       The user can edit the resource, but cannot alter the 
                      structure of, delete or share the resource.
        
        EDITOR_SHARE: The same as EDITOR, but with the ability to share the 
                      resource to other users.
        
        ADMIN:        The user can edit and share the resource, and can alter 
                      the structure of the resource as well.
        
        OWNER:        The user has complete control over the resource.
        '''

        # Grab the arguments and put them in the request body
        request_body = dict([('email', email),
                             ('accessLevel', accessLevel.upper())])
        
        
        # Set endpoint, including email flag.
        email_flag = "?sendEmail=" + ("true" if notify else "false")   
        endpoint = ('sheet/%d/shares' % self.id) + email_flag
        
        # send the request.
        
        response = self.socket.send_request(method = post, endpoint = endpoint,
                                            data = request_body)
        
    def change_access(self, userId, accessLevel):
        """Updates a user's level of access to a given sheet. Possible access
        levels:
        
        VIEWER:       The user has read-only access to the resource.
        
        EDITOR:       The user can edit the resource, but cannot alter the 
                      structure of, delete or share the resource.
        
        EDITOR_SHARE: The same as EDITOR, but with the ability to share the 
                      resource to other users.
        
        ADMIN:        The user can edit and share the resource, and can alter 
                      the structure of the resource as well.
        
        OWNER:        The user has complete control over the resource.
        
        NONE:         The user can no longer view this sheet.
        """
        
        # The data packet to be sent along with the HTTP request.
        request_body = dict([('userId', userId),
                          ('accessLevel', accessLevel)])
        
        endpoint = 'sheet/%(sheetId)d/share/%(userId)' % {'sheetId' : self.id,
                                                          'userId' : userId}
        
        # 'NONE' uses a different HTTP method, same endpoint
        method = delete if accessLevel == 'NONE' else put
        
        r = self.socket.send_request(method = method, endpoint = endpoint,
                                     data = request_body)
        