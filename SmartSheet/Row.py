from SmartObjects import *

from Cell import SmartCell

class SmartRow(Columned):    
    
    def __init__(self, sheet, attr_dict): 
        self.sheet = sheet
        self.__dict__.update(attr_dict)
        self.initialize_cells()
        
    def __getattr__(self, name):
        if name == 'columns':
            self.refresh(True, ('attachments' in self.__dict__),
                         ('discussions' in self.__dict__))
            if 'columns' in self.__dict__:
                return self.columns

        raise AttributeError(name)
                         
    
    def initialize_cells(self):
        '''Convert the row's cells from dictionaries to SmartCell objects.'''
        self.cells = map(lambda cell_dict: \
                         SmartCell(row = self, attr_dict = cell_dict),
                         self.cells)        
    
    def refresh(self, includeColumns = False,
                include_attachments = False, include_discussions = False):
        
        # The API endpoint is 'row/{sheetId}'
        endpoint = 'row/%s' % str(self.id)
        
        # Set up include parameter.
        include = []
        if includeColumns:
            include.append('columns')
        if include_discussions:
            include.append('discussions')
        if include_attachments:
            include.append('attachments')
        
        if include:
            include = '?include=' + ','.join(include)
            endpoint += include
        
        '''Send the request through the socket. The response is a dictionary of
        attributes.'''
        new_row_dict = \
            self.socket.send_request(method = get, endpoint = endpoint)
        
        self.update_from_dict(new_row_dict)
        
    def update_from_dict(self, new_dict):
        
        if new_dict['version'] <= self.version:
            if 'columns' not in self.__dict__:
                self.update_columns(new_dict['columns'])
            return
        
        self.update_cells(newAttrDict.pop('cells'))
        self.update_columns(newAttrDict.pop('columns'))
        
    def update_cells(self, new_cell_dicts):
        
        align_key = lambda current_cell, new_cell: \
            (current_cell['id'] if isinstance(current_cell, dict) \
             else current_cell.id) == new_cell['id']
            
        updates = align.align_right(self.cells.as_dicts(), new_cell_dicts)
        '''
        # An array of the cell ID's we wish to keep.
        newColIdSpace = [c[columnId] for c in newCellDicts]
        
        # Remove cells that have been deleted remotely.
        self.cells = filter(lambda cell: cell.columnId in newColIdSpace,
                            self.cells)
        
        '''
        '''Create a dictionary which pairs each SmartCell object with the
        new information about that object.'''
        updates = map(lambda dct: \
                      dict((next([cell for cell in self.cells \
                             if dct['columnId'] == cell.columnId], None), dct)),
                      newCellDicts)
        
        # Update cell objects using the new info.
        map(lambda (cell, info): cell.update(info), updates.iteritems())
        
    
    def display(self, col_query = None, maxWidth = MAX_WIDTH):
        # If the column field is not already populated, populate it.
        if 'columns' not in self.__dict__:
            self.refresh(includeColumns = True)
            
        # If all columns are being printed, no col_query sanity check required.
        if col_query is None:
            col_query = range(len(self.cells))
        else:
            ''' Handle the case where a user passes a single string or integer
            as a column value.'''
            if not isinstance(col_query, list):
                col_query = [col_query]
            
            '''If col_query argument contains things that are not ints or 
            strings, raise a TypeError''' 
            if not all(map(lambda c: isinstance(c, str) or isinstance(c, int),
                           col_query)):
                # TODO: be more descriptive.
                raise TypeError()
            
            # Convert numerical column indices to 0-index
            col_query = map(lambda c: c - 1 if isinstance(c, int) else c, 
                           col_query)
            
            # Check that all numerical indices are in range.
            try:
                indices = filter(lambda c: isinstance(c, int), col_query)
                if min(indices) < 0:
                    raise ColumnError(min(indices, self.sheet))
                if max(indices > len(self.columns) - 1):
                    raise ColumnError(max(indices, self.sheet))
                       
            except ValueError:
                '''We'll get a ValueError for min() and max() if there are no
                numerical indices in the col_query, but this is ok, so pass.'''                
                pass
            
            # Translate column string names to numerical indices.
            col_query = map(lambda c: c if isinstance(c, int) \
                           else self.sheet.__lookupColumnIndex(c))
            col_query.sort()
    
        '''Create the header. Leave some space at the right for the row
        number.'''
        header = map(lambda c: c['title'] if isinstance(c, dict) 
                     else c.attr,
                     [self.columns[i] for i in col_query])
        header.insert(0, '')
    
        # Extract values in each of the row's cells.
        data = map(lambda cell: str(cell['value']) if isinstance(cell, dict) \
                   else cell.value,
                   [self.cells[i] for i in col_query])
        
        # Add the row number.
        data.insert(0, str(self.rowNumber))
        data = data
        
        # Print everything.
        columnPrint(data = data, header = header, delimiter = '|')