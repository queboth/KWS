"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 
    
    This Module Class contains methods and properties to create overall 
    statistics for KWS runs. eg it is used to count word occurrences.
    
    Copyright (C) 2023  Raphael Unterweger

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


'''
Created on 18.09.2023

@author: run
'''

class KWSStats(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.overall_word_count = 0
        self.document_word_count = 0
        self.page_word_count = 0
        
    
    def increment_overall_word_count(self):
        self.overall_word_count = self.overall_word_count + 1
        
    def increment_document_word_count(self):
        self.document_word_count = self.document_word_count + 1
        
    def increment_page_word_count(self):
        self.page_word_count = self.page_word_count + 1
        
    def increment(self):
        self.increment_overall_word_count()
        self.increment_document_word_count()
        self.increment_page_word_count()


