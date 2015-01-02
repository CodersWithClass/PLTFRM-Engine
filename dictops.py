'''
DictOps: Python Dictionary Operations

Created on Dec 28, 2014

@author: jiaweichen

Copyright (c) 2015 CodersWithClass{}

See below for terms of use

Gives filesystem-like recursive reading and writing in dictionaries.
'''
def changeDir(usr_dict, directory, contents): 
    #Changes the contents of a value in a nested dictionary, given list of nested dicts. 
    #Creates dict entry with provided directory if not found.
    dictionary = dict(usr_dict) #Prevents modifying main-level dictionary by creating an actual copy. Otherwise, it'll create a symbolic link and edit both simultaneously.
    current_dir = directory[0]#Saves the current directory item so it can be deleted from queue (recursive search is length-dependent)
    if len(directory) > 1: #Crawls through list until it's reached the deepest level of the directory--then it creates/modifies contents under the last item's key
        del(directory[0]) #Deletes directory entries as the recursive function dives deeper into directory
        if current_dir not in dictionary:
            dictionary[current_dir] = {} #Creates an empty placeholder if the dict doesn't exist--this is to create an existing directory for function to call 
        dictionary[current_dir] = changeDir(dictionary[current_dir], directory, contents) #Function recurses into itself--function-ception!
    else:
        dictionary[directory[0]] = contents #Creates/modifies dict entry at end of directory path
            
    return dictionary #Returns modified dictionary. 
    #This return value is passed up through all levels of recursion and is recombined with larger and larger sections of the dict. 
    #Think: Russian nesting doll

def doesExist(dictionary, directory):#Checks if dict entry in nested dict exists. 
    #Returns True if found; returns False if not.
    #This function only reads from dict--it doesn't modify it so a symbolic link is okay here.
    if directory[0] in dictionary: #Saves time by checking if the current directory level's value matches nested dict value. 
        #Only continues recursing if values match. Otherwise, returns NoneType.
        if len(directory) > 1:#Crawls through list until it's reached the deepest level of the directory
            current_dir = directory[0]#Saves the current directory item so it can be deleted from queue (recursive search is length-dependent)
            del(directory[0])#Deletes directory entries as the recursive function dives deeper into directory
            result = doesExist(dictionary[current_dir], directory) #Function recurses into itself--function-ception!
        elif len(directory) == 1: #If there's only one item left in directory, and it matches the dictionary value, the directories must match.
            return True 
    else:
        return False #If function has reached deepest level of nested dict and directory doesn't match, returns False.
    
    return result
        
def getAt(dictionary, directory): #Gets value of nested dict's key via the directory provided. Returns value if found, returns NoneType if directory doesn't exist.
    current_dir = directory[0]#Saves the current directory item so it can be deleted from queue (recursive search is length-dependent)
    if len(directory) > 1: #Crawls through list until it's reached the deepest level of the directory
        del(directory[0]) #Deletes directory entries as the recursive function dives deeper into directory
        if current_dir in dictionary: #If directory matches with dictionary's contents, this gives the OK to dive deeper and check further.
            return getAt(dictionary[current_dir], directory) #Function recurses into itself--function-ception!
        else:#Otherwise, if directory doesn't match, it automatically returns NoneType.
            return None
    else:
        if directory[0] in dictionary: #If it's reached the deepest level of nested dict and directories match, it returns value.
            return dictionary[directory[0]]
        else: #If dictionary key doesn't exist at all, there's no way you can retrieve its contents!
            return None
        
        
'''
        And now to get all those legal qualifications out of the way:
        
        
        Permission is hereby granted, free of charge, to any person obtaining a copy     
        of this software and associated documentation files (the "Software"), to deal    
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:
        
        The above copyright notice and this permission notice shall be included in
        all copies or substantial portions of the Software.
        
        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
        THE SOFTWARE.

'''
