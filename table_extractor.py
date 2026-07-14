import pdfplumber 
import pandas as pd

tables = []
with pdfplumber.open("wars_1800-1899.pdf") as pdf:
    for page in pdf.pages:
        #for link in page.hyperlinks:
            #print("URL:", link.get("uri"))
        tables_on_page = page.extract_tables()
        if tables_on_page:
            for table in tables_on_page:
                if table:
                    tables.append({"page": pdf.pages.index(page) + 1, "data": table})

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

all_tables_df.to_csv("all_tables.csv", index=False)