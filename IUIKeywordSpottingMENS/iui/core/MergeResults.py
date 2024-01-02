"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 

    This is the CLI MergeResults Module to concat all results of a 
    given RUN_ID recursivly into one CSV file.
    
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


import os
import argparse
import csv


"""
These functions are used to merge multiple kws-results into one big CSV.
It also contains a CLI Interface
"""
def merge_csv_files(input_folder, output_filename, run_id):
    # Initialize a list to hold the data from all CSV files
    all_data = []

    # Search for CSV files with the specified RUN_ID in the filename
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.startswith(f"results_{run_id}") and file.endswith(".csv"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as csv_file:
                    csv_reader = csv.reader(csv_file)
                    data = list(csv_reader)
                    if not all_data:
                        # If all_data is empty, use the first file's header
                        header = data[0]
                        all_data.append(header)
                    # Append data from this file to the all_data list
                    all_data.extend(data[1:])

    if not all_data:
        print(f"No CSV files found with RUN_ID '{run_id}' in the input folder.")
        return

    # Determine the output file path
    if not output_filename:
        output_filename = f"results_{run_id}_merged.csv"

    # Write the merged CSV to the input folder
    output_file_path = os.path.join(input_folder, output_filename)
    with open(output_file_path, "w", newline="") as merged_csv:
        csv_writer = csv.writer(merged_csv)
        csv_writer.writerows(all_data)

def main():
    
    '''
    Print GNU GPL Messages
    '''
    print("The new Keyword Spotting Tool.  Copyright (C) 2023  Raphael Unterweger")
    print("This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.")
    print("This is free software, and you are welcome to redistribute it")
    print("under certain conditions; type `show c' for details.\n")
    
    
    parser = argparse.ArgumentParser(description="Merge CSV files in a folder recursively.")
    parser.add_argument("input_folder", help="Input folder containing CSV files (default is the current working directory).")
    parser.add_argument("-o", "--output", help="Output filename (optional).")
    parser.add_argument("run_id", help="RUN_ID to identify CSV files to merge.")
    args = parser.parse_args()

    merge_csv_files(args.input_folder, args.output, args.run_id)
    print(f"Merged all {args.run_id} CSV files and saved it to {args.input_folder}")

if __name__ == "__main__":
    main()
