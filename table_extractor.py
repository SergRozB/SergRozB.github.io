import pdfplumber 
import pandas as pd
import requests

def bbox_overlaps(bbox1, bbox2):
    x0_1, top_1, x1_1, bottom_1 = bbox1
    x0_2, top_2, x1_2, bottom_2 = bbox2
    return not (x1_1 < x0_2 or x1_2 < x0_1 or bottom_1 < top_2 or bottom_2 < top_1)

tables = []
war_links = []
wider_conflict_links = []
with pdfplumber.open("wars_1800-1899.pdf") as pdf:
    for page in pdf.pages:
        #for link in page.hyperlinks:
            #print("URL:", link.get("uri"))
        tables_text_on_page = page.extract_tables()
        if tables_text_on_page:
            for table in tables_text_on_page:
                if table:
                    tables.append({"page": pdf.pages.index(page) + 1, "data": table})

        ######
        # Check for hyperlinks in the conflict table cells
        
        tables_on_page = page.find_tables(table_settings={})
        if tables_on_page:
            for table in tables_on_page:
                for row in table.rows:
                    cell_bbox = row.cells[2]  # Assuming the "Name of conflict" column is the third column (index 2)
                    if cell_bbox is None:
                        print("Warning: Cell bbox is None for row:", row)
                        continue
                    matching_links = [
                        link for link in page.hyperlinks
                        if bbox_overlaps(cell_bbox, (link['x0'], link['top'], link['x1'], link['bottom']))
                    ]
                    if matching_links:
                        war_link = ""
                        wider_conflict_link = ""
                        if len(matching_links) == 2:
                            # If two links, higher link in page should be the war link, lower link should be the wider conflict link
                            if matching_links[0]['top'] < matching_links[1]['top']:
                                war_link = matching_links[0]
                                wider_conflict_link = matching_links[1]
                            else:
                                war_link = matching_links[1]
                                wider_conflict_link = matching_links[0]
                        elif len(matching_links) == 1:
                            war_link = matching_links[0]
                        elif len(matching_links) > 2:
                            print(f"Warning: More than 2 links found for conflicts in row {row}. Using the first two links.")
                            war_link = matching_links[0]
                            wider_conflict_link = matching_links[1]
                        war_links.append(war_link.get("uri") if war_link else "")
                        wider_conflict_links.append(wider_conflict_link.get("uri") if wider_conflict_link else "")

for table in tables:
    df = pd.DataFrame(table["data"])
    #print(df)
all_tables_df = pd.concat([pd.DataFrame(table["data"]) for table in tables], ignore_index=True)
all_tables_df.columns = all_tables_df.iloc[0] 
all_tables_df = all_tables_df[1:]
print(all_tables_df.columns.values.tolist())

# Get the "Name of conflict" column and create a new column for the wider conflict its part of if applicable
conflicts_list = all_tables_df["Name of conflict"].tolist()
part_of_list = []
for i in range(len(conflicts_list)):
    conflict = conflicts_list[i]
    if type(conflict) == str:
        index_of_part_of = conflict.find("Part of the ")
        length_of_part_of = len("Part of the ")
        if index_of_part_of != -1:
            index_of_start_of_wider_conflict = index_of_part_of + length_of_part_of
            part_of_value = conflict[index_of_start_of_wider_conflict:]
            part_of_list.append(part_of_value)
            #print("conflict without part of:", conflict[:index_of_start_of_wider_conflict - length_of_part_of])
            conflicts_list[i] = conflict[:index_of_start_of_wider_conflict - length_of_part_of]
        else:
            part_of_list.append("")
    else:
        part_of_list.append("")

#print("part of list:", part_of_list)
all_tables_df["Name of conflict"] = conflicts_list
all_tables_df["Part of"] = part_of_list
all_tables_df["War link"] = war_links
all_tables_df["Wider conflict link"] = wider_conflict_links

######
# Get the total views for a specific Wikipedia article over a date range
"""
article = "Cat"  # Wikipedia article title, spaces become underscores automatically below
project = "en.wikipedia.org"
start = "20250101"  # YYYYMMDD
end = "20260630"
url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/all-agents/{article.replace(' ', '_')}/monthly/{start}/{end}"
headers = {
    'User-Agent': 'WarWordleWebsite (serg.rozalenbreton@gmail.com)'
}

response = requests.get(url, headers=headers)
data = response.json()

# Calculate total views from the daily breakdown
total_views = sum(item['views'] for item in data['items'])
print("Total views:", total_views)
"""

all_tables_df.to_csv("all_tables.csv", index=False)