from SmartObjects import *

class SmartColumn(Rowed):
    
    def __init__(self, sheet, attr_dict):
        self.sheet = sheet
        self.__dict__.update(attr_dict)  
        
    def __getattr__(self, name):
        if name == 'cells':
            return self.getCells()
        else:
            return super(SmartColumn, self).__getattr__(name)
        
    def modify_column(self, **kwargs):
        self.sheet.modify_column(col_id = self.id, **kwargs)
    
    def getCells(self, rowRange = None):
        '''Return an array of cell objects belonging to this column. Empty cells
        are omitted.'''
        
        if rowRange is None:
            rowRange = [r.rowNumber for r in self.rows] 
            
        if isinstance(rowRange, int):
            row = self.getRow(field = rowNumber, query = rowRange)
            cell = row.getCell(field = 'columnId', query = self.id)
            return cell        
            
        if isinstance(rowRange, list):
            cells = [self.getCells(r) for r in rowRange]
            cells = [c for c in cells if c is not None]
            return cells
        
    def display(self, rowRange = None, maxWidth = MAX_WIDTH):
        
        # Grab the cell objects corresponding to the rows we need to print.
        cells = self.getCells(rowRange)
        
        # Grab the data rows
        data = [[c.rowNumber, str(c.value)] for c in cells]
         
        # Create the header row.
        header = ['', self.title]
        
        columnPrint(data = data, header = header, maxWidth = maxWidth)