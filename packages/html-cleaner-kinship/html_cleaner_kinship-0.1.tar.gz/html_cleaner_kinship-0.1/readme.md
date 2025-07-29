![Alt text](images/Kinship_Ties_Extraction.png)

This repository enables users to extract kinship ties and relational information from large text corpora, such as genealogies, biographies, and historical dictionaries.

It is designed to process HTML documents (this format offers many task-related benefits, such as font-identification). The HTML files go through a structured cleaning and segmentation process to be finally supplied to LLMs for the purpouse of kinship relations and events extraction. For example, extracting from a historical dictionary information about individuals("father of", "married to", "born"). 

Flowchart of the code logic: 



The user needs to manually identify when does the relevant HTML section begin and when does it end. For example, by opening the file in code editor (here VS Code) and selecting how many characters are before and after the desired text chunk:

![Demo animation](images/relevant_sec.gif)

In this case the number for relevant beginning is 4601.
This information needs to be added to the JSON file in the section that includes this specific HTML.