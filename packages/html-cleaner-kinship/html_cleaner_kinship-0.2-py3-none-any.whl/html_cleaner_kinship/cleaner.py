
import os
import sys
import json
import numpy as np
import pandas as pd
import re
from bs4 import BeautifulSoup
import ast
import string
from pathlib import Path
from html_cleaner_kinship.utils import insert_jumpjump
from html_cleaner_kinship.io import _load_inventory, _save_inventory


class HTMLCleaner:
    def __init__(self, json_path: str, html_directory: str = None, extension: str = ".htm"):
        """
        Initializes the cleaner. If the JSON doesn't exist but a directory is given, it builds the inventory.
        """
        self.json_path = Path(json_path)

        if not self.json_path.exists():
            if html_directory is None:
                raise FileNotFoundError(f"JSON not found at {json_path} and no directory given to create one.")
            self._create_inventory(html_directory, extension)
            print(f"Created new inventory at {json_path}")

        self.inventory = _load_inventory(self.json_path)

    #Creates the inventory from a given directory of HTML files.
    def _create_inventory(self, directory: str, extension: str = ".htm"):
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory} does not exist.")

        data = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    data.append({
                        "file_path": str(Path(root) / file),
                        "relevant_beginning": None, #Needs to be manually set by the user.
                        "relevant_end": None, #Needs to be manually set by the user.
                        "font_usage": [] #Gets updated during cleaning.
                    })

        inventory = {"files": data}
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=4)

    #Lists all files in the inventory with their index for easy reference.
    def list_files(self):
        """
        Prints all file paths with their corresponding index for easy reference.
        """
        print("Inventory File Index:")
        for idx, file_info in enumerate(self.inventory['files']):
            print(f"{idx}: {Path(file_info['file_path']).name}")

    #Allowing the user to set the relevant beginning and end for each file, the files can be accessed by filename
    def set_relevant_bounds(self, filename: str, beginning, end):
        for file in self.inventory['files']:
            if file['file_path'].endswith(filename):
                file['relevant_beginning'] = beginning
                file['relevant_end'] = end
                _save_inventory(self.json_path,self.inventory)
                return
        raise ValueError(f"File {filename} not found in inventory.")
    
    def analyze_html_fonts(self, file_index: int):
        """
        Analyzes the HTML content of a file's relevant section to extract font usage statistics.
        Parameters:
        - file_index (int): Index of the file in the inventory
        Updates:
        - Updates the `font_usage` field in the JSON for the selected file.
        """
        file_info = self.inventory['files'][file_index]
        html_path = Path(file_info['file_path'])

        if not html_path.exists():
            print(f"File not found: {html_path}")
            return

        if file_info['relevant_beginning'] is None or file_info['relevant_end'] is None:
            print(f"relevant_beginning and relevant_end must be set first.")
            return

        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        relevant_text = html_content[file_info['relevant_beginning']:file_info['relevant_end']-1]
        soup = BeautifulSoup(relevant_text, 'html.parser')

        # Match font classes like font1, font12, etc.
        pattern = re.compile(r'font\d{1,2}')
        class_stats = {}

        for tag in soup.find_all(class_=pattern):
            class_list = tag.get('class', [])
            for cls_name in class_list:
                if not pattern.match(cls_name):
                    continue
                text = tag.get_text(strip=True)
                if cls_name in class_stats:
                    class_stats[cls_name]['total_length'] += len(text)
                    class_stats[cls_name]['count'] += 1
                else:
                    class_stats[cls_name] = {'total_length': len(text), 'count': 1}

        # Format and save to inventory
        font_usage = []
        for cls, stats in class_stats.items():
            font_usage.append({
                'class': cls,
                'instances': stats['count'],
                'average_length': stats['total_length'] / stats['count'],
                'usage': ""  # Still to be set by user
            })

        file_info['font_usage'] = font_usage
        _save_inventory(self.json_path, self.inventory)
        #Display the fonts to the user
        df = pd.DataFrame(font_usage)
        print(df)
        print(f"Font usage statistics for {Path(file_info['file_path']).name} updated.")


        #Display the results as a DataFrame
        

    def classify_fonts_usage(self, index: int, usages: dict):
        """
        Classifies font usage for a specific file in the inventory.

        Parameters:
        - index (int): The index of the file in the inventory.
        - usages (dict): Dictionary of font classes to usage labels (e.g., {'font3': 'MainText'}).
        """

        if 0 <= index < len(self.inventory['files']):
            file_info = self.inventory['files'][index]
            for font, usage_type in usages.items():
                for font_entry in file_info.get('font_usage', []):
                    if font_entry['class'] == font:
                        font_entry['usage'] = usage_type
                        break

            _save_inventory(self.json_path,self.inventory)
            print("Updated font usage for file index", index)
        else:
            print(f"Invalid index: {index}")
    
        #Remove all the

    #Converts the inventory into a pandas DataFrame for easy analysis if the user desires it.

    def to_dataframe(self):
        """
        Converts the inventory into a pandas DataFrame.

        Returns:
        - pd.DataFrame: Columns include File, RelevantBeginning, RelevantEnd, class, instances, average_length, Usage.
        """
        records = []

        for file_info in self.inventory['files']:
            for font_entry in file_info.get('font_usage', []):
                records.append({
                    'File': file_info['file_path'],
                    'RelevantBeginning': file_info['relevant_beginning'],
                    'RelevantEnd': file_info['relevant_end'],
                    'class': font_entry['class'],
                    'instances': font_entry['instances'],
                    'average_length': font_entry['average_length'],
                    'Usage': font_entry['usage']
                })
                
    def selecting_text_chunks(self):
        json_path = self.json_path
        inventory = _load_inventory(json_path)

        for file_info in inventory['files']:
            html_file_path = file_info['file_path']

            try:
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except FileNotFoundError:
                print(f"File not found: {html_file_path}")
                continue

            print(f"Processing: {Path(html_file_path).name}")

            # Slice relevant section, based on the markings in relevant beginning and relevant end
            relevant_text = html_content[file_info['relevant_beginning']:file_info['relevant_end']]
            soup = BeautifulSoup(relevant_text, 'html.parser')

            # Insert JumPJumP before Title classes (following the previous logic with Pandas)
            for font_entry in file_info.get('font_usage', []):
                if font_entry.get('usage') == 'Title':
                    class_name = font_entry['class']
                    for el in soup.find_all(class_=class_name):
                        el.insert_before(soup.new_string("JumPJumP"))

            # Extract *only* MainText text (with jumps already inserted) -> following the logic from markdown cell explanation (right under classify font usage section)
            maintext_classes = {entry['class'] for entry in file_info.get('font_usage', []) if entry['usage'] == 'MainText'}
            filtered_text_parts = []
            for tag in soup.find_all(class_=lambda c: c and c in maintext_classes):
                filtered_text_parts.append(tag.get_text())

            text = '\n'.join(filtered_text_parts)


            # Clean up the text
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r'[ ]+', ' ', text)

            excluded_punctuation = re.escape(string.punctuation.replace('.', ''))
            text = re.sub(
                fr"([a-záéíóúü]) ?([{excluded_punctuation}])?\n([{excluded_punctuation}])? ?([a-záéíóúü])",
                r'\1 \4',
                text,
                flags=re.IGNORECASE
            )

            # Optional: insert jump markers every X characters
            text = insert_jumpjump(text, max_chars=10000)
            print("→ Number of JumPJumP inserted:", text.count("JumPJumP"))

            # Merge short sections unnecessarily split by jumps
            while True:
                new_text = re.sub(r'JumPJumP(.{1,500})JumPJumP', r'JumPJumP\1', text, flags=re.DOTALL)
                if new_text == text:
                    break
                text = new_text

            # Split by marker and embed directly in JSON
            text_sections = [t.strip() for t in re.split(r'\n*JumPJumP\n*', text) if t.strip()]
            file_info['cleaned_subsections'] = text_sections

        # Save updated JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=4, ensure_ascii=False)

        print("Cleaned text added to each file entry in the JSON.")

