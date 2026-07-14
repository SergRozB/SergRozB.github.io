import pdfplumber 
import pandas as pd

tables = []
with pdfplumber.open("wars_1800-1899.pdf") as pdf:
    for page in pdf.pages:
        for link in page.hyperlinks:
            print("URL:", link.get("uri"))
        tables_on_page = page.extract_tables()
        if tables_on_page:
            for table in tables_on_page:
                if table:
                    tables.append({"page": pdf.pages.index(page) + 1, "data": table})

for table in tables:
    df = pd.DataFrame(table["data"])
    print(df)
all_tables_df = pd.concat([pd.DataFrame(table["data"]) for table in tables], ignore_index=True)
all_tables_df.to_csv("all_tables.csv", index=False)