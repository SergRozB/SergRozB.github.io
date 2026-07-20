import pdfplumber 
from tqdm import tqdm
import pandas as pd

# Geographical area conflict links
european_conflicts_links = []
asian_conflicts_links = []
african_conflicts_links = []
south_american_conflicts_links = []
north_american_conflicts_links = []

PDF_folder_name = "pdfs"
PDF_continents_list = ["List_of_conflicts_in_Africa.pdf", "List_of_conflicts_in_Asia.pdf",
                        "List_of_conflicts_in_Europe.pdf", "List_of_conflicts_in_North_America.pdf", 
                        "List_of_conflicts_in_South_America.pdf"]

PDF_tables_list = ["tables\wars_before_1000.pdf_tables.csv",
                    "tables\wars_1000-1499.pdf_tables.csv", "tables\wars_1500-1799.pdf_tables.csv",
                    "tables\wars_1800-1899.pdf_tables.csv", "tables\wars_1900-1944.pdf_tables.csv",
                    "tables\wars_1945-1989.pdf_tables.csv", "tables\wars_1990-2002.pdf_tables.csv",
                    "tables\wars_2003-2019.pdf_tables.csv", "tables\wars_2020-present.pdf_tables.csv"]

pdf_to_link_list_dict = {
    "List_of_conflicts_in_Europe.pdf": european_conflicts_links,
    "List_of_conflicts_in_Asia.pdf": asian_conflicts_links,
    "List_of_conflicts_in_Africa.pdf": african_conflicts_links,
    "List_of_conflicts_in_South_America.pdf": south_american_conflicts_links,
    "List_of_conflicts_in_North_America.pdf": north_american_conflicts_links,
}

for pdf_name in PDF_continents_list:
    with pdfplumber.open(f'{PDF_folder_name}/'+pdf_name) as pdf:
        for page in tqdm(pdf.pages, desc=f"Processing pages of PDF '{pdf_name}'"):
            page_number = pdf.pages.index(page) + 1
            for link in page.hyperlinks:
                pdf_to_link_list_dict[pdf_name].append(link.get("uri"))

conflict_link_to_continent = {}

for link in european_conflicts_links:
    conflict_link_to_continent[link] = "Europe"
for link in asian_conflicts_links:
    conflict_link_to_continent[link] = "Asia"
for link in african_conflicts_links:
    conflict_link_to_continent[link] = "Africa"
for link in south_american_conflicts_links:
    conflict_link_to_continent[link] = "South America"
for link in north_american_conflicts_links:
    conflict_link_to_continent[link] = "North America"

def Which_continent(link):
    # Returns continent link is from
    return conflict_link_to_continent.get(link, "Undefined")

print("\n\nProcessing which link is from which continent from the table\n\n")
for table_path in PDF_tables_list:
    df = pd.read_csv(table_path)
    df_link_list = df["War link"].tolist()
    continent_list = []
    for link in tqdm(df_link_list, desc=f"Processing links for table: '{table_path}"):
        continent_list.append(Which_continent(link))
    df["Continent"] = continent_list
    df.to_csv(table_path)

