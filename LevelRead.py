level = open('Flippy1.lvl') #Reads from .lvl file
active_objects = [] #Active objects are level commands that aren't comments or blank.
object_list = []#List of processed items ready for import to the PLTFRM engine
import re
for lines in level:
    if lines[0] != '' and lines[0] != '#':
        lines = re.split(':|\n|', lines)
        
        
        if len(lines) > 1:
            lines[1] = re.split(';', lines[1])
            
                        
        if lines[0] != '':
            active_objects.append(lines)


            
for lines in active_objects:

    if len(lines[1]) > 0:
        for num in range(0, len(lines[1])): #Removes leading spaces in data entries
            if lines[1][num][0] == ' ':
                lines[1][num] = lines[1][num][1:]
    object_list.append(lines)
    
for items in object_list:
    print(items)
#raise TypeError('ERROR: this object required a number in its properties.')
