"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 
    
    This is the CLI Module to start a spotting run on a single 
    confMats.ark. For a list of possible arguments please start 
    the Programm with the -h argument:
    python -m iui.cli.KWS -h
    
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



import logging
import time
from iui.utils.KeywordSpottingUtils import KeywordSpottingUtils 
from iui.core.KWSOptions import KWSOptions 




if __name__ == '__main__':
    start_time = time.time()
    
    '''
    Parameters / CLI arguments
    '''
    utils = KeywordSpottingUtils()
    kwsOptions = KWSOptions()
    kwsOptions.parse_args()


    '''
    Set log-level from KWS Options
    '''    
    if kwsOptions.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format=kwsOptions.LOG_FORMAT)
    else:
        match kwsOptions.LOG_LEVEL:
            case "FATAL":  
                logging.basicConfig(level=logging.FATAL, format=kwsOptions.LOGGING_FORMAT)
            case "INFO":  
                logging.basicConfig(level=logging.INFO, format=kwsOptions.LOGGING_FORMAT)
            case "DEBUG":  
                logging.basicConfig(level=logging.DEBUG, format=kwsOptions.LOGGING_FORMAT)
            case _:  
                logging.basicConfig(level=logging.WARN, format=kwsOptions.LOGGING_FORMAT)
            

    '''
    Print GNU GPL Messages
    '''
    print("The new Keyword Spotting Tool.  Copyright (C) 2023  Raphael Unterweger")
    print("This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.")
    print("This is free software, and you are welcome to redistribute it")
    print("under certain conditions; type `show c' for details.\n")

    if kwsOptions.SHOWW:
        print("IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.")
        exit()
        
    if kwsOptions.SHOWC:
        print("This is the new Keyword Spotting Tool, which spot's search terms") 
        print("in the PyLaia ConfMats.ark. ")
    
        print("Copyright (C) 2023  Raphael Unterweger")

        print("This program is free software: you can redistribute it and/or modify")
        print("it under the terms of the GNU General Public License as published by")
        print("the Free Software Foundation, either version 3 of the License, or")
        print("(at your option) any later version.")

        print("This program is distributed in the hope that it will be useful,")
        print("but WITHOUT ANY WARRANTY; without even the implied warranty of")
        print("MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
        print("GNU General Public License for more details.")

        print("You should have received a copy of the GNU General Public License")
        print("along with this program.  If not, see <https://www.gnu.org/licenses/>.")
        exit()
        

        
    '''
    read essential arguments from kwsOptions for logging
    '''
    file_path_to_process = kwsOptions.directory_path
    search_words = kwsOptions.search_words
    logging.info(f"Start spotting of '{search_words}' in {file_path_to_process} ")


    '''
    read paylaia/page document
    '''    
    pageDoc = utils.read_page(file_path_to_process, kwsOptions)
    
    
    '''
    start spotting
    '''
    logging.info("start spotting ...")
    res = utils.spot(pageDoc, search_words, kwsOptions)

    '''
    creating result csv
    '''
    logging.info("spotting finished, writing results ...")    
    utils.createFullCSV(pageDoc, res, kwsOptions)
    
    # Record the end time
    end_time = time.time()
    
    # Calculate the processing time
    processing_time = end_time - start_time
    
    logging.info(f"Fin! Processing time: {processing_time} seconds")   
    print(f"Fin! Processing time: {processing_time} seconds")   
    