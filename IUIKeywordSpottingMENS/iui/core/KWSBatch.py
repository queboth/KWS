"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 
    
    This is the CLI Batch Module to start a spotting run on mutiple  
    confMats.ark. For a list of possible arguments please start 
    the Programm with the -h argument:
    python -m iui.core.KWSBatch -h

    
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
import os
import logging
import time
import fnmatch
from iui.utils.KeywordSpottingUtils import KeywordSpottingUtils 
from iui.core.KWSOptions import KWSOptions 


"""
Set up logging configuration.

:param run_id: Unique identifier for the run.
:param log_directory: Directory where the log file will be stored (default is current directory).
"""
def setup_logging(run_id, log_directory="."):
    log_file = os.path.join(log_directory, f"{run_id}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.info(f"Log file will be written to: {log_file}")

def log_error(run_id, document_path, error_message):
    logging.error(f"Run ID: {run_id}, Document: {document_path}, Error: {error_message}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Batch processing tool")
    
    # Add the folder_path and run_id arguments (with defaults)
    parser.add_argument("--run_id", default="0001", help="Unique run ID")
    parser.add_argument("--no_reduction", default=False, action="store_true", help="Turn off reduction methods (default False)")
    parser.add_argument("--normalization_power", type=int, default=2, help="Normalization power (default is 2)") 
    parser.add_argument("folder_path", help="Path to the folder containing ConfMats documents")
    parser.add_argument("search_words", help="List of search words, best surround it with apostrophes")
    parser.add_argument("word_confidence", type=float, help="Word confidence as float from 0..1")

    return parser.parse_args()



def process_document(document_path, run_id, search_words, word_confidence, no_reduction, normalization_power, kwsOptions = KWSOptions()):
    # Implement your document processing logic here
    try:
        utils = KeywordSpottingUtils()
    
        kwsOptions.WORD_CONFIDENCE = word_confidence
        kwsOptions.NORMALIZATION_POWER = normalization_power
        kwsOptions.RUN_ID = run_id
        if no_reduction:
            kwsOptions.CLEAN_CTC_COLS = False
            
    
        logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    
        file_path_to_process = document_path
        search_words = search_words
    
        start_time = time.time()
    
        pageDoc = utils.read_page(file_path_to_process, kwsOptions)
    
        res = utils.spot(pageDoc, search_words, kwsOptions)
    
        utils.createFullCSV(pageDoc, res, kwsOptions, True)
    
            # Record the end time
        end_time = time.time()
    
        # Calculate the processing time
        processing_time = end_time - start_time
    
        logging.info(f"Processing time for document:{document_path} was {processing_time} seconds")   
        pass
    except Exception as e:
        # Log the error
        log_error(run_id, document_path, str(e))
        
        

def process_documents_in_folder(folder_path, run_id, search_words, word_confidence, no_reduction, normalization_power, kwsOptions = KWSOptions()):
    for root, _, files in os.walk(folder_path):
        for _ in fnmatch.filter(files, 'ConfMats.ark'):
            process_document(root, run_id, search_words, word_confidence, no_reduction, normalization_power, kwsOptions)


def merge_results(folder_path, run_id):
    all_lines = []
    output_file = os.path.join(folder_path, f"merged_results_{run_id}.csv")
    for root, _, files in os.walk(folder_path):
        for filename in fnmatch.filter(files, f"*results_{run_id}.csv"):
            current_result_csv = os.path.join(root, filename)
            logging.debug(f"Merging in {current_result_csv}")
            with open(current_result_csv, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if not all_lines:
                    all_lines.extend(lines)
                elif lines[0].startswith('SearchWord,SearchWordConf'):
                    all_lines.extend(lines[1:])
    with open(output_file, 'w', encoding='utf-8') as output:
        output.writelines(all_lines)

    logging.info(f"Merged results saved to {output_file}")
            
            



if __name__ == "__main__":
    
    '''
    Print GNU GPL Messages
    '''
    print("The new Keyword Spotting Tool.  Copyright (C) 2023  Raphael Unterweger")
    print("This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.")
    print("This is free software, and you are welcome to redistribute it")
    print("under certain conditions; type `show c' for details.\n")
    
    
    args = parse_arguments()
    setup_logging(args.run_id, args.folder_path)
    process_documents_in_folder(args.folder_path, args.run_id, args.search_words, args.word_confidence, args.no_reduction, args.normalization_power)
    merge_results(args.folder_path, args.run_id)
    
    
    
    