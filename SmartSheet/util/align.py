import copy

testcol1 = [{'name' : 'Jonathan', 'number' : 3235375583},
           {'name' : 'Michael', 'number' : 1234567890},
           {'name' : 'Yonas', 'number' : 1234567890}]

testcol2 = [{'name' : 'Jonathan', 'number' : 1234567890},
           {'name' : 'Michael', 'number' : 3235375583},
           {'name' : 'Yonas', 'number' : 1234567890},
           {'name' : 'Kanye', 'number' : 3235375583}]

def align(column1, column2, key):
    align_outer(column1, column2, key)

def align_outer(column1, column2, key):
    return align_master(column1, column2, mode = 'outer', key = key)

def align_inner(column1, column2, key):
    return align_master(column1, column2, mode = 'inner', key = key)

def align_left(column1, column2, key):
    return align_master(column1, column2, mode = 'left', key = key)

def align_right(column1, column2, key):
    new_key = lambda c1, c2: key(c2, c1)
    return align_master(column1, column2, mode = 'right', key = new_key)
    
def align_master(leftcol, rightcol, mode, key):
    
    if mode == 'right':
        primary_col = copy.copy(rightcol)
        secondary_col = copy.copy(leftcol)
    
    else:
        primary_col = copy.copy(leftcol)
        secondary_col = copy.copy(rightcol)
        
    result = []
    leftovers = copy.copy(secondary_col)
    
    for p_entry in primary_col:

        matches = [s_entry for s_entry in secondary_col \
                    if key(p_entry, s_entry)]
        
        if matches == []:
            if mode == 'right':
                result.append((None, p_entry))
            else:
                result.append((p_entry, None))
        
        else:
            for match in matches:
                if match in leftovers:
                    leftovers.remove(match)
                
                if mode == 'right':
                    result.append((match, p_entry))
                else:
                    result.append((p_entry, match))
                
        
    if mode == 'outer':
        while leftovers != []:
            result.append((None, leftovers.pop()))
    
    elif mode == 'inner':
        result = [(p_entry, s_entry) for (p_entry, s_entry) in result \
                  if s_entry is not None]
        
    return result
        
        
    
        
        
        
