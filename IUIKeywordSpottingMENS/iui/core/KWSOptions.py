"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 
    
    This Module hold all the Options for the KWS Tool and also a method 
    to parse CLI argumnets and map them to the Options.
    
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


import argparse


class KWSOptions(object):
    '''
    classdocs
    '''
    

    def __init__(self, auto_parse_args = False):
        #tool process options
        self.directory_path = "." #main start path, this folder should contain a ConfMats.ark
        self.search_words = "Johan" #words to spot in the ConfMats 
        self.DEBUG = False  # the Debug-Function has a problem while analysing the confidence List
        self.LOG_LEVEL = "FATAL"  # the logging Log-Level
        self.LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s' # logging entry format
        self.PRINT_RESULTS_TO_CONSOLE = False  # the Debug-Function has a problem while analysing the confidence List
        self.RUN_ID = "0001" # RUN_ID will be used as part of the output file name
        
        self.CHARACTER_TRESHOLD = 0.98 #this determines quality and performance heavily
        self.WORD_CONFIDENCE = 0.95 #to filter resulting words by confidence, it will also determine the max char-Threshold
        self.LIMIT_RESULTS = 10 #to limt the result list
        self.CLEAN_CTC_DOUBLE_CHARACTERS = False #when true, this will improve performace drastically, but will lead to siglty lower confidence value. The number of results should stay the same
        self.CLEAN_CTC_COLS = True # when true, ctc windows will be removed from the ConfMats in beforehand => Good Speed, Proper Confidences
        self.CLEAN_NONSEARCHWORD_CHARS = True
        self.NORMALIZATION_CAP = -65 #Confidences in the PyLaia ConfMat ranging from 0 to  -200 up to -500
        self.NORMALIZATION_POWER = 2 #ConfMat will be powered during normalization, the highe this number gets the more the higher confidences will be streched and the lower confidences will be compressed 
        self.USE_NORMALIZATION_CAP = False #apply normalization cap
        self.ADJUST_CONFIDENCE_BY_WORD_LENGTH = True #if the spotted word length differs too much from the bestword found, than the confidence for the spotted word will be reduced
        self.REMOVE_HTR_CONTROL_SYMBOLS = True #sometimes there is a <$> in the HTR Output, not the Symbols List, these will be removed
        self.USE_CONFMAT_DUMP = True #Use the dumped ConfMat for quicker repeated searches
        self.CREATE_CONFMAT_DUMP = True #ConfMat will be dumped after normalization
        
        #planned options for output format
        self.OUTPUT_CSV = True # create output CSV
        self.OUTPUT_EVALUATION_CSV = True #create Evaluation CSV, onlywritten when GT is present in the PyLaia Document 'gt'
        self.OUTPUT_FORMAT_ADD_MIN_MAX_CONFIDENCES = True # will add min and max confidence to the hits
        self.OUTPUT_FORMAT_ADD_BEST = True #add the original htr result
        self.OUTPUT_FORMAT_ADD_TRESHOLD = False #add used search word confidence, only usefull for evaluation
        self.OUTPUT_FORMAT_ADD_CAP = False # add normalization cap, only usefull for evaluation
        self.OUTPUT_FORMAT_ADD_POWER = True # add normalization power 
        self.OUTPUT_FORMAT_ADD_LINE_SNIPPETS = True #add entire line text plus a link to a image snippet of that line 
        self.OUTPUT_FORMAT_ADD_WORD_COUNTS = True # add word counts
        self.OUTPUT_FORMAT_ADD_DOC_PATH = True # add local doc path, mainly usefull for batch processing
        
        #planned options for stability
        self.INDICES_LIMIT = 4000000000 #if number of indices exceed this limit, following actions can be forced 
        self.STOP_ON_LIMIT_EXCEED = False #will exit the programm when limit is reached
        self.WARN_ON_LIMIT_EXCEED = True # displays a warning when limit is reached
        
        self.SHOWW = False
        self.SHOWC = False
        
        if auto_parse_args:
            self.parse_args()
        
    

    def parse_args(self):
        parser = argparse.ArgumentParser(description="Keyword Spotting Tool (by run IUI)")

        # Define command-line options
        parser.add_argument("directory_path", nargs=argparse.REMAINDER, help="Path to a directory with a PyLaia ConfMat. It has to be the last CLI argument.")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logs (default False)")
        parser.add_argument("-l", "--log_level", help="Set a Log Level (default WARN, accepts: FATAL,INFO,DEBUG)")
        parser.add_argument("-lf", "--logging_format", help="Set a Log Level (default WARN, accepts: FATAL,INFO,DEBUG)")
        parser.add_argument("-r", "--run_id", help="Set the RUN_ID (Default: 0001)")
        parser.add_argument("-p", "--print_results_to_console", action="store_true", help="Print Results to std-out")
        parser.add_argument("-q", "--query", help="Comma separated List of search words")
        parser.add_argument("-wc", "--word_confidence", type=float, help="Set WORD_CONFIDENCE (Default: 0.95)")
        parser.add_argument("-lr", "--limit_results", type=int, help="Set LIMIT_RESULTS will limit the number of result (default 4000000000)")
        parser.add_argument("-cd", "--clean_ctc_double_characters", action="store_true", help="Enable CLEAN_CTC_DOUBLE_CHARACTERS, when true, this will improve performace drastically, but will lead to siglty lower confidence values. The number of results should nearly stay the same.")
        parser.add_argument("-cc", "--clean_ctc_cols", action="store_true", help="Enable CLEAN_CTC_COLS, this Option will remove all CTC Windows from the matrix in beforehand. This will improve performance drastically and confidences stay nearly the same as without, because of the nature of the PyLaia ConfMat.")
        parser.add_argument("-cnsc", "--clean_nonsearchword_chars", action="store_true", help="Enable CLEAN_NONSEARCHWORD_CHARS, this Option will remove all Non-SearchWord-Character-Rows from the confidence matrix and by that will reduce the memory consumption, but eliminates the possibillity to carry over the correct confidence value for the best value written to the Page-XML ")
        parser.add_argument("-np", "--normalization_power", type=int, help="Set NORMALIZATION_POWER (default 8) This will stretch the ConfMats confidences, which helps to find a good word confidence")
        parser.add_argument("-nc", "--normalization_cap", type=int, help="Set NORMALIZATION_CAP. This will raise very low confidences in the matrix and can be used for two reasons: a) it will stretch the confidences and makes finding a good threshold easier and b) gives us the possibility to raise very low characters back into scope")
        parser.add_argument("-unc", "--use_normalization_cap", action="store_true", help="Enable USE_NORMALIZATION_CAP")
        parser.add_argument("-awl", "--adjust_confidence_by_word_length", action="store_true", help="Enable ADJUST_CONFIDENCE_BY_WORD_LENGTH. This will adjust the result confidence by the length difference between the found word and the best word. Has nearly no effect when using CLEAN_CTC_COLS")
        parser.add_argument("-rhc", "--remove_htr_control_symbols", action="store_true", help="Enable REMOVE_HTR_CONTROL_SYMBOLS, some models has learend controlsymbols like <$>. This option will just remove them from the result.")
        parser.add_argument("-oc", "--output_csv", action="store_true", help="Enable OUTPUT_CSV, default equals enabled")
        #parser.add_argument("-oec", "--output_evaluation_csv", action="store_true", help="Enable OUTPUT_EVALUATION_CSV")
        parser.add_argument("-oafmm", "--output_format_add_min_max_confidences", action="store_true", help="Enable OUTPUT_FORMAT_ADD_MIN_MAX_CONFIDENCES, will add min and max confidence values for hits and best")
        parser.add_argument("-oafbest", "--output_format_add_best", action="store_true", help="Enable OUTPUT_FORMAT_ADD_BEST, will add the best value from the ConfMat to the CSV")
        parser.add_argument("-oaft", "--output_format_add_threshold", action="store_true", help="Enable OUTPUT_FORMAT_ADD_THRESHOLD, will add the word confidence to the CSV")
        parser.add_argument("-oafc", "--output_format_add_cap", action="store_true", help="Enable OUTPUT_FORMAT_ADD_CAP, will add normalization cap to the CSV")
        parser.add_argument("-oafls", "--output_format_add_line_snippets", action="store_true", help="Enable OUTPUT_FORMAT_ADD_LINE_SNIPPETS, will add a link to the line snippet")
        parser.add_argument("-oafwc", "--output_format_add_word_count", action="store_true", help="Enable OUTPUT_FORMAT_ADD_WORD_COUNT, will add word count stats")
        parser.add_argument("-oafdp", "--output_format_add_doc_path", action="store_true", help="Enable OUTPUT_FORMAT_ADD_DOC_PATH, will add the page document path to the output CSV")
        parser.add_argument("-il", "--indices_limit", type=int, help="Set INDICES_LIMIT. The number of possible combinations will be calculated in beforhand and can be used to skip processing of problematic lines.")
        parser.add_argument("-sol", "--stop_on_limit_exceed", action="store_true", help="Enable STOP_ON_LIMIT_EXCEED")
        parser.add_argument("-wol", "--warn_on_limit_exceed", action="store_true", help="Enable WARN_ON_LIMIT_EXCEED")
        parser.add_argument("-ucd", "--use_confmat_dump", action="store_true", help="This will use the dumped confmat and with that speed up repeated searches")
        parser.add_argument("-ccd", "--create_confmat_dump", action="store_true", help="This will dump the normalized confmat")

        
        args = parser.parse_args()
        
        self.parsed_args = args
        self.parser = parser
        
        
 
        # Update options based on parsed arguments
        self.directory_path = args.directory_path[0] if args.directory_path else self.directory_path
        self.DEBUG = args.debug
        self.LOG_LEVEL = args.log_level if args.log_level else self.LOG_LEVEL
        self.LOGGING_FORMAT = args.logging_format if args.logging_format else self.LOGGING_FORMAT
        self.RUN_ID = args.run_id if args.run_id else self.RUN_ID
        self.PRINT_RESULTS_TO_CONSOLE = args.print_results_to_console if args.print_results_to_console else self.PRINT_RESULTS_TO_CONSOLE
        self.search_words = args.query if args.query else self.search_words
        self.WORD_CONFIDENCE = args.word_confidence if args.word_confidence else self.WORD_CONFIDENCE
        self.LIMIT_RESULTS = args.limit_results if args.limit_results else self.LIMIT_RESULTS
        self.CLEAN_CTC_DOUBLE_CHARACTERS = args.clean_ctc_double_characters or self.CLEAN_CTC_DOUBLE_CHARACTERS
        self.CLEAN_CTC_COLS = args.clean_ctc_cols or self.CLEAN_CTC_COLS
        self.CLEAN_NONSEARCHWORD_CHARS = args.clean_nonsearchword_chars or self.CLEAN_NONSEARCHWORD_CHARS
        self.NORMALIZATION_CAP = args.normalization_cap if args.normalization_cap else self.NORMALIZATION_CAP
        self.USE_NORMALIZATION_CAP = args.use_normalization_cap or self.USE_NORMALIZATION_CAP
        self.ADJUST_CONFIDENCE_BY_WORD_LENGTH = args.adjust_confidence_by_word_length or self.ADJUST_CONFIDENCE_BY_WORD_LENGTH
        self.REMOVE_HTR_CONTROL_SYMBOLS = args.remove_htr_control_symbols or self.REMOVE_HTR_CONTROL_SYMBOLS
        self.OUTPUT_CSV = args.output_csv or self.OUTPUT_CSV
        self.OUTPUT_FORMAT_ADD_MIN_MAX_CONFIDENCES = args.output_format_add_min_max_confidences or self.OUTPUT_FORMAT_ADD_MIN_MAX_CONFIDENCES
        self.OUTPUT_FORMAT_ADD_BEST = args.output_format_add_best or self.OUTPUT_FORMAT_ADD_BEST
        self.OUTPUT_FORMAT_ADD_TRESHOLD = args.output_format_add_threshold or self.OUTPUT_FORMAT_ADD_TRESHOLD
        self.OUTPUT_FORMAT_ADD_CAP = args.output_format_add_cap or self.OUTPUT_FORMAT_ADD_CAP
        self.OUTPUT_FORMAT_ADD_LINE_SNIPPETS = args.output_format_add_line_snippets or self.OUTPUT_FORMAT_ADD_LINE_SNIPPETS
        self.OUTPUT_FORMAT_ADD_WORD_COUNTS = args.output_format_add_word_count or self.OUTPUT_FORMAT_ADD_WORD_COUNTS
        self.OUTPUT_FORMAT_ADD_DOC_PATH = args.output_format_add_doc_path or self.OUTPUT_FORMAT_ADD_DOC_PATH
        self.INDICES_LIMIT = args.indices_limit if args.indices_limit else self.INDICES_LIMIT
        self.STOP_ON_LIMIT_EXCEED = args.stop_on_limit_exceed or self.STOP_ON_LIMIT_EXCEED
        self.WARN_ON_LIMIT_EXCEED = args.warn_on_limit_exceed or self.WARN_ON_LIMIT_EXCEED
        self.USE_CONFMAT_DUMP = args.use_confmat_dump or self.USE_CONFMAT_DUMP
        self.CREATE_CONFMAT_DUMP = args.create_confmat_dump or self.CREATE_CONFMAT_DUMP
        
        if len(args.directory_path) == 2:
            if args.directory_path[0] == 'show' and args.directory_path[1] == 'c':
                self.SHOWC = True
            if args.directory_path[0] == 'show' and args.directory_path[1] == 'w':
                self.SHOWW = True
        
