import pandas as pd
import random
from flask import Flask, render_template

app = Flask(__name__)

# Columns
# ['Start', 'End', 'Name of Conflict', 'Victors', 'Defeated', 'Part of',
#  'War link', 'Wider conflict link', 'Wikipedia pageviews (2025 - 2026)',
#  'Continent', 'Victors links', 'Defeated links']

PDFList = ["wars_before_1000.pdf", "wars_1000-1499.pdf", "wars_1500-1799.pdf", "wars_1800-1899.pdf", "wars_1900-1944.pdf", "wars_1945-1989.pdf", 
           "wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"] # all of em

combined_df = pd.read_csv("tables/combined_popular_conflicts.csv")
random_row_num = random.randint(0, len(combined_df)-1)
random_row = combined_df.iloc[random_row_num].tolist()

vars_dict = {
    "start" : str(random_row[0]).replace('\\n', '<br>'),
    "end" : str(random_row[1]).replace('\\n', '<br>'),
    "name" : str(random_row[2]).replace('\\n', '<br>'),
    "victors" : str(random_row[3]).replace('\\n', '<br>'),
    "defeated" : str(random_row[4]).replace('\\n', '<br>'),
}

conflict_names = []
for pdf in PDFList:
    csv_path = f"tables/{pdf}_tables.csv"
    df = pd.read_csv(csv_path)
    df = df.rename(columns={"Name of conflict" : "Name of Conflict"})
    without_nan = []
    
    for name in df["Name of Conflict"].tolist():
        if type(name) == str:
            without_nan.append(name)

    temp_conflict_names = [str(name).replace('\\n', ' ') for name in without_nan]

    for name in temp_conflict_names:
        index_of_part_of_the = name.find("Part of the ")
        length_of_part_of_the = len("Part of the ")
        index_of_part_of = name.find("Part of ")
        length_of_part_of = len("Part of ")
        if index_of_part_of_the != -1:
            index_of_start_of_wider_conflict = index_of_part_of_the + length_of_part_of_the
            name = name[:index_of_start_of_wider_conflict - length_of_part_of_the]
        elif index_of_part_of != -1:
            index_of_start_of_wider_conflict = index_of_part_of + length_of_part_of
            name = name[:index_of_start_of_wider_conflict - length_of_part_of]
        
        index_of_first_bracket = name.find("[")
        if index_of_first_bracket != -1:
            name = name[:index_of_first_bracket]
        
        conflict_names.append(name)

@app.route('/')
def show_conflict():
    return render_template(
        'index.html',
        **vars_dict,
        conflict_names=conflict_names
    )

if __name__ == '__main__':
    app.run(debug=True)