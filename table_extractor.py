import pdfplumber 
import pandas as pd
import requests
from time import sleep
from pathlib import Path
from tqdm import tqdm

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
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            print(f"Rate limited. Retrying after: {retry_after} seconds")
            sleep(float(retry_after))  # Sleep for a short duration to avoid hitting the API too quickly
            return get_wikipedia_pageviews(article, start, end, project)
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

# PDFList specifies which PDFs to make csvs for

#PDFList = ["wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"]
#PDFList = ["wars_before_1000.pdf", "wars_1000-1499.pdf"]
#PDFList = ["wars_2003-2019.pdf", "wars_2020-present.pdf"]
#PDFList = ["wars_1990-2002.pdf"]
#PDFList = ["wars_1900-1944.pdf", "wars_1945-1989.pdf", 
        #"wars_1990-2002.pdf"]
#PDFList = ["wars_1500-1799.pdf", "wars_1800-1899.pdf", "wars_1900-1944.pdf", "wars_1945-1989.pdf", # Current intended ones
           #"wars_1990-2002.pdf"]
PDFList = ["wars_before_1000.pdf", "wars_1000-1499.pdf", "wars_1500-1799.pdf", "wars_1800-1899.pdf", "wars_1900-1944.pdf", "wars_1945-1989.pdf", 
           "wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"] # all of em
#PDFList = ["wars_2003-2019.pdf"]
#PDFList = ["wars_1500-1799.pdf"]

pdfs_with_extra_column = ["wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"]
pdf_to_df = {}
pdf_to_war_links = {}
pdf_to_wider_conflict_links = {}
use_intermediate_csv = False  # Set to True to skip page processing and use intermediate CSV files if they exist
                            # Ensure relevant intermediate CSV and textfiles exist when set True, otherwise the script will raise an exception.
skipped_page_processing = False  # Flag to indicate if page processing was skipped

for pdf in PDFList:
    path = Path("pdfs/"+pdf)
    if path.exists():
        print(f"PDF file '{pdf}' found.")
    else:
        raise Exception(f"PDF file '{pdf}' not found. Please check the path.")

# Goes through PDF and extracts tables, hyperlinks, and other relevant data
if not use_intermediate_csv:
    for pdf_name in PDFList:
        tables = []
        war_links = []
        wider_conflict_links = []
        p_inspect = None
        list_of_table_conflicts = []
        count = 0
        with pdfplumber.open('pdfs/'+pdf_name) as pdf:
            for page in tqdm(pdf.pages, desc=f"Processing pages of PDF '{pdf_name}'"):
                page_number = pdf.pages.index(page) + 1
                if page_number == 1:
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
                            #print(f"Processing row {j} on page {page_number} of PDF '{pdf_name}'. Count: {count}")
                            if len(row.cells) < 3:
                                continue  # Skip rows that don't have enough cells

                            # Get war links

                            if pdf_name in pdfs_with_extra_column:
                                conflict_cell_bbox = row.cells[3] # "Name of conflict" column different index in these pdfs
                            else:
                                conflict_cell_bbox = row.cells[2]  # Assuming the "Name of conflict" column is the third column (index 2)

                            if conflict_cell_bbox is None:
                                #print("Warning: Cell bbox is None for row:", j, "on page:", page_number)
                                war_links.append("")
                                wider_conflict_links.append("")
                                list_of_table_conflicts.append(("no cell bbox", page_number, j))
                                continue

                            conflict_matching_links = [
                                link for link in page.hyperlinks
                                if bbox_overlaps(conflict_cell_bbox, (link['x0'], link['top'], link['x1'], link['bottom']))
                            ]

                            war_link = None
                            wider_conflict_link = None
                            if conflict_matching_links:
                                if len(conflict_matching_links) == 2:
                                    # If two links, higher link in page should be the war link, lower link should be the wider conflict link
                                    if conflict_matching_links[0]['top'] < conflict_matching_links[1]['top']:
                                        war_link = conflict_matching_links[0]
                                        wider_conflict_link = conflict_matching_links[1]
                                    else:
                                        war_link = conflict_matching_links[1]
                                        wider_conflict_link = conflict_matching_links[0]

                                elif len(conflict_matching_links) == 1:
                                    war_link = conflict_matching_links[0]

                                elif len(conflict_matching_links) > 2:
                                    #print(f"Warning: More than 2 links found for conflicts in row {j} on page {page_number}."+ 
                                    #    " Using the first two links.")
                                    #list_of_table_conflicts.append(("more than 2 links", page_number, j))
                                    if conflict_matching_links[0]['top'] < conflict_matching_links[1]['top']:
                                        war_link = conflict_matching_links[0]
                                        wider_conflict_link = conflict_matching_links[1]
                        
                                    else:
                                        war_link = conflict_matching_links[1]
                                        wider_conflict_link = conflict_matching_links[0]
                                    
                                    if war_link == wider_conflict_link:
                                        # Get the next link up
                                            for i in range(len(conflict_matching_links)):
                                                i += 2
                                                if i > (len(conflict_matching_links) - 1):
                                                    break
                                                if wider_conflict_link != war_link:
                                                    wider_conflict_link = conflict_matching_links[i]
                                                    break
                            
                            war_links.append(war_link.get("uri") if war_link else "")
                            wider_conflict_links.append(wider_conflict_link.get("uri") if wider_conflict_link else "")                            

        pdf_to_df[pdf_name] = pd.concat([pd.DataFrame(table["data"]) for table in tables], ignore_index=True)
        pdf_to_war_links[pdf_name] = war_links
        pdf_to_wider_conflict_links[pdf_name] = wider_conflict_links
        df = pdf_to_df[pdf_name]

        if pdf_name in pdfs_with_extra_column: # Removing column which only this PDF has
            df = df.drop(df.columns[0], axis=1)

        if not df.empty:
            header_index = -1
            conflict_index = 2
            for row_index in range(len(df)):
                print("row index:", row_index, "| row contents:", df.iloc[row_index].tolist())
                if df.iloc[row_index, conflict_index] == "Name of conflict" or df.iloc[row_index, conflict_index] == "Name of Conflict":
                    header_index = row_index
                    break
                if row_index > 10:  # Limit the search to the first 10 rows
                    raise Exception(f"Header row not found in the first 10 rows of DataFrame for PDF '{pdf_name}'.")
            if header_index == -1:
                raise Exception(f"Header row not found in DataFrame for PDF '{pdf_name}'.")
            else:
                df.columns = df.iloc[header_index]  # Set the header row as the DataFrame's columns
                df = df[header_index + 1:]  
                df.reset_index(drop=True, inplace=True)  # Reset the index after removing rows

        else:
            raise Exception(f"Warning: DataFrame for PDF '{pdf_name}' is empty.")

        # Get the "Name of conflict" column and create a new column for the wider conflict its part of if applicable
        # Some of them have different capitalisation, so we check for both "Name of conflict" and "Name of Conflict"
        conflict_header_name = "Name of conflict"
        if conflict_header_name not in df.columns:
            conflict_header_name = "Name of Conflict" 
        conflicts_list = df[conflict_header_name].tolist()
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
                    conflicts_list[i] = conflict[:index_of_start_of_wider_conflict - length_of_part_of]
                else:
                    part_of_list.append("")
            else:
                part_of_list.append("")

        df[conflict_header_name] = conflicts_list
        df["Part of"] = part_of_list
        print("war links length:", len(war_links), "table rows length:", len(df))
        df["War link"] = war_links
        df["Wider conflict link"] = wider_conflict_links
        intermediate_csv = df.to_csv(f"intermediate/{pdf_name}_intermediate.csv", index=False)
        intermediate_file = open(f"intermediate/{pdf_name}_intermediate_file.txt", "a")
        intermediate_file.write(str(war_links)+"\n")
        intermediate_file.write(str(wider_conflict_links)+"\n")
        pdf_to_df[pdf_name] = df

