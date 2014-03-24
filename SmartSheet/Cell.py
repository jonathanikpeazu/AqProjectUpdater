from SmartObjects import *

class SmartCell(SmartObjectBase):
    
    def __init__(self, row, attr_dict):
        self.row = row
        self.__dict__.update(attr_dict)
        
    def __getattr__(self, name):
        
        if name in ['value', 'displayValue']:
            return ''

        if name == 'column':
            return self.sheet.search_columns(field = 'id', \
                                             query = self.columnId)
        
        if name in ['column_title', 'columnTitle']:
            return self.column.title
        
        if name in ['row_number', 'rowNumber']:
            return self.row.rowNumber
        
        raise AttributeError(name)
        
        
    def __str__(self):
        return str(self.value)
    
    def display(self, colTitle = True, underLine = True, maxWidth = MAX_WIDTH,\
                padding = 2):
        header = ['', self.column_title]
        rows = [[self.row_number, str(self)]]
        columnPrint(header = header, rows = rows, maxWidth = maxWidth)