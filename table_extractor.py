import pdfplumber 
import pandas as pd
import requests
from time import sleep
from pathlib import Path

# Returns true if bounding box 1 overlaps with bounding box 2
def bbox_overlaps(bbox1, bbox2):
    x0_1, top_1, x1_1, bottom_1 = bbox1
    x0_2, top_2, x1_2, bottom_2 = bbox2
    return not (x1_1 < x0_2 or x1_2 < x0_1 or bottom_1 < top_2 or bottom_2 < top_1)

# Get the total views for a specific Wikipedia article over a date range
def get_wikipedia_pageviews(article, start, end, project="en.wikipedia.org"):
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/all-agents/{article.replace(' ', '_')}/monthly/{start}/{end}"
    headers = {
        'User-Agent': 'WarWordleWebsite (serg.rozalenbreton@gmail.com)'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"HTTP {response.status_code} for '{article}': {response.text[:200]}")
        return -1

    try:
        data = response.json()
    except Exception as e:
        print(f"Error parsing JSON for article '{article}': {e}. Body: {response.text[:200]}")
        return -1

    if "items" not in data:
        print(f"Article '{article}' not found. Skipping.")
        return -1

    if "items" not in data.keys():
        print(f"Article '{article}' not found. Skipping.")
        return -1
    else:
        # Calculate total views from the daily breakdown
        total_views = sum(item['views'] for item in data['items'])

        return total_views

tables = []
war_links = []
wider_conflict_links = []
p_inspect = None
list_of_table_conflicts = []
count = 0
#PDFList = ["wars_1500-1799.pdf", "wars_1800-1899.pdf", "wars_1900-1944.pdf", "wars_1945-1989.pdf", 
           #"wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"]
PDFList = ["wars_2003-2019.pdf"]

for pdf in PDFList:
    path = Path(pdf)
    if path.exists():
        print(f"PDF file '{pdf}' found.")
    else:
        raise Exception(f"PDF file '{pdf}' not found. Please check the path.")

# Goes through PDF and extracts tables, hyperlinks, and other relevant data
for pdf_name in PDFList:
    count = 0
    with pdfplumber.open(pdf_name) as pdf:
        for page in pdf.pages:
            page_number = pdf.pages.index(page) + 1
            if pdf_name != "wars_2003-2019.pdf" or page_number != 1:
                continue  # Skip the first page of the first PDF as it doesn't contain relevant data
            #for link in page.hyperlinks:
                #print("URL:", link.get("uri"))
            #if page_number == 42:
                #print("PAGE FOUND")
            #p_inspect = page
            tables_text_on_page = page.extract_tables()
            if tables_text_on_page:
                for table in tables_text_on_page:
                    if table:
                        tables.append({"page": page_number, "data": table})

            ######
            # Check for hyperlinks in the conflict table cells
            
            tables_on_page = page.find_tables(table_settings={})
            if tables_on_page:
                for i in range(len(tables_on_page)):
                    table = tables_on_page[i]
                    for j in range(len(table.rows)):
                        count += 1
                        if count == 3:
                            continue
                        row = table.rows[j]
                        print(f"Processing row {j} on page {page_number} of PDF '{pdf_name}'. Count: {count}")
                        if len(row.cells) < 3:
                            continue  # Skip rows that don't have enough cells
                        cell_bbox = row.cells[2]  # Assuming the "Name of conflict" column is the third column (index 2)

                        if cell_bbox is None:
                            #print("Warning: Cell bbox is None for row:", j, "on page:", page_number)
                            war_links.append("")
                            wider_conflict_links.append("")
                            list_of_table_conflicts.append(("no cell bbox", page_number, j))
                            continue

                        matching_links = [
                            link for link in page.hyperlinks
                            if bbox_overlaps(cell_bbox, (link['x0'], link['top'], link['x1'], link['bottom']))
                        ]

                        war_link = None
                        wider_conflict_link = None
                        if matching_links:
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
                                #print(f"Warning: More than 2 links found for conflicts in row {j} on page {page_number}."+ 
                                #    " Using the first two links.")
                                #list_of_table_conflicts.append(("more than 2 links", page_number, j))
                                if matching_links[0]['top'] < matching_links[1]['top']:
                                    war_link = matching_links[0]
                                    wider_conflict_link = matching_links[1]
                                else:
                                    war_link = matching_links[1]
                                    wider_conflict_link = matching_links[0]

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


#im = p_inspect.to_image()
#im.debug_tablefinder(table_settings={})
#im.show()
#print("list_of_table_conflicts:", list_of_table_conflicts)
#print("count:", count)
#print("conflicts list length:", len(conflicts_list))

#print("part of list:", part_of_list)
print("headers: "+str(all_tables_df.columns.values.tolist()))
all_tables_df["Name of conflict"] = conflicts_list
all_tables_df["Part of"] = part_of_list
#print("war links length:", len(war_links))
all_tables_df["War link"] = war_links
all_tables_df["Wider conflict link"] = wider_conflict_links

######
# Get the total views for a specific Wikipedia article over a date range
start = "20250101"  # YYYYMMDD
end = "20260630"    # YYYYMMDD
page_views_list = []
for i in range(len(war_links)):
    war_link = war_links[i]
    if war_link and war_link.startswith("https://en.wikipedia.org/wiki/"):
        article_title = war_link.split("/")[-1]  # Extract the article title from the URL
        hashtag_index = article_title.find("#")
        article_title = article_title[:hashtag_index] if hashtag_index != -1 else article_title
        #print(f"Fetching pageviews for article: {article_title}")
        total_views = get_wikipedia_pageviews(article_title, start, end)
        #print(f"Total views for {article_title}: {total_views}")
        page_views_list.append(total_views)
        sleep(0.1)
    else:
        page_views_list.append(None)

page_views_title = f"Wikipedia pageviews ({start[:4]} - {end[:4]})"
all_tables_df[page_views_title] = page_views_list
all_tables_title = "all_tables.csv"
all_tables_df.to_csv(all_tables_title, index=False)

vars_file = open("vars_file.txt", "a")
vars_file.write(all_tables_title + "\n")
vars_file.write(page_views_title + "\n")
vars_file.write(str(page_views_list) + "\n")
vars_file.close()
