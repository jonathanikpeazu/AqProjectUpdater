from SmartObjects import *

class SmartColumn(Rowed):
    
    def __init__(self, sheet, attr_dict):
        self.sheet = sheet
        self.__dict__.update(attr_dict)  
        
    def __getattr__(self, name):
        if name == 'cells':
            return self.getCells()
        
        return Rowed.__getattr__(self, name)
        
    def modify_column(self, **kwargs):
        self.sheet.modify_column(col_id = self.id, **kwargs)
    
    def get_cells(self, row_query = None):
        '''Return an array of cell objects belonging to this column. Empty cells
        are omitted.'''
        
        if row_query is None:
            rows = self.rows
        
        else:  
            if not isinstance(row_query, list):
                row_query = [row_query]
            if not all([isinstance(q, int) for q in row_query]):
                raise TypeError('''Rows in a given column must be referred to 
                by row number.''')
            
            rows = [self.get_row(query = q, field = 'rowNumber') \
                    for q in row_query]
            
            rows.sort(key = lambda r: r.rowNumber)
        
        cells = [row.get_cell(field = 'columnId', query = self.id) \
                 for row in rows]
        return [c for c in cells if c is not None]
        
    def update_from_dict(self, new_dict):
        self.__dict__.update(new_dict)
        
    def display(self, row_query = None, max_width = MAX_WIDTH):
        
        self.sheet.display(row_query = row_query, col_query = self.index, \
                           max_width = max_width)