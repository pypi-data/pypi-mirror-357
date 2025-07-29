
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

def insert_jumpjump(text, max_chars=10000):
    """
    Insert JumPJumP every time accumulated characters between newlines exceed max_chars,
    while ensuring there's no existing JumPJumP immediately after the first newline.
    """
    lines = text.split('\n')
    result = []
    char_count = 0
    last_inserted = False

    for line in lines:
        char_count += len(line)
        result.append(line)

        # If we hit the char limit and didn't just insert a jump, do it
        if char_count >= max_chars and not last_inserted:
            result.append("JumPJumP")
            char_count = 0
            last_inserted = True
        elif "JumPJumP" in line:
            # If the line already has JumPJumP, reset char count but don’t reinsert
            char_count = 0
            last_inserted = True
        else:
            last_inserted = False

    return '\n'.join(result)
