import pdfplumber 
import pandas as pd
import requests
from time import sleep
from pathlib import Path
from tqdm import tqdm

#PDFList = ["wars_before_1000.pdf", "wars_1000-1499.pdf", "wars_1500-1799.pdf", "wars_1800-1899.pdf", "wars_1900-1944.pdf", "wars_1945-1989.pdf", 
           #"wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"] # all of em

#PDFList = ["wars_before_1000.pdf"]
PDFList = ["wars_1800-1899.pdf"]

pdfs_with_extra_column = ["wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"]

# Returns true if bounding box 1 overlaps with bounding box 2
def bbox_overlaps(bbox1, bbox2):
    x0_1, top_1, x1_1, bottom_1 = bbox1
    x0_2, top_2, x1_2, bottom_2 = bbox2
    return not (x1_1 < x0_2 or x1_2 < x0_1 or bottom_1 < top_2 or bottom_2 < top_1)

for pdf_name in PDFList:
    tables = []
    war_links = []
    wider_conflict_links = []
    victors_links = []
    defeated_links = []
    p_inspect = None
    list_of_table_conflicts = []
    count = 0
    with pdfplumber.open('pdfs/'+pdf_name) as pdf:
        for page in tqdm(pdf.pages, desc=f"Processing pages of PDF '{pdf_name}'"):
            page_number = pdf.pages.index(page) + 1
            
            tables_on_page = page.find_tables(table_settings={})
            if tables_on_page:
                for i in range(len(tables_on_page)):
                    table = tables_on_page[i]
                    for j in range(len(table.rows)):
                        count += 1
                        if count == 3:
                            continue
                        row = table.rows[j]

                        if len(row.cells) < 5:
                            continue  # Skip rows that don't have enough cells

                        victors_cell_bbox = 0
                        defeated_cell_bbox = 0

                        if pdf_name in pdfs_with_extra_column:
                            victors_cell_bbox = row.cells[4] # "Victors" column different index in these pdfs
                            defeated_cell_bbox = row.cells[5]
                        else:
                            victors_cell_bbox = row.cells[3]  # Assuming the "Victors" column is the fourth column (index 3)
                            defeated_cell_bbox = row.cells[4]
                        
                        if victors_cell_bbox is None or defeated_cell_bbox is None:
                            #print("Warning: Cell bbox is None for row:", j, "on page:", page_number)
                            list_of_table_conflicts.append(("no cell bbox", page_number, j))
                            victors_links.append([])
                            defeated_links.append([])
                            continue

                        victors_matching_links = [
                            link for link in page.hyperlinks
                            if bbox_overlaps(victors_cell_bbox, (link['x0'], link['top'], link['x1'], link['bottom']))
                            ]
                        
                        defeated_matching_links = [
                            link for link in page.hyperlinks
                            if bbox_overlaps(defeated_cell_bbox, (link['x0'], link['top'], link['x1'], link['bottom']))
                            ]
                        
                        victors_matching_links = [link.get("uri") for link in victors_matching_links]
                        defeated_matching_links = [link.get("uri") for link in defeated_matching_links]

                        victors_links.append(victors_matching_links)
                        defeated_links.append(defeated_matching_links)
    
    csv_path_string = f"tables/{pdf_name}_tables.csv"
    csv_df = pd.read_csv(csv_path_string)
    print("Length of victors:", len(victors_links), "| length of defeated:", len(defeated_links))
    print("len of file:", len(csv_df))
    csv_df["Victors links"] = pd.Series(victors_links)
    csv_df["Defeated links"] = pd.Series(defeated_links)
    csv_df.to_csv(csv_path_string)
        
        