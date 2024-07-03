"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 
    
    This Class contains Methods for the KWS Tool needed to read and write
    PyLaia and Transkribus Data
    
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
Created on 21.08.2023

@author: Raphael Unterweger
'''

import logging
import os
import traceback
import csv
import re
import pickle
import gc
import numpy as np
import xml.etree.ElementTree as ET
from kaldiio import ReadHelper
from .KeywordSpottingMatrixUtils import *
from Tools.scripts.nm2def import symbols
from pickle import FALSE
from iui.core.KWSOptions import KWSOptions
from iui.utils.KWSStats import KWSStats
from numpy.f2py.auxfuncs import options
from iui.utils.XmlUtils import XMLUtils
from test.test_buffer import numpy_array



class KeywordSpottingUtils(object):
    
    
    
    
    def __init__(self):
        '''
        Constructor
        '''
        # Constructor code here
    
    
    def read_page(self, file_path, kwsOptions:KWSOptions):
        """
        This methods reads the PyLaia and Transkribus Data needed for the 
        spotting, eg: It collects the page-xml pathes, it creates a dictionary
        from the symbols.txt and reads and normalizes the ConfMats.ark.
        It is also capable to dump and read the normalized matrix. 
        """
        
        try:

            
            logging.debug("Processing: " + file_path)
            
            
            
            # Step 2: Loop over XML files in Images subfolder and extract IDs
            logging.debug("reading all xml pathes")
            xml_files = [file_path + "/Images/" + filename for filename in os.listdir(file_path + "/Images") if filename.endswith(".xml")]
            gt_files = []
            if os.path.exists(file_path + "/gt"):
                gt_files = [file_path + "/gt/" + filename for filename in os.listdir(file_path + "/gt") if filename.endswith(".xml")]
            
             
            # Step 3: Read symbols from symbols.txt and create a symbols dictionary
            logging.debug("reading symbols.txt")
            symbols_dict = {}
            ctc_index = -1
            space_index = -1
            with open(file_path + "/symbols.txt", 'r', encoding='utf-8') as symbols_txt:
                for line in symbols_txt:
                    char, index = line.strip().split('\t')
                    if (char == '<ctc>'):
                        ctc_index = int(index)
                    if (char == '<space>'):
                        symbols_dict[int(index)] = ' '
                        space_index = int(index)
                    else:
                        symbols_dict[int(index)] = char
            
            
            # Step 1: Read matrices from ARK file
            logging.debug("reading ark file ConfMats.ark")
            query = kwsOptions.search_words
            all_query_indices = get_indices(symbols_dict, query, kwsOptions.CLEAN_NONSEARCHWORD_CHARS)
            if kwsOptions.CLEAN_NONSEARCHWORD_CHARS:
                all_query_indices = merge_and_clean(all_query_indices) 
                symbols_dict = create_corrected_symbols_dict(symbols_dict, all_query_indices) 
            
            normalized_path = file_path+'/ConfMats_' + generate_hex_hash("".join(symbols_dict.values())) + '.dmp'
            if kwsOptions.USE_CONFMAT_DUMP and os.path.exists(normalized_path):
                with open(normalized_path, 'rb') as file:
                    conf_mats_by_lineid = pickle.load(file)
            else:
                normal_max = kwsOptions.NORMALIZATION_CAP
                conf_mats_by_lineid = {}
                with ReadHelper('ark:'+file_path+'/ConfMats.ark') as reader:
                    line_counter = 0
                    for key, numpy_array_full in reader:
                        numpy_array = numpy_array_full
                        if kwsOptions.CLEAN_NONSEARCHWORD_CHARS:
                            numpy_array = [[element for idx, element in enumerate(row) if idx in all_query_indices or idx == ctc_index or idx == space_index] for row in numpy_array_full ]
                        max_val = np.min(numpy_array)
                        normalization_cap = max_val
                        if kwsOptions.USE_NORMALIZATION_CAP:
                            normalization_cap = normal_max
                        normalization_power = kwsOptions.NORMALIZATION_POWER
                        result_matrix = [[(1 - (max(cell, normal_max) / normalization_cap))**normalization_power for cell in row] for row in numpy_array]
                        conf_mats_by_lineid[key] = result_matrix
                        line_counter += 1
                        if line_counter % 100 == 0:
                            logging.debug(f"lines normalized: {line_counter}")
                            gc.collect()
                if kwsOptions.CREATE_CONFMAT_DUMP:
                    with open(normalized_path, 'wb') as file:
                        pickle.dump(conf_mats_by_lineid, file)
                    
                    
                    
                        
            
            
            
            return { "path": file_path, "xml_files": xml_files, "conf_mats":conf_mats_by_lineid, "symbols_dict":symbols_dict, "gt_files": gt_files, "has_gt": (len(gt_files) > 0)}
            
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")


        return { "xml_files": None, "conf_mats":None, "symbols_dict":None}

    def spot(self, htr_in, search_value,  options:KWSOptions, stats:KWSStats = KWSStats()):
        """
        This method will start the spotting for one given page-doc read by read_page-Method
        """
        
        
        res = []
        
        # Read and process the file content
        conf_mats = htr_in['conf_mats']
        symbols = htr_in['symbols_dict']
        
        #map searchword characters to given symbol indices
        all_search_value_indexes = get_indices(symbols, search_value)
        
        stats.document_word_count = 0
        previous_page_id = None
        for key in conf_mats:
            logging.debug(f"processing line: {key}")
            page_key = key.split('.')[0]
            #line_key = key.split('.')[1]


            #if key == '34854534.r1l1':
            #    logging.debug(f"BREAK on: {key}")
            #    break

            
            if previous_page_id == None or previous_page_id != page_key:
                stats.page_word_count = 0
                previous_page_id = page_key
            
            #just for debugging
            #if key != '14262.line_275f0a60-e39b-4f62-8b5a-6979234faa25':
            #    logging.debug(f"DEBUG MODE: skipping  line: {key}")
            #    continue
            
            
            #read current conf_mat
            conf_mat = np.abs(conf_mats[key])
            #line_best = find_best(conf_mat, symbols)
            #self.writeBest(htr_in['path'], key, line_best)
            #print(line_best)
            #print(conf_mat)

            #split matrix at space locations
            space_id = getCharIdFromSymbols(symbols, " ")
            sub_mats = split_matrix(conf_mat, space_id)
            
            line_pos = 1;
            
            for mat in sub_mats:
                act_key = key + '.' + str(line_pos)
                logging.debug(f"processing line: {act_key}")
                
                if (mat.shape[0] != 0):
                    best = find_best(mat, symbols)
                    stats.increment()
                    for search_value_indexes in all_search_value_indexes:
                        l = len(search_value_indexes)
                        #automatically calculate lowest possible character threshold
                        options.CHARACTER_TRESHOLD = max(options.WORD_CONFIDENCE * l - (l - 1), 0)
                        logging.debug(f"min character confidence determined by word_confidence: {options.CHARACTER_TRESHOLD}")
                
                        if mat.shape[0] > len(search_value_indexes):
                            valid_occurrences = calculate_confidence_for_occurrences(mat, act_key, search_value_indexes, symbols, options)

                            if options.ADJUST_CONFIDENCE_BY_WORD_LENGTH:
                                valid_occurrences = self.adjust_confidence_by_best_lenght(valid_occurrences, best, options)
                            
                            res.extend(self.mapResult(valid_occurrences, options, stats, htr_in, best))
                            
                            for res_key in valid_occurrences:
                                #TODO: write output handler
                                occurrence = valid_occurrences[res_key]
                                #result_str = f"Occurrence found: {occurrence['asstring']}  with Confidence: {occurrence['confidence']} at {occurrence['at']}  for best: {best}"
                                result_str = f"Occurrence found: {occurrence['asstring']}  at {occurrence['at']}  for best: {best}"
                                if options.DEBUG:
                                    logging.info(result_str)
                                if options.PRINT_RESULTS_TO_CONSOLE:
                                    print(result_str)
                                    
                                

                line_pos = line_pos + 1
        
        #if len(res) > 0 and options.OUTPUT_EVALUATION_CSV:
        #    self.writeCSV(htr_in['path'] + f"\\results_{options.RUN_ID}.csv", res)

        return res
    
    
    def writeBest(self, path, key, line_best):
        """
        This method will export all HTR best values.
        """
        with open(path+'/besties.csv', mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)  
            writer.writerow([key,line_best[0], line_best[1]])
            csv_file.close()    
      
    def createFullCSV(self, htr_in, res, options:KWSOptions, delete_old_csv = False):
        """
        Wrapper method to create the result CSV.
        """
        output_path = htr_in['path'] + f"\\results_{options.RUN_ID}.csv"
        if delete_old_csv and os.path.exists(output_path):
            os.remove(output_path)
        
        if len(res) > 0 and options.OUTPUT_CSV:
            self.writeCSV(output_path, res)
  
            
    def adjust_confidence_by_best_lenght(self, valid_occurrences, best, options:KWSOptions):
        """
        This method is used to reduce the confidecne of the found word, when it differs 
        to much from the best value by length.
        """
        best_len = len(best[0])
        to_remove_keys = []
        for res_key in valid_occurrences:
            occurrence = valid_occurrences[res_key]
            hit_lenght = len(occurrence['asstring'][0])
            if abs(best_len - hit_lenght) > 2:
                factor = 1.0
                if best_len > hit_lenght:
                    factor = (hit_lenght + 1) / best_len
                else:
                    factor = (best_len + 1)/ hit_lenght
                occurrence['asstring'] = [occurrence['asstring'][0], occurrence['asstring'][1] * factor, occurrence['asstring'][2] * factor, occurrence['asstring'][3] * factor,]
                occurrence['confidence'] = occurrence['confidence'] * factor
                if occurrence['confidence'] < options.WORD_CONFIDENCE:
                    to_remove_keys.append(res_key)
                else:
                    valid_occurrences[res_key] = occurrence
        for key in to_remove_keys:
            del valid_occurrences[key]
        return valid_occurrences
        
        
    def mapResult(self, valid_occurrences, options:KWSOptions, stats, htr_in, best = None):
        """
        This method will map all the values from the found results dict to a dict containing 
        the CSV field names.
        """
        
        res = []
        
        utils = XMLUtils()
        page_dict = {}
        line_dict = {}
        if options.OUTPUT_FORMAT_ADD_LINE_SNIPPETS:
            page_dict = utils.createMetadataDict(htr_in["xml_files"])
            line_dict = utils.createTextLineDict(htr_in["xml_files"])
            
        
        #convert result list
        for res_key in valid_occurrences:
            #TODO: write output handler
            sub_res = {}
            occurrence = valid_occurrences[res_key]
            page_id = occurrence['at'].split('.')[0]
            line_id = occurrence['at'].split('.')[1]
            word_id = occurrence['at'].split('.')[2]
            page_number = page_dict[page_id][0]
            doc_id = page_dict[page_id][2]
            
            sub_res["SearchWord"] = occurrence['asstring'][0]
            sub_res["SearchWordConf"] = occurrence['asstring'][1]
            
            if options.OUTPUT_FORMAT_ADD_MIN_MAX_CONFIDENCES:
                sub_res["SearchWordMinConf"] = occurrence['asstring'][2]
                sub_res["SearchWordMaxConf"] = occurrence['asstring'][3]
            
            sub_res["doc_id"] = doc_id
            sub_res["page_number"] = page_number
            sub_res["page_id"] = page_id
            sub_res["line_id"] = line_id
            sub_res["word_id"] = word_id
             
            if options.OUTPUT_FORMAT_ADD_BEST and best:
                sub_res["BestWord"] = best[0]
                sub_res["BestWordConf"] = best[1]
                if options.OUTPUT_FORMAT_ADD_MIN_MAX_CONFIDENCES:
                    sub_res["BestWordMinConf"] = best[2]
                    sub_res["BestWordMaxConf"] = best[3]

            if options.OUTPUT_FORMAT_ADD_CAP:
                sub_res["NormalizationCap"] = options.NORMALIZATION_CAP

            if options.OUTPUT_FORMAT_ADD_POWER:
                sub_res["NormalizationPower"] = options.NORMALIZATION_POWER

            if options.OUTPUT_FORMAT_ADD_TRESHOLD:
                sub_res["WordThreshold"] = options.WORD_CONFIDENCE


            if stats != None:
                sub_res["OverallWordCount"] = stats.overall_word_count
                sub_res["DocumentWordCount"] = stats.document_word_count
                sub_res["PageWordCount"] = stats.page_word_count

            if options.OUTPUT_FORMAT_ADD_DOC_PATH:
                sub_res["PyLaiaFolder"] = os.path.basename(htr_in['path'])

                
            if options.OUTPUT_FORMAT_ADD_LINE_SNIPPETS:
                sub_res["snippet"] = self.createSnippetEntry(occurrence, page_dict, line_dict)
            
            res.append(sub_res)
        
        
        
        return res
            
    def createSnippetEntry(self, occurrence, page_dict, line_dict):
        """
        This method will create the line snippet link for the CSV 
        """
        current_location = occurrence['at']
        page_id = current_location.split('.')[0]
        line_id = current_location.split('.')[1]
        snippet_url = page_dict[page_id][1]
        coords = line_dict[line_id][0]
        res_url = snippet_url + "&crop=" + coords
        return res_url
    
        
        
         
            
    def writeCSV(self, path, data):   
        """
        This method will write the final CSV results
        """
        with open(path, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)  
            
            header = data[0].keys()
            writer.writerow(header)
            
            for row in data:
                writer.writerow(row.values())
                
            csv_file.close()
        

    def createFrequencyListFromPageDoc(self, pageDoc, kwsOptions:KWSOptions):
        """
        This method will create a word frequencies list for all words in the
        given page-doc gt-folder. This was used for evaluation.
        """
        logging.debug(f"creating frequency-list for {pageDoc['path']}")
        gt_files = pageDoc['gt_files']
        namespace = {'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
        word_counts = {} 
        for gt_file in gt_files:
            page_xml = ET.parse(gt_file)
            root = page_xml.getroot()
            
            # Define the specific element type you want to loop over (e.g., 'element_type')
            xpath = './/ns:TextLine/ns:TextEquiv/ns:Unicode'
            
            # Loop over elements of the specific type
            for element in root.findall(xpath, namespaces=namespace):
                # Process the elements here
                #print(element.tag, element.text)
                words = element.text.split()
                for word in words:
                    
                    cleaned_word = self.clean_word(word)
                    
                    if len(cleaned_word) < 4:
                        continue
                    if cleaned_word in word_counts:
                        word_counts[cleaned_word] += 1
                    else:
                        word_counts[cleaned_word] = 1
        
        res = [{"keyword": word, "count": count} for word, count in word_counts.items()]
        
        return res    
    
    
    
    def createFrequencyListFromMiniOCR(self, path_to_mini_ocr, kwsOptions):
        """
        Same as createFrequencyListFromPageDoc, but it will count the words form the
        miniOCR files. Used to compare the F1 Measure between these two approaches.
        """
        logging.debug(f"creating frequency-list for {path_to_mini_ocr}")
        mini_ocr_files =  [path_to_mini_ocr + "/" + filename for filename in os.listdir(path_to_mini_ocr) if filename.endswith(".xml")]
        word_counts = {} 
        for mini_ocr_file in mini_ocr_files:
            mini_ocr_xml = ET.parse(mini_ocr_file)
            root = mini_ocr_xml.getroot()
            
            # Define the specific element type you want to loop over (e.g., 'element_type')
            xpath = './/w'
            
            # Loop over elements of the specific type
            for element in root.findall(xpath):
                # Process the elements here
                variants = element.text.split('⇿')
                for variant in variants:
                    
                    cleaned_variant = self.clean_word(variant)
                    
                    if len(cleaned_variant) < 4:
                        continue
                    if cleaned_variant in word_counts:
                        word_counts[cleaned_variant] += 1
                    else:
                        word_counts[cleaned_variant] = 1
        
        res = [{"keyword": variant, "count": count} for variant, count in word_counts.items()]
        
        return res    
            
        
    def clean_word(self, word):
        """
        This method will remove special characters from the given string
        """
        res = re.sub(r'[^a-zA-Z0-9\s]', '', word)
        return res
        
    
