import csv
from aksharamukha import transliterate
import pycdsl

from config import *


# Create an instance of CDSLCorpus321
CDSL = pycdsl.CDSLCorpus()

# Setup dictionaries
dictionaries = ["MW", "AP90", "VCP", "SHS"]
CDSL.setup(dictionaries)


column_index_to_extract = 0  # Adjust as needed, considering 0-based indexing
# Read the CSV file and extract the specified column
with open(PRATYAYA_FILE, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    
    # Use list comprehension to extract the specified column
    suffixes = [row[column_index_to_extract] for row in csv_reader]

    suffixes_iso_temp = [transliterate.process('Devanagari','iso', txt) for txt in suffixes]



suffixes_iso = []
for suffix in suffixes_iso_temp:
    
    if(len(suffix) >= 3):
        for dictionary in dictionaries:
            results = CDSL[dictionary].search(suffix)
            if results:
                suffixes_iso.append(suffix)
                break

suffixes_iso = list(set(suffixes_iso))


# token_file = "tokens.txt"

no_suffix_tokens=[]
stems=[]
suffix_freq = {key: 0 for key in suffixes_iso}
with open(DATA_FILE,'r') as file:
    content = file.read()
    tokens = content.split()
    with open(RESULTS_DIR + "suffix_3march_final.csv", 'w', newline='') as csv_file:


        tokens_iso = [transliterate.process('Devanagari','iso', txt) for txt in tokens]
        for token in tokens_iso:
            count = 0
            for suffix in suffixes_iso:
                if(token.endswith(suffix) and len(token[:-len(suffix)])>=3):

                    # if(len(suffix) >= 3):
                    # print(token,suffix)
                    for dictionary in dictionaries:
                        results = CDSL[dictionary].search(transliterate.process( 'iso','Devanagari', token[:-len(suffix)]))
                        # vidy
                        # print(token[4:-len(suffix)] + 'ā',results)
                        if results:

                            stems.append(transliterate.process( 'iso','Devanagari',token[:-len(suffix)] ))
                            count = 1
                            suffix_freq[suffix] += 1
                            csv_writer = csv.writer(csv_file)
                            row = [token,token[:-len(suffix)],suffix]
                            row_hi = [transliterate.process( 'iso','Devanagari', txt) for txt in row]
                            csv_writer.writerow(row_hi)
                            break
            if(count == 0):
                no_suffix_tokens.append(transliterate.process( 'iso','Devanagari',token))



# Open a new file in write mode
with open(RESULTS_DIR + 'stems.txt', 'w') as file:
    # Write each element to the file on a new line
    for element in stems:
        file.write(element + '\n')

with open(RESULTS_DIR + 'no_suffix.txt', 'w') as file:
    # Write each element to the file on a new line
    for element in no_suffix_tokens:
        file.write(element + '\n')
    
