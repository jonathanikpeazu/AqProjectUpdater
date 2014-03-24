from SmartObjects import *

class ColumnError(BaseException):
    '''This error is thrown when a program tries to access a column that does 
    not exist within a SmartSheet. '''    
    
    def __init__(self, column, sheet):
        
        # check that sheet is a valid smartsheet instance
        if not isinstance(sheet, SmartSheet):
            raise TypeError(
                '''sheet argument passed to ColumnError is not a SmartSheet
                instance.''')
        
        if isinstance(column, int):
            self.msg = '''Index %d out of range for sheet %s. Enter a value 
            between 1 and %d''' \
                % (column, sheet.name, len(sheet.columns))
        elif isinstance(column, str):
            self.msg = 'Sheet %s has no column called %s.' \
                % (sheet.name, column) 
        else:
            raise TypeError(
                '''column argument passed to ColumnError must be a valid int
                or string.''') 
        
        self.column = column
        self.sheet = sheet    
        
    def __str__(self):
        return self.msg 

class RowError(BaseException):
    '''This error is thrown when a program tries to access a row that does not
    exist within a SmartSheet. '''
    def __init__(self, row, sheet):
            if all([isinstance(sheet, SmartSheet), \
                        isinstance(row, SmartRow)]):
                self.row = row
                self.sheet = sheet
            else:
                # TODO: be more descriptive
                raise TypeError()

                
    def __str__(self):
        return 'RowError: Index %d out of range for sheet %s.' \
               % self.column, self.sheet.name
    
class SheetError(BaseException):
    ''' This error is thrown when a program tries to access a sheet that does
    not exist within a SmartSocket. '''
    def __init__(self, sheet, socket):
        if all([isinstance(sheet, SmartSheet), \
                isinstance(socket, SmartSocket)]):
            self.sheet = sheet
            self.socket = socket
        else:
            # TODO: Be more descriptive
            raise TypeError()

    def __str__(self):
        return 'SheetError: User has no sheet called %s.' % self.sheet.name