else:
    skipped_page_processing = True
    for pdf_name in PDFList:
        intermediate_csv_path = Path(f"{pdf_name}_intermediate.csv")
        intermediate_file_path = Path(f"{pdf_name}_intermediate_file.txt")
        if intermediate_csv_path.exists() and intermediate_file_path.exists():
            print(f"Intermediate CSV and file for '{pdf_name}' found. Loading data.")
            df = pd.read_csv(intermediate_csv_path)
            with open('intermediate/'+intermediate_file_path, "r") as f:
                lines = f.readlines()
                war_links = eval(lines[0].strip())
                wider_conflict_links = eval(lines[1].strip())
            pdf_to_df[pdf_name] = df
            pdf_to_war_links[pdf_name] = war_links
            pdf_to_wider_conflict_links[pdf_name] = wider_conflict_links
        else:
            raise Exception(f"Intermediate CSV or file for '{pdf_name}' not found. Please run the script without 'use_intermediate_csv' set to True first.")

#all_tables_df = pd.concat([pd.DataFrame(table["data"]) for table in tables], ignore_index=True)
#all_tables_df.columns = all_tables_df.iloc[0] 
#all_tables_df = all_tables_df[1:]
#print(all_tables_df.columns.values.tolist())

for pdf_name in PDFList:
    df = pdf_to_df[pdf_name]
    war_links = pdf_to_war_links[pdf_name]
    wider_conflict_links = pdf_to_wider_conflict_links[pdf_name]

    ######
    # Get the total views for a specific Wikipedia article over a date range
    start = "20250101"  # YYYYMMDD
    end = "20260630"    # YYYYMMDD
    page_views_list = []
    for i in tqdm(range(len(war_links)), desc=f"Fetching Wikipedia pageviews for {pdf_name}"):
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
    print("LEN of table:", len(df))
    df[page_views_title] = page_views_list
    df_title = f"{pdf_name}_tables.csv"
    df.to_csv("tables/"+df_title, index=False) 

    pdf_to_df[pdf_name] = df
#im = p_inspect.to_image()
#im.debug_tablefinder(table_settings={})
#im.show()
#print("list_of_table_conflicts:", list_of_table_conflicts)
#print("count:", count)
#print("conflicts list length:", len(conflicts_list))


