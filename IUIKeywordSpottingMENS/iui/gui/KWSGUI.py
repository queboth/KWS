"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 
    
    This is the GUI Module which enables easy spottings for normal users.

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


import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import scrolledtext
from iui.core.KWSOptions import KWSOptions
from idlelib.tooltip import Hovertip
from iui.core.KWSBatch import setup_logging, process_documents_in_folder, merge_results
import sys
import logging

class KWSOptionsGUI:
    """
    This is the GUI for the new KWS Tool
    """
    
    class TextRedirector:
        """
        Redirector Class, used to pipe stdout into the TextWidget
        """
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag

        def write(self, str):
            self.widget.configure(state="normal")
            self.widget.insert(tk.END, str, (self.tag,))
            self.widget.configure(state="disabled")
            self.widget.yview(tk.END)  # Auto-scroll to the end
            self.widget.update_idletasks()  # Update the widget immediately

        def flush(self):
            pass  # No-op, as flushing is not needed in this context

    class TextWidgetHandler(logging.Handler):
        """
        This handler will add a handler to the logger, so that logs will be appended to the TextWidget
        """
        def __init__(self, widget):
            super().__init__()
            self.widget = widget

        def emit(self, record):
            msg = self.format(record)
            self.widget.configure(state="normal")
            self.widget.insert(tk.END, msg + '\n', ('stderr' if record.levelno >= logging.ERROR else 'stdout',))
            self.widget.configure(state="disabled")
            self.widget.yview(tk.END)  # Auto-scroll to the end
            self.widget.update_idletasks()  # Update the widget immediately
    
    
    
    def __init__(self, master):
        self.master = master
        self.master.title("Keyword Spotting Tool GUI")

        # Set the window state to "zoomed" (maximized)
        self.master.state('zoomed')

        self.kwsOptions = KWSOptions(True)

        # Add GUI elements for options
        self.create_options_frame()

        # Add a button to run the program (make it green)
        run_button = tk.Button(self.master, text="Start Keyword Spotting", command=self.run_program, bg="green", fg="white")
        run_button.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        # Create a scrolled text widget for displaying stdout
        self.output_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=80, height=42)
        self.output_text.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        
        # Redirect stdout to the ScrolledText widget
        sys.stdout = self.TextRedirector(self.output_text)
        log_handler = self.TextWidgetHandler(self.output_text)
        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)
        
        '''
        Print GNU GPL Messages
        '''
        print("The new Keyword Spotting Tool GUI.  Copyright (C) 2023  Raphael Unterweger")
        print("This program comes with ABSOLUTELY NO WARRANTY and is published under the")
        print("GNU General Public License 3.0")
        print("For more deatils see https://www.gnu.org/licenses/")
        
        # Configure row and column weights for resizing
        for i in range(11):  # Adjust the range according to the number of rows
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(3):   # Adjust the range according to the number of columns
            self.master.grid_columnconfigure(i, weight=1)


    def create_options_frame(self):
        options_frame = ttk.Frame(self.master)
        options_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="n")

        # Add GUI elements for options
        label = tk.Label(options_frame, text="Directory Path:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.directory_entry = tk.Entry(options_frame, width=40)
        self.directory_entry.grid(row=0, column=1, padx=5, pady=5)

        browse_button = tk.Button(options_frame, text="Browse", command=self.browse_directory)
        browse_button.grid(row=0, column=2, padx=5, pady=5)
        self.browse_button_tp = Hovertip(browse_button, "Choose a folder containing a ConfMat.ark")

        run_id_label = tk.Label(options_frame, text="Run ID:")
        run_id_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.run_id_entry = tk.Entry(options_frame)
        self.run_id_entry.grid(row=1, column=1, padx=5, pady=5)
        self.run_id_entry.insert(0, self.kwsOptions.RUN_ID)
        self.run_id_entry_tp = Hovertip(self.run_id_entry, self.kwsOptions.parser._option_string_actions["-r"].help)




        word_confidence_label = tk.Label(options_frame, text="Word Confidence:")
        word_confidence_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        self.word_confidence_entry = tk.Entry(options_frame)
        self.word_confidence_entry.grid(row=2, column=1, padx=5, pady=5)
        self.word_confidence_entry.insert(0, self.kwsOptions.WORD_CONFIDENCE )
        self.word_confidence_entry_tp = Hovertip(self.word_confidence_entry, self.kwsOptions.parser._option_string_actions["-wc"].help)
        

        normalization_power_label = tk.Label(options_frame, text="Normalization Power:")
        normalization_power_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")

        self.normalization_power_entry = tk.Entry(options_frame)
        self.normalization_power_entry.grid(row=3, column=1, padx=5, pady=5)
        self.normalization_power_entry.insert(0, self.kwsOptions.NORMALIZATION_POWER)
        self.normalization_power_entry_tp = Hovertip(self.normalization_power_entry, self.kwsOptions.parser._option_string_actions["-np"].help)

        search_words_label = tk.Label(options_frame, text="Search Words:")
        search_words_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")

        self.search_words_entry = tk.Entry(options_frame)
        self.search_words_entry.grid(row=4, column=1, padx=5, pady=5)
        self.search_words_entry.insert(0, self.kwsOptions.search_words)
        self.search_words_entry_tp = Hovertip(self.search_words_entry, self.kwsOptions.parser._option_string_actions["-q"].help)


        # Checkbox frame
        checkbox_frame = ttk.Frame(options_frame)
        checkbox_frame.grid(row=5, column=0, columnspan=3, pady=5, sticky="w")

        self.debug = tk.BooleanVar()
        self.debug_checkbox = tk.Checkbutton(checkbox_frame, text="Debug", variable=self.debug)
        self.debug_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.debug_tp = Hovertip(self.debug_checkbox, self.kwsOptions.parser._option_string_actions["-d"].help)
        if self.kwsOptions.DEBUG:
            self.debug_checkbox.select()

        self.clean_ctc_double_chars = tk.BooleanVar()
        self.clean_ctc_double_chars_checkbox = tk.Checkbutton(checkbox_frame, text="Clean CTC Double Characters", variable=self.clean_ctc_double_chars)
        self.clean_ctc_double_chars_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.clean_ctc_double_chars_checkbox_tp = Hovertip(self.clean_ctc_double_chars_checkbox, self.kwsOptions.parser._option_string_actions["-cd"].help)
        if self.kwsOptions.CLEAN_CTC_DOUBLE_CHARACTERS:
            self.clean_ctc_double_chars_checkbox.select()

        self.clean_ctc_cols = tk.BooleanVar()
        self.clean_ctc_cols_checkbox = tk.Checkbutton(checkbox_frame, text="Clean CTC Cols", variable=self.clean_ctc_cols)
        self.clean_ctc_cols_checkbox.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.clean_ctc_cols_checkbox_tp = Hovertip(self.clean_ctc_cols_checkbox, self.kwsOptions.parser._option_string_actions["-cc"].help)
        if self.kwsOptions.CLEAN_CTC_COLS:
            self.clean_ctc_cols_checkbox.select()

        self.clean_nonsearchword_chars = tk.BooleanVar()
        self.clean_nonsearchword_chars_checkbox = tk.Checkbutton(checkbox_frame, text="Clean Non-SearchWord Chars", variable=self.clean_nonsearchword_chars)
        self.clean_nonsearchword_chars_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.clean_nonsearchword_chars_checkbox_tp = Hovertip(self.clean_nonsearchword_chars_checkbox, self.kwsOptions.parser._option_string_actions["-cnsc"].help)
        if self.kwsOptions.CLEAN_NONSEARCHWORD_CHARS:
            self.clean_nonsearchword_chars_checkbox.select()


    def browse_directory(self): 
        directory_path = filedialog.askdirectory()
        self.directory_entry.delete(0, tk.END)
        self.directory_entry.insert(0, directory_path)

    def run_program(self):
        # Get values from GUI elements and call your program
        self.kwsOptions.directory_path = self.directory_entry.get()
        self.kwsOptions.RUN_ID = self.run_id_entry.get()
        self.kwsOptions.WORD_CONFIDENCE = float(self.word_confidence_entry.get())
        self.kwsOptions.NORMALIZATION_POWER = int(self.normalization_power_entry.get())
        self.kwsOptions.search_words = self.search_words_entry.get()
        self.kwsOptions.CLEAN_CTC_DOUBLE_CHARACTERS = self.clean_ctc_double_chars.get()
        self.kwsOptions.CLEAN_CTC_COLS = self.clean_ctc_cols.get()
        self.kwsOptions.CLEAN_NONSEARCHWORD_CHARS = self.clean_nonsearchword_chars.get()
        self.kwsOptions.DEBUG = self.debug.get()
        self.kwsOptions.PRINT_RESULTS_TO_CONSOLE = True
    
        self.output_text.delete("1.0", tk.END)
        # Print options to the output text
        if self.kwsOptions.directory_path:
            print(f"Directory Path: {self.kwsOptions.directory_path}")
            print(f"Run ID: {self.kwsOptions.RUN_ID}")
            print(f"Word Confidence: {self.kwsOptions.WORD_CONFIDENCE}")
            print(f"Clean CTC Double Characters: {self.kwsOptions.CLEAN_CTC_DOUBLE_CHARACTERS}")
            print(f"Clean CTC Cols: {self.kwsOptions.CLEAN_CTC_COLS}")
            print(f"Clean Non-SearchWord Chars: {self.kwsOptions.CLEAN_NONSEARCHWORD_CHARS}")
            print(f"Normalization Power: {self.kwsOptions.NORMALIZATION_POWER}")
            print(f"Search Words: {self.kwsOptions.search_words}")
            print(f"Debug: {self.kwsOptions.DEBUG}")
            # Call your program's logic here
            # your_program_logic(directory_path, run_id, word_confidence, clean_ctc_double_chars, clean_ctc_cols, clean_nonsearchword_chars, normalization_power, debug)
            
            print("spotting ...")
            
            setup_logging(self.kwsOptions.RUN_ID, self.kwsOptions.directory_path)
            process_documents_in_folder(self.kwsOptions.directory_path, self.kwsOptions.RUN_ID, self.kwsOptions.search_words, self.kwsOptions.WORD_CONFIDENCE, self.kwsOptions.CLEAN_CTC_COLS, self.kwsOptions.NORMALIZATION_POWER, self.kwsOptions)
            merge_results(self.kwsOptions.directory_path, self.kwsOptions.RUN_ID)
            
            print(f"Fin! Results written to: {self.kwsOptions.directory_path}/merged_results_{self.kwsOptions.RUN_ID}.csv")

        else:
            self.output_text.insert(tk.END, f"please select a folder with a ConfMat.ark")
    

if __name__ == "__main__":
    root = tk.Tk()
    app = KWSOptionsGUI(root)
    root.mainloop()
