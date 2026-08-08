import pandas as pd

PDFList = ["wars_before_1000.pdf", "wars_1000-1499.pdf", "wars_1500-1799.pdf", "wars_1800-1899.pdf", "wars_1900-1944.pdf", "wars_1945-1989.pdf", 
           "wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"] # all of em

for pdf_name in PDFList:
    csv_name = pdf_name + "_tables.csv"
    df = pd.read_csv("tables/"+csv_name)
    df = df.rename(columns={"Started":"Start", "Ended":"End", 
                            "Finish":"End", "Name of conflict":"Name of Conflict", "Belligerents" : "Victors", "Unnamed: 4": "Defeated"})
    new_start_years_list = []
    new_end_years_list = []
    old_start_years_list = df["Start"].to_list()
    old_end_years_list = df["End"].to_list()
    not_exact_list = [] # Stores which dates may not be exact
    list_of_nums = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
    for i in range(len(old_start_years_list)):
        year_string = old_start_years_list[i]
        number_of_nums = sum(char.isdigit() for char in year_string)
        if number_of_nums == 2 and "century" in year_string:
            # Assume the date is something like "23rd"
            front_two_nums = ""
            for j in range(len(year_string)):
                char = year_string[j]
                if char in list_of_nums:
                    front_two_nums += char + year_string[j+1]
            new_start_years_list.append(front_two_nums + "00")
            not_exact_list[i] = True
            continue

        for i in range(len(year_string)):
            char = year_string[i]
            if char in list_of_nums:
                