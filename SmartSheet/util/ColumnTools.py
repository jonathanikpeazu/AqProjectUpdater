import copy

DEFAULT_PADDING = 2
DEFAULT_FILL = ' '

def getColumnWidths(rows):
    '''Takes a row as a list, or a set of rows as a nested list and returns a 
    list of the widths of the widest element in each column. 
    
    Single row:
    [1, ab] -> [1, 2]
    
    Multiple rows:
    [[1, 'abc'], [2, 'defg']], where [1, 'ab'] is a row and [1, 2] is a
    column. This would return [1, 4]. Wide cells are truncated to 
    MAX_CELL_WIDTH'''
    
    '''If the data passed in is a single row, just grab the width of each value
    and return.'''
    if all(map(lambda value: not isinstance(value, list), rows)):
        columnWidths = map(lambda value: len(str(value)), rows)
        return columnWidths
          
    else:
        # Turn the rows into columns:
        columns = zip(*rows)
        
        '''Functional transformations:
        1) [['apples', 'sauce'], ['hello', 'goodbye']] -> [[6, 5], [5, 7]]
        2) [[6, 5], [5, 7]] -> [6, 7]
        3) Truncate lengths to MAX_CELL_WIDTH'''
        columnWidths = \
            map(max, \
                map(lambda c: map(lambda colVal: len(str(colVal)), c), \
                    columns))
        
        return columnWidths

def truncateRows(rows, maxWidth):
    '''Takes a two-dimensional list, where each inner list represents a row,
    and returns a new 2D list in which the length of each value is at most
    maxWidth. Does not alter the original array.
    
    Ex:   
    lst = [['blah blah', 'hello'], ['good', 'bye']]
    truncateRows(lst, 5) RETURNS:
    [['blah ', 'hello'], ['blah', ''], ['good', 'bye']]'''
    
    # Copy the row array so that we do not alter the original array.
    rows = copy.copy(rows)
    
    '''Since we will be adding new rows while iterating, we must keep track of
    the growing number of rows while iterating. '''
    numRows = len(rows)
    i = 0
    while i < numRows:
        
        newRow = map(lambda cellVal: cellVal[maxWidth:], rows[i])
        
        '''Check if there is any spillover. If so, add a new row after the 
        truncated row.'''
        if any(newRow):
            truncRow = map(lambda cellVal: cellVal[:maxWidth], rows[i])
            rows[i] = truncRow
            rows.insert(i + 1, newRow)
            numRows += 1
            break
        
        i += 1
        
    return rows

def columnPrint(data, header = None, maxWidth = None, \
                delimiter = '|', padding = 2, fillChar = ' '):
    '''Takes an array of rows in nested list representation, 
    automatically detects the width of each column, and prints the rows to fit 
    these column widths.
    
    Arguments:
    
    1. data: [# row 1: [1, 'apple'], #row 2: [2, 'banana']]
    
    2. header: A column header as a single row. Must be the same length as each
    column.
    
    3. maxWidth: The maximum display width of a column
    
    4. delimiter: The character which will be placed between columns.
    
    5. padding: the additional spaces padding the right side of each column.
    
    6. fillChar: the character used to pad out each column.
    
    With delimiter '|', padding 2 and fillChar ' ', the above input looks like:
       
       |1  |a       |
       |2  |banana  |
    '''
    
    # If the data has been passed in as a single row, convert it to a row array.
    if not all(map(lambda d: isinstance(d, list), data)):
        data = [data]
    else:
        '''Otherwise, if we have many rows, make sure each row has the same 
        number of columns.'''
        columns_per_row = map(len, data)
        
        if max(columns_per_row) != min(columns_per_row):
            print map(len, data)
            print data
            raise TypeError('All rows must have the same number of columns.')
        
    data = map(lambda row: map(str, row), data)
        
    # Get the width of each column without headers.
    dataWidths = getColumnWidths(data)
    
    # If any of the columns is too wide, truncate.
    if maxWidth and any(map(lambda w: w > maxWidth, dataWidths)):
        data = truncateRows(data, maxWidth)
        dataWidths = map(lambda w: min(w, maxWidth), dataWidths)
    
    # Header processing
    if not header:
        rows = data
        columnWidths = dataWidths 
    else:
        if not all(map(lambda h: isinstance(h, list), header)):
            header = [header]
        
        header = map(lambda row: map(str, row), header)
        headerWidths = getColumnWidths(header)
        
        # If any of the header columns is too wide, truncate.
        if maxWidth and any(map(lambda w: w > maxWidth, headerWidths)):
            header = truncateRows(header, maxWidth)
            headerWidths = map(lambda w: min(w, maxWidth), columnWidths)
            
        columnWidths = map(max, zip(dataWidths, headerWidths))
        
        # Insert a line below the header out of dashes
        lowerLine = map(lambda w: '-' * (w + padding), columnWidths)
        header.append(lowerLine)
        
        # Combine the header with the rest of the data.
        rows = header + data
    
     
    # Pad out each row to the width of its column, plus padding, using fillChar.
    paddedRows = map(lambda row: \
                     map(lambda value, width: \
                         value.ljust(width + padding, fillChar),\
                         row, columnWidths), \
                     rows)
    
    # Make a top line out of underscores and a bottom line out of dashes.
    upperLine = map(lambda w: '_' * (w + padding), columnWidths)
    upperLine = '_' + '_'.join(upperLine) + '_'
    
    lowerLine = map(lambda w: '-' * (w + padding), columnWidths)
    lowerLine = '-' + '-'.join(lowerLine) + '-'
    
    # Print everything
    print upperLine
    for r in paddedRows:
        print(delimiter + delimiter.join(r) + delimiter)
    print lowerLine