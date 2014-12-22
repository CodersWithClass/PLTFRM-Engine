level = open('Flippy1.lvl') #Reads from .lvl file
active_objects = [] #Active objects are level commands that aren't comments or blank.
object_list = []#List of processed items ready for import to the PLTFRM engine
import re
filtered_level = [] #Result of basic symbolic parsing
final_level = [] #Final result of tag/advanced parsing
tag = [] #Lists of tags encountered in the order encountered
for lines in level:
    if lines[0] != '' and lines[0] != '#':
        
        lines = re.sub(r'\s', '', lines)
        lines = re.split(':|\n|', lines)
        
        
        if len(lines) > 1:
            lines[1] = re.split(';', lines[1])
        
      #  lines[0] = re.sub(r'\s', '', lines[0])    
                      
        if lines[0] != '': #Adds everything except empty lists
            active_objects.append(lines)
        

for lines in active_objects:
    if len(lines) > 1:
        for num in range(0, len(lines[1])):
                try:
                    lines[1][num] = int(lines[1][num])
                    
                except ValueError:
                    pass


    filtered_level.append(lines)
    
for lines in filtered_level:
    
    if lines[0][0] == '<' and lines[0][1] == '/' and lines[0][-1] == '>':
        print("EndTag: " + lines[0][2:-1])
        if lines[0][2:-1] == tag[-1]:
            del(tag[-1])
        else:
            print("Tag mismatch!")
        
    elif lines[0][0] == '<' and lines[0][-1] == '>':
        print("StartTag: " + lines[0][1:-1])
        tag.append(lines[0][1:-1])
    else:
        for items in tag:
            print(items + ": ")
        print(lines)
        

    #===========================================================================
    # if len(lines[1]) > 1:
    #     for num in range(0, len(lines[1])): #Removes leading spaces in data entries
    #         if lines[1][num][0] == ' ':
    #             lines[1][num] = lines[1][num][1:]
    #             
    # for num in range(0, len(lines)):
    #     if lines[num] == '':
    #         del(lines[num])
    # object_list.append(lines)
    #  
    #===========================================================================
#for items in object_list:
 #   print(items)
#raise TypeError('ERROR: this object required a number in its properties.')