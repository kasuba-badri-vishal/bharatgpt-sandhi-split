import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate

vowel_list = ["a", "aa", "i", "ii", "u", "uu", ".r", ".rr", "e", "ai", "o", "au"]

def has_more_than_two_subwords(word):
    count = 0
    for vowel in vowel_list:
        if vowel in word:
            count += 1
            if count >= 2:
                return True
    return False

def ends_with_suffix(word, suffix_list):
    for suffix in suffix_list:
        if word.endswith(suffix):
            return True
    return False


def get_table_result(table):
    rows = table.find_all('tr')
    if len(rows) > 0:
        # Find the first row
        first_row = rows[1]
        # Find the first column in the first row
        columns = first_row.find_all('th')
        if len(columns) > 1:
            # Get the content of the second column in the second row
            result = columns[1].get_text(strip=True)
        else:
            print("No content found in the first column of the first row.")
    else:
        print("No rows found in the table.")
        
    return result

#read txt and get all the words
with open('./inputs/no_suffix.txt', 'r') as file:
    data = file.read()
    words = data.split("\n")
    
results = []
no_table = []
count = 0

final_results = []
for word in tqdm(words):
    
    sandhi_data = {}
    sandhi_data['word'] = word
    result = ''
    l_velthuis=transliterate(word,sanscript.DEVANAGARI,sanscript.VELTHUIS)
    sandhi_data['eng'] = l_velthuis
    sandhi_data['gen'] = 'Mas'
    fem_words = ['aa' 'ii', 'uu', '.rr', 'e', 'ai', 'o', 'au']
    vibakthi_type = 'Mas'
    if(ends_with_suffix(l_velthuis, fem_words)):
        vibakthi_type = 'Fem'
        sandhi_data['gen'] = 'Fem'


    url = "http://10.198.63.39/cgi-bin/SKT/sktdeclin"
    params = {
        'lex': 'SH',
        'q': l_velthuis,
        't': 'VH',
        'g': vibakthi_type,
        'font': 'deva'
    }
    response = requests.get(url, params=params)
    sandhi_data['result'] = True
    try:
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the table
            table = soup.find('table', class_='inflexion')
            if table:
                result = get_table_result(table)
            else:
                params = {
                    'lex': 'SH',
                    'q': l_velthuis,
                    't': 'VH',
                    'g': 'Fem',
                    'font': 'deva'
                }
                response = requests.get(url, params=params)
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', class_='inflexion')
                sandhi_data['gen'] = 'Fem'
                result = get_table_result(table)
        else:
            print("Error:", response.status_code)
            sandhi_data['result'] = False
    except:
        result = word
        count +=1
        sandhi_data['result'] = False
                 
    if('Fatal' in result):
        result = word
        count+=1
        sandhi_data['result'] = False
    results.append(result)
    sandhi_data['vibhakti'] = result
    final_results.append(sandhi_data)
    

print("Total Errors: ", count)
with open('./results2/no_suffix_vibhakti.txt', 'w') as file:
    for result in results:
        file.write(result + "\n")
        
        
#save json file

with open('./results2/no_suffix_vibhakti.json', 'w') as file:
    json.dump(final_results, file, ensure_ascii=False, indent=4)

