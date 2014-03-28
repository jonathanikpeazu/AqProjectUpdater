from SmartObjects import *

class SmartRow(Columned):    
    
    def __init__(self, sheet, attr_dict): 
        self.sheet = sheet
        if 'columns' in attr_dict:
            attr_dict.pop('columns')
        self.__dict__.update(attr_dict)
        self.initialize_cells()
        
    def __getattr__(self, name):
        if name == 'columns':
            return self.sheet.columns
        raise AttributeError(name)
                         
    
    def initialize_cells(self):
        '''Convert the row's cells from dictionaries to SmartCell objects.'''
        self.cells = map(lambda cell_dict: \
                         SmartCell(row = self, attr_dict = cell_dict),
                         self.cells)  
        
    def get_cell(self, field, query):
        try:
            print field, query
            return next(c for c in self.cells if getattr(c, field) == query)
        except StopIteration:
            return None           
    
    def refresh(self, include = []):
        '''Fetch the latest information about this row from the server. 
        Possible values for the include parameter are combinations of the 
        following: "columns", "discussions", and "attachments".'''
        
        # The API endpoint is 'row/{sheetId}'
        endpoint = 'row/%s' % str(self.id)
        
        # Set up include parameter.
        if include:
            include = '?include=' + ','.join(include)
            endpoint += include
        
        '''Send the request through the socket. The response is a 
        dictionary of attributes.'''
        new_row_dict = \
            self.socket.send_request(method = get, endpoint = endpoint)
        
        self.update_from_dict(new_row_dict)
        
    def update_from_dict(self, new_dict):
                              
        if 'columns' in new_dict:
            self.update_columns(new_dict.pop('columns'))
            
        self.update_cells(new_dict.pop('cells'))        
        self.__dict__.update(new_dict)
        
    def update_cells(self, new_dicts):
        
        align_key = lambda cell, new_dict: cell.columnId == \
            new_dict['columnId']
            
        updates = align.align_right(self.cells, new_dicts, align_key)
        
        # Update cell objects using the new info.
        map(lambda (cell, new_dict): \
            cell.update_from_dict(new_dict) if cell else None, updates)
        
        self.cells = [cell if cell else SmartCell(self, new_dict) \
                      for (cell, new_dict) in updates]        
    
    def display(self, col_query = None, max_width = MAX_WIDTH):
        
        self.sheet.display(row_query = self.rowNumber, \
                           col_query = col_query, max_width = max_width)
            
    def make_data(self, columns = None):
        '''Extract values in each of the row's cells, leaving a blank space
        if the cell is not present. Used for column printing.'''
        
        if columns is None:
            columns = self.columns   
            
        align_key = lambda cell, column: cell.columnId == column.id
        data = align.align_right(self.cells, columns, align_key)
        data = [str(cell.value) if cell else '' for (cell, column) in data]
        
        # Add the row number.
        data.insert(0, str(self.rowNumber))  
        
        return data