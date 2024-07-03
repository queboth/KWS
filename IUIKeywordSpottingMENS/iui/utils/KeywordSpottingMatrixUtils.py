"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 
    
    This Module contains helper functions for different list comprehensions 
    and matrix manipulations around the new KWS.
    
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
Created on 22.08.2023

@author: Raphael Unterweger
'''


import hashlib
import numpy as np
import logging
import itertools
from itertools import product
from iui.core.KWSOptions import KWSOptions



def cells_below_threshold(matrix, threshold):
    """
    This method will create a boolean matrix, identifiing Cells below the given threshold
    """
    result_matrix = matrix < threshold
    return result_matrix

def ctc_decode(ctc_text, blank_symbol="<ctc>"):
    """
    This method will decode a CTC encoded string
    """
    temp_blank = "-"
    temp_replacement = "<$$$>"
    decoded_sequence = []
    previous_symbol = None
    
    process_text = ctc_text.replace(temp_blank, temp_replacement).replace(blank_symbol, temp_blank)
    
    
    for symbol in process_text:
        if symbol != temp_blank and symbol != previous_symbol:
            decoded_sequence.append(symbol)
        previous_symbol = symbol
    
    decoded_text = ''.join(decoded_sequence)
    decoded_text = decoded_text.replace(temp_replacement, temp_blank)
    return decoded_text


def getCharIdFromSymbols(symbols, charString):
    """
    Get character ID by character from symbols dictionary
    """
    res = -1
    for key, char in symbols.items():
        if char == charString:
            res = key
            break
    
    if res == -1:
        logging.debug(f"{charString } not found in Symbols, trying default space-id '1'")
        res = 1
    
    return res
    


def calculateLineResults(symbols, combinations, temp_matrix, max_val, line_id):
    """
    This method will create a string from a symbol index array
    """
    results = []
    for comb in combinations:
        combined_symbol = ''.join(symbols[i] for i in comb)
        temp_vals = temp_matrix[range(len(comb)), comb]
        confidence_sum = np.sum(temp_vals) / len(comb)
        results.append((combined_symbol, confidence_sum, line_id))
    return results


def calculateWordResults(symbols, combinations, temp_matrix, max_val, line_id):
    """
    This method will create a string from a symbol index array
    """
    
    results = []
    
    # Create a dictionary to store sub_symbols_str as keys and their corresponding max confidence_sum as values
    unique_values = {}
    ids = {}
    
    for comb in combinations:
        sub_arrays = []  # To store subarrays after splitting
        
        # Split comb into subarrays at positions where symbols[i] is a space
        temp_sub = []
        for i in comb:
            if symbols[i] == ' ':
                if temp_sub:
                    sub_arrays.append(temp_sub)
                    temp_sub = []
            else:
                temp_sub.append(i)
        if temp_sub:
            sub_arrays.append(temp_sub)
        
        temp_vals = temp_matrix[range(len(comb)), comb]
        
        idx = 1
        for sub_comb in sub_arrays:
            sub_symbols = [symbols[i] for i in sub_comb]
            sub_symbols_str = ''.join(sub_symbols)
            sub_symbols_decoded = ctc_decode(sub_symbols_str, "<ctc>")
            
            confidence_sum = np.sum(temp_vals) / len(sub_comb)
            
            
            ids[sub_symbols_decoded] = line_id + "_" + str(idx)
            idx = idx + 1 
            if sub_symbols_decoded in unique_values:
                # Update confidence_sum if the current value is higher
                unique_values[sub_symbols_decoded] = max(unique_values[sub_symbols_decoded], confidence_sum)
            else:
                # Add new value to the dictionary
                unique_values[sub_symbols_decoded] = confidence_sum
                #results.append((sub_symbols_str, confidence_sum, line_id + "_" + idx))
    
    # Append the unique values with their max confidence_sum to the results list
    for sub_symbols_str, max_confidence_sum in unique_values.items():
        results.append((sub_symbols_str, max_confidence_sum, ids[sub_symbols_str]))

    
    return results



def extract_combinations(line_id, matrix, symbols, threshold, max_permutation_symbols=50):
    """
    DEPRECATED: This method was used for the first version, where all possible combinations 
    were build and then the search words were searched in there
    """
    
    
    print(f"Shape: {matrix.shape}")
    
    #read max and min values
    max_val = np.max(matrix)
    min_val = np.min(matrix)
    print(f"Min-Confidence: {min_val}")
    print(f"Max-Confidence: {max_val}")
    
    temp_matrix = matrix
    
    
    logging.debug("prepare matrix")
    
    # Set the minimum values to zero using the obtained indices, so that the best match is always returned
    matrix_max_indices = np.argmax(matrix, axis=1)
    for row_idx, col_idx in enumerate(matrix_max_indices):
        matrix[row_idx, col_idx] = 0
    
    #start filtering by threshold and generate boolean index table     
    logging.debug("filtering matrix by given threshold")
    filtered_matrix = cells_below_threshold(matrix, threshold)



    logging.debug("create combinations")

    # Get column indices where each row has True values
    row_true_indices = [np.where(row)[0] for row in filtered_matrix]

    #calculate combinations
    combinations = list(product(*row_true_indices))
    
    logging.debug(f"number of found combinations: {len(combinations)}")
    #    
    logging.debug("create result object with confidence values")
    
    
    #results = calculateLineResults(symbols, combinations, temp_matrix, max_val, line_id)
    results = calculateWordResults(symbols, combinations, temp_matrix, max_val, line_id)
        
    
    return results


def get_indices(symbols, search_words, keep_space=False):
    """
    This method converts all strings of a given array to an array of symbol indices
    """
    indices = []
    for search_word in search_words.split(','):
        sub_result = []
        elements = [char for char in search_word.strip()]
        for elem in elements:
            for key, value in symbols.items():
                if value == elem or (value==" " and keep_space):
                    sub_result.append(key) 
        indices.append(sub_result)
    return indices


def merge_and_clean(all_query_indices):
    """
    This method will create an array of unique symbol indices
    """
    res = []
    for sub_array in all_query_indices:
        for elem in sub_array:
            if elem not in res:
                res.append(elem)
    return res

def create_corrected_symbols_dict(symbols, all_query_indices):
    """
    This method will reduce the symbols dict, so that it only contains characters
    from from the search words array
    """
    corrected_symbols = {}
    act_key = 0
    for key, value in symbols.items():
        if key in all_query_indices or value=="<ctc>":
            corrected_symbols[act_key] = value
            act_key += 1
    return corrected_symbols

def split_matrix(matrix, by_col):
    """
    This method will split a matrix into 2 matrices at given column index
    """
    array = np.array(matrix)
    
    matrix_max_indices = np.argmax(matrix, axis=1)
    one_indices = [index for index, item in enumerate(matrix_max_indices) if item == by_col]
    
    sub_matrices = []
    prev_index = 0
    
    for index in one_indices:
        sub_matrix = array[prev_index:index, :]
        sub_matrices.append(sub_matrix)
        prev_index = index + 1
    
    
    return sub_matrices


def extract_string_by_indices(mat, symbols, cols, rows, do_ctc_decode = True):
    """
    creates a string by the symbol mapping and collects confidecne values from confmat for given array of character indices
    """
    res = ''.join(symbols[i] for i in rows)
    if do_ctc_decode:
        res = ctc_decode(res, "<ctc>")
        res = res.replace("<$>", "")
    
    colrows = list(zip(cols, rows))
    all_zero = all(item[1] == 0 for item in colrows)
    if all_zero:
        logging.debug("this line has only <ctc> chars, skipping")
        return ['<ctc>', 1.0, 1.0, 1.0]
    cols_filtered, rows_filtered = zip(*[elem for elem in colrows if elem[1] != 0])
    temp_vals = mat[cols_filtered, rows_filtered]
    confidence_sum = np.sum(temp_vals) / len(rows_filtered)
    
    min_conf = np.min(temp_vals)
    max_conf = np.max(temp_vals)
    
    #if (rows[0]==81 and rows[1]==83):
    #    print(f"Used Symbols for '{res}' ({confidence_sum}): {cols_filtered} | {rows_filtered}")
    
    return [res, confidence_sum, min_conf, max_conf ]
    




def find_best(mat, symbols):
    """
    Get value for the best confidecnes 
    """
    max_row_indices = np.argmax(mat, axis=1)
    [res, confidence_sum, min_conf, max_conf] = extract_string_by_indices(mat, symbols, range(len(max_row_indices)), max_row_indices)
    return [res, confidence_sum, min_conf, max_conf];


def generate_combinations_with_rules(keys, arrays):
    """
    Arrays contains an array for every search word charcater index. This method will build all possible combinations from it. 
    """
    if not arrays:
        return

    stack = [(0, [])]

    while stack:
        index, current_combination = stack.pop()

        if index == len(arrays):
            yield current_combination
            continue

        current_array = arrays[index]

        for num in current_array:
            if not current_combination or num > current_combination[-1]:
                new_combination = current_combination + [num]
                stack.append((index + 1, new_combination))




def generate_combinations_full(keys, arrays):
    """
    Arrays contains an array for every search word charcater index. This method will build all possible combinations from it. 
    """
    
    valid_combinations = []
    
    
    #calculating comvbination cout, max is (shape.x*shape.y)! ~ 10^400  for a word with 7 characters
    product_length = 1
    for arr in arrays:
        product_length *= len(arr)
        
    logging.debug(f"possible combinations count: {product_length}")
    
    if (product_length > 100000000000):
        logging.debug(f"too much combinations: {product_length}, skipping line")
        return []
         
    
    products = itertools.product(*arrays) 
    
    for combination in products:
        valid = True
        for i in range(1, len(keys)):
            if combination[i] <= combination[i - 1]:
                valid = False
                break
        if valid:
            valid_combinations.append(tuple(zip(keys, combination)))
    
    return valid_combinations


def generate_combinations(data_tuples):
    """
    Arrays contains an array for every search word charcater index. This method will build all possible combinations from it. 
    """

    
    keys = [key for key, _ in data_tuples]
    arrays = [array for _, array in data_tuples]
    
    # Check if any array is empty
    if any(len(array) == 0 for array in arrays):
        return []
    
    valid_combinations = generate_combinations_with_rules(keys, arrays)
    #valid_combinations = generate_combinations_full(keys, arrays)
    
    return valid_combinations


def add_result_with_conditions_old(results, act_key, comb, comb_conf, asstring):
    """
    Adding result to result array, but filter redundant information
    """
    existing_index = None
    
    for idx, result in enumerate(results):
        if result['at'] == act_key and result['asstring'][0] == asstring[0]:
            existing_index = idx
            break
    
    if existing_index is None:
        results.append({'at': act_key, 'comb': comb, 'confidence': comb_conf, 'asstring': asstring})
    else:
        results[existing_index] = {'at': act_key, 'comb': comb, 'confidence': comb_conf, 'asstring': asstring}


def add_result_with_conditions(results, act_key, comb, comb_conf, mat, symbols, cols, rows, options:KWSOptions):
    """
    Insert result in respect to the confidecne
    """
    #key = f"{act_key}_{asstring[0]}"
    asstring = extract_string_by_indices(mat, symbols, cols, rows, False)   
    key = (act_key, asstring[0])
    if key in results:
        existing_result = results[key]
        if comb_conf > existing_result['confidence']:
            results[key] = {'at': act_key, 'comb': comb, 'confidence': comb_conf, 'asstring': asstring}
            
    else:
        results[key] = {'at': act_key, 'comb': comb, 'confidence': comb_conf, 'asstring': asstring}


def compress_sub_sequences(seq):
    
    result = []
    start = None

    for num in seq:
        if start is None:
            start = num
        elif num != seq[-1]:
            continue
        else:
            result.append([start, num])
            start = None

    return result


def clean_ctc_double_occurances_v2(mat, res2, clean_ctc_double_occurances):
    """
    If there are two CTC-Characters next to each another, they will bring in no new information, so we can collapse it into one.
    """
    res3 = []
    if clean_ctc_double_occurances:
        previous_array = []
        for key, sub_array in res2:
            if (len(res3) == 0 ):
                res3.append((key,sub_array))
                previous_array = sub_array
            else:
                if (len(previous_array) == 0):
                    return []
                else:
                    confidences_array = mat[sub_array, key]
                    new_res_array = [sub_array[0]]  # Initialize a new array with the first element
                    min_index = sub_array[0]
                    max_index = sub_array[len(sub_array) - 1]
                    
                    last_used_index = 0
                    for i in range(1, len(sub_array)):
                        if sub_array[i] == sub_array[i - 1] + 1:
                            if confidences_array[i] > confidences_array[last_used_index]:
                                if i != 1:
                                    new_res_array = new_res_array[:-1]
                                new_res_array.append(sub_array[i]) 
                            else:
                                continue
                        else:
                            new_res_array.append(sub_array[i])  # Add non-consecutive elements to the new array
                        last_used_index = i
                    
                    if new_res_array[0] != min_index:
                        new_res_array.insert(0, min_index)
                    if new_res_array[len(new_res_array) - 1] != max_index:
                        new_res_array.append(max_index)
                            
                    
                    res3.append((key,new_res_array))
                    previous_array = new_res_array
    else:
        res3 = res2
    return res3



def clean_ctc_cols_v1(mat, data, symbols, clean_ctc_cols):
    """
    In nearly all cases the CTC-Windows are the same for all words in the matrix, by removing them in beforehand we are able to reduce the number of combinations by factor of around 0.3
    """
    res = []
    if clean_ctc_cols:
        ctc_index = getCharIdFromSymbols(symbols, '<ctc>')
        max_row_indices = np.argmax(mat, axis=1)
        positions = np.where(max_row_indices != ctc_index)[0]
        filtered_tuples_array = [(key, [value for value in arr if value in positions]) for key, arr in data]
        res = filtered_tuples_array
    else:
        res = data
    
    return res
    
    
    


def clean_ctc_double_occurances_v1(mat, res2, clean_ctc_double_occurances):
    """
    If there are two CTC-Characters next to each another, they will bring in no new information, so we can collapse it into one.
    This version removes all subsequences

    """
    res3 = []
    if clean_ctc_double_occurances:
        for key, sub_array in res2:
            sub_seqs = compress_sub_sequences(sub_array)
            res_sub_array = []
            for sub_seq in sub_seqs:
                start = sub_seq[0]
                end = sub_seq[1]
                
                if start==end:
                    res_sub_array.append(start)
                    continue
                
                max_conf = 0
                max_idx = 0
                for i in range(start, end):
                    conf = mat[i, key]
                    if conf > max_conf:
                        max_conf = conf
                        max_idx = i

                res_sub_array.append(start)
                if max_idx != start and max_idx != end:
                    res_sub_array.append(max_idx)
                res_sub_array.append(end)
                
                    
            res3.append((key, res_sub_array))   
    else:
        res3 = res2
        
    return res3
    

def clean_indices_rules(mat, indices_arrays, symbols, options:KWSOptions):
    """
    These rules will remove unpossible index combinations in beforehand. for example: Char n must have an greater index than char n-1, and same for above.
    """
    
    clean_lower_indices = True
    clean_higher_indices = True

    
    #clean lower indices, because if following arrays contain indices that are lower than the previous array's lowest element, it will never be used, so we kill it away
    res = []
    previous_array = []
    if clean_lower_indices:
        for key, sub_array in indices_arrays:
            if (len(res) == 0 ):
                res.append((key,sub_array))
                previous_array = sub_array
            else:
                if (len(previous_array) == 0):
                    return []
                else:
                    minelem = min(previous_array)
                    filtered_array = [x for x in sub_array if x > minelem]
                    
                    if len(filtered_array) == 0:
                        return []
                    
                    res.append((key,filtered_array))
                    previous_array = filtered_array
    else:
        res = indices_arrays



    #clean higher indices, because the first array highest element can not be higher than len(comb) - len(searchword)
    res2 = []
    pos = 0
    if clean_higher_indices:
        for key, sub_array in res:
            maxelem = mat.shape[0] - (len(indices_arrays) - pos)
            filtered_array = [x for x in sub_array if x < maxelem]
            
            if len(filtered_array) == 0:
                return []
            
            res2.append((key,filtered_array))
            pos = pos + 1
    else:
        res2 = res

    res3 = clean_ctc_cols_v1(mat, res2, symbols, options.CLEAN_CTC_COLS) 

    #res3 = clean_ctc_double_occurances_v1(mat, res2, clean_ctc_double_occurances)
    res4 = clean_ctc_double_occurances_v2(mat, res3, options.CLEAN_CTC_DOUBLE_CHARACTERS)
    
            
    return res4;

def count_indices_combination_size(indices_arrays):
    """
    Calculates number of all possible combinations
    """
    prod = 1
    for _, sub_array in indices_arrays:
        prod = prod * len(sub_array)
    return prod
        
    

def get_wildcard_indices(symbols):
    """
    DEPRECATED
    """
    result = {}
    for key, value in symbols.items():
        if value == '?':
            result[value] = key
        if value == '*':
            result[value] = key
    
    return result
    

    
def calculate_confidence_for_occurrences(mat, act_key, search_value_indexes, symbols, options:KWSOptions):
    """
    This method uses the combinations indices to calculate the confidence value from the ConfMat
    """
    
    #debug
    #if act_key == '102910.tr_1_tl_19_11':
    #    print("Here")
    
    
    #read options
    char_threshold = options.CHARACTER_TRESHOLD
    word_threshold = options.WORD_CONFIDENCE
    max_indices = options.INDICES_LIMIT
    stop_on_limit_exceed = options.STOP_ON_LIMIT_EXCEED
    
    #prepare final result object
    results = {}
    
    #get all possible search word character indices and apply wildcards. TODO: implementing wildcards
    #wildcards = get_wildcard_indices(symbols)    
    all_symbol_col_indices = []
    for symbol_idx in search_value_indexes:
        all_symbol_col_indices.append((symbol_idx, np.where(mat[:, symbol_idx] > char_threshold)[0]))
    
    #clean indices to reduce number of results
    all_symbol_col_indices = clean_indices_rules(mat, all_symbol_col_indices, symbols, options)
    
    #count indices to determine runtime
    true_count = count_indices_combination_size(all_symbol_col_indices)
    
    #check indices limit
    #print(f"TrueCount: {true_count}")
    if true_count > max_indices:
        logging.debug(f"MAX_INDICES overflow: {true_count}")
        if stop_on_limit_exceed:
            logging.debug(f"skipping this word!")
            #raise Exception(f"Indices Limit reached: {true_count}")
            return {} 
    
    
    #create all possible combinations from found indices
    all_combinations =   generate_combinations(all_symbol_col_indices)
    
    #calculate confidences for found combinations and add results
    rows = [tup[0] for tup in all_symbol_col_indices]
    for comb in all_combinations:
        cols = [tup for tup in comb]
        comb_conf = np.sum(mat[cols, rows]) / len(cols)
        
        
        if (comb_conf > word_threshold):
            add_result_with_conditions(results, act_key, comb, comb_conf, mat, symbols, cols, rows, options);

    if options.DEBUG:
        all_combinations_list = list(generate_combinations(all_symbol_col_indices))
        logging.debug(f"combinations found: {len(all_combinations_list)}, dismissed: {len(all_combinations_list) - len(results)}" )
    
    return results
    
    

def generate_hex_hash(input_string):
    """
    Generates a fixed hash from a string
    """
    input_bytes = input_string.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_bytes)
    hex_hash = sha256_hash.hexdigest()
    return hex_hash
