![Alt text](images/Kinship_Ties_Extraction.png)
![PyPI version](https://img.shields.io/pypi/v/html-cleaner-kinship)



This is the package implementation of the code for the kinship ties and relational information from large text corpora, such as genealogies, biographies, and historical dictionaries. 

### Important information: 
- For example package usage, see ```test_workflow.ipynb```
- For information about individual functions before the package implementation and release, see ```examples``` folder. 

### Current release: 
Current release includes inventory creation, setting text bounds, assigning font usage and selecting appropriate text chunks from the files (including restriction to "MainText" fonts and JumPJumP insertion). 

### Files structure: 

1. #### cleaner.py 
Contains the HTMLCleaner class and thus the main logic. 

2. #### utils.py
Contains helper functions (like JumPJumP insertion)

3. #### io.py
Contains the file processing logic, such as loading and saving the JSON inventory. 
