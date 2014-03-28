import sys
reload(sys)  # to enable `setdefaultencoding` again
sys.setdefaultencoding("UTF-8")

# CELL_PADDING, MAX_WIDTH
from config import *

# Copy constructors
import copy

# Date/time utilities
from datetime import datetime
from dateutil import parser

# Alignment
from util import align
from util.columntools import column_print

# HTTP requests
import requests
from requests import get
from requests import post
from requests import put

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
    
    def make_header(self, columns = None):
        '''Make a header out of the given columns. Includes title, ID, and 
        index. Used for column printing.'''
        if not columns:
            columns = self.columns
        
        # Leave space to the left for the row number.
        header = [([''] + [col.title for col in columns])]
        header += [([''] + ['Index: %d' % col.index for col in columns])]
        header += [([''] + ['ID: %d' % col.id for col in columns])] 
        
        return header
        
    def get_column(self, field, query):
        try:
            return next(c for c in self.columns if getattr(c, field) == query)
        except StopIteration:
            raise ColumnError(field, query, self.sheet)
        
    def update_columns(self, new_dicts):
        
        # Match up the columns with their new dictionaries.
        align_key = lambda col, new_dict: col.id == new_dict['id']
        updates = align.align_right(self.columns, new_dicts, align_key)
        
        # Update existing rows
        map(lambda (col, new_dict):
            col.update_from_dict(new_dict) if col else None, updates)
        
        '''Put existing, updated rows back into self.rows and instantiate
        new rows'''
        self.columns = [col if col else SmartColumn(new_dict)
                        for (col, new_dict) in updates]
        
        self.columns.sort(key = lambda col: col.id)   
        
       
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
            return next(r for r in self.rows if getattr(r, field) == query)
        except StopIteration:
            raise RowError(field, query, self.sheet)
        
    def update_rows(self, new_dicts):
        
        # Match up the rows with their new dictionaries.
        align_key = lambda row, new_dict: row.id == new_dict['id']
        updates = align.align_right(self.rows, new_dicts, align_key)
        
        # Update existing rows
        map(lambda (row, new_dict):
            row.update_from_dict(new_dict) if row is not None else None, updates)
        
        '''Put existing, updated rows back into self.rows and instantiate
        new rows'''
        self.rows = [row if row else SmartRow(self, new_dict)
                     for (row, new_dict) in updates]
        
        self.rows.sort(key = lambda row: row.id)        
  
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