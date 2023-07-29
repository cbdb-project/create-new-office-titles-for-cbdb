import pandas as pd
# pip install pypinyin
from pypinyin import lazy_pinyin
from bs4 import BeautifulSoup
import requests

# Create dynasty dictionary
dynasty_df = pd.read_csv('DYNASTIES.csv', encoding='utf-8', dtype=str)
dynasty_dict = {dynasty_df['c_dynasty_chn'][i]: dynasty_df['c_dy'][i] for i in range(len(dynasty_df))}

# Read input file
input_df = pd.read_csv('input.txt', delimiter='\t', header=None, encoding='utf-8', dtype=str)
title_list = [title.strip() for title in input_df[0].tolist()]
title_trans_list = [title_trans.strip() for title_trans in input_df[1].tolist()]
dynasty_id_list = [dynasty_dict[dynasty] for dynasty in input_df[2].tolist()]
office_type_list = [office_type.strip() for office_type in input_df[3].tolist()]
source_list = [source.strip() for source in input_df[5].tolist()]

# Finding the latest office_id
latest_office_id_url = "https://input.cbdb.fas.harvard.edu/officecodes/create"
response = requests.get(latest_office_id_url)
soup = BeautifulSoup(response.text, 'html.parser')
office_id = int(soup.find('input', {'name': 'c_office_id'})['value'])
print(office_id)

# Create output
office_codes_sql_list = []
office_type_sql_list = []
office_info_list = []

# create sql string for office_codes table, the columns are:tts_sysno	c_office_id	c_dy	c_office_pinyin	c_office_chn	c_office_pinyin_alt	c_office_chn_alt	c_office_trans	c_office_trans_alt	c_source	c_pages	c_secondary_source_author	c_notes	c_category_1	c_category_2	c_category_3	c_category_4	c_office_id_old
# but I only have: c_office_id	c_dy	c_office_pinyin	c_office_chn    c_source
for i in range(len(title_list)):
    office_codes_sql_str = ""
    office_id += 1
    office_id_str = str(office_id)
    office_pinyin = " ".join(lazy_pinyin(title_list[i]))
    office_dy = dynasty_id_list[i]
    office_chn = title_list[i]
    office_source = source_list[i]
    office_type = office_type_list[i]
    office_codes_sql_str = f"INSERT INTO OFFICE_CODES (c_office_id, c_dy, c_office_pinyin, c_office_chn, c_source) VALUES ({office_id_str}, {office_dy}, {office_pinyin}, {office_chn}, {office_source});"
    office_codes_sql_list.append(office_codes_sql_str)
    office_code_type_rel_str = f"INSERT INTO OFFICE_CODE_TYPE_REL (c_office_id, c_office_tree_id) VALUES ({office_id_str}, {office_type});"
    office_type_sql_list.append(office_code_type_rel_str)
    office_info_list.append([office_id, office_dy, office_pinyin, office_chn, office_source])

# Write files
with open('output_sql.txt', 'w', encoding='utf-8') as f:
    for i in range(len(office_codes_sql_list)):
        f.write(office_codes_sql_list[i] + '\n')
        f.write(office_type_sql_list[i] + '\n')

output_df = pd.DataFrame(office_info_list, columns=['c_office_id', 'c_dy', 'c_office_pinyin', 'c_office_chn', 'c_source'])
output_df.to_csv('output.csv', index=False, encoding='utf-8')
output_df.to_excel('output.xlsx', index=False, encoding='utf-8')



    