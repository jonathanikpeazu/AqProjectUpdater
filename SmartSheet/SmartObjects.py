from config import *

# Copy constructors
import copy

# Date/time utilities
from datetime import datetime
from dateutil import parser

# Alignment
from util import *

# More imports at the bottom

class SmartObjectBase(object):
    
    # For casting to dictionary
    def __iter__(self):
       return vars(self).iteritems()
            
    def __getattr__(self, name):
        if name == 'socket':
            return self.sheet.socket
        
        try:
            return dict(self)[name]
        except KeyError:
            raise AttributeError(name)
        
    def __init__(self, attr_dict):
        dict.__init__(attr_dict)
            
    def refresh(self):
        pass  
    
    def display(self):
        pass
    
class Columned(SmartObjectBase):
    
    def initialize_columns(self):
        '''Initialize column dictionaries to SmartColumn objects.'''
        self.columns = map(lambda c:
                           c if isinstance(c, SmartColumn) \
                           else SmartColumn(sheet = self, attr_dict = c),
                           self.columns)    
    
        
    def get_column(self, field, query):
        
        # Adjustment from one-based to zero-based column indexing.
        if field == 'index':
            query -= 1
        
        try:
            return next(c for c in self.columns if dict(c)[field] == query)
        except StopIteration:
            raise ColumnError(field, query, self.sheet)
        
    def updateColumns(self, newColumnDicts):
        
        # ID space of the columns that should stick around.
        newColIdSpace = [dct['id'] for dct in newColumnDicts]
        
        # Remove columns that have been deleted remotely.
        self.columns = filter(lambda c: c.id in newColIdSpace,
                              self.columns)
        
        # Pair up each column object with a dict of new info about the column.
        updates = map(lambda dct:
                      dict(next([col for col in self.columns \
                                 if col.id == dct['id']], None), dct),
                      newColumnDicts)
        
        # Perform the updates.
        map(lambda (column, info): column.update(info), updates)
        
       
class Rowed(SmartObjectBase):
    
    def __getattr__(self, name):
        if name == 'rows':
            return self.sheet.rows
        else:
            return SmartObjectBase.__getattr__(name)
        
    def initialize_rows(self):
        '''Initialize row dictionaries to SmartRow objects.'''
        self.rows = map(lambda r: 
                        r if isinstance(r, SmartRow) \
                        else SmartRow(sheet = self, attr_dict = r),
                        self.rows)  
        
    def get_row(self, field, query):
        try:
            return next([r for r in self.rows if getattr(r, field) == query])
        except StopIteration:
            raise RowError(field, query, self.sheet)
        
    def updateRows(self, newRowDicts):
        # ID space of the rows that should stick around.
        newRowIdSpace = [dct['id'] for dct in newRowDicts]
        
        # Remove rows that have been deleted remotely.
        self.rows = filter(lambda r: r.id in newRowIdSpace,
                           self.rows)
        
        # Pair up each row object with a dict of new info about the row.
        updates = map(lambda dct:
                      dict(next([row for row in self.rows \
                                 if row.id == dct['id']], None), dct),
                      newRowDicts)
        
        # Perform the updates.
        map(lambda (row, newDict): row.update(newDict), updates)        
  
class SmartObjectArray(list):
    '''A modified array class which allows lazy initialization of Smart Objects.
    SmartObjects exist in the array as dictionaries until they are requested
    via __getitem__.'''    
        
    def __init__(self, obj_class, lst = [], **kwargs):
        list.__init__(self, lst)
        
        def as_object(item):
            if isinstance(item, obj_class):
                return item
            
            item = obj_class(attr_dict = item, **kwargs)
            return item
    
        def get_item(i):
            obj = as_object(list.__getitem__(self, i))
            return obj
        
        self.as_object = as_object
        self.get_item = get_item
        
    def __getitem__(self, i):
        # obj = to_obj(list.__getitem__(self, i))
        # list.__setitem__(self, i, obj)
        return self.get_item(i)
    
    def __iter__(self):
        class SmartIter(iterator):
            def __init__(self, lst):
                list.__init__(list)
            
            def next(self):
                return as_object(it.next())
            
        return SmartIter(list(self))
    
    def to_dict_array(self):
        return map(dict, self)
            
        
# More imports        
from SmartErrors import *
from SmartSocket import *
from Cell import SmartCell
from Column import SmartColumn
from Row import SmartRow
from Sheet import SmartSheet