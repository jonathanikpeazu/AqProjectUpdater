from SmartObjects import *

class SmartCell(SmartObjectBase):
    
    def __init__(self, row, attr_dict):
        self.row = row
        self.__dict__.update(attr_dict)
        
    def __getattr__(self, name):
        
        if name in ['value', 'displayValue']:
            return ''

        if name == 'column':
            return self.sheet.get_column('id', self.columnId)
        
        if name in ['column_title', 'columnTitle']:
            return self.column.title
        
        if name in ['row_number', 'rowNumber']:
            return self.row.rowNumber
        
        raise AttributeError(name)
        
        
    def __str__(self):
        return str(self.value)
    
    def display(self, header = True, max_width = MAX_WIDTH):
        header = ['', self.column_title]
        rows = [[self.row_number, str(self)]]
        columnPrint(header = header, rows = rows, maxWidth = maxWidth)
        
    def update_from_dict(self, new_dict):
        self.__dict__.update(new_dict)