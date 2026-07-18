import pandas as pd

PDFList = ["wars_1500-1799.pdf", "wars_1800-1899.pdf", "wars_1900-1944.pdf", "wars_1945-1989.pdf", 
           "wars_1990-2002.pdf"]
top_x_percent = 10 # Percentage of most viewed conflicts to display
page_views_title = "Wikipedia pageviews (2025 - 2026)"
top_x_dataframes_list = []

for pdf_name in PDFList:
    csv_name = pdf_name + "_tables.csv"
    df = pd.read_csv(csv_name)
    df = df.rename(columns={"Started":"Start", "Ended":"End", "Finish":"End", "Name of conflict":"Name of Conflict"})
    page_views_list = df[page_views_title].to_list()
    purged_page_views_list = [view for view in page_views_list if view is not None and view > 0]
    number_of_top_articles = int(len(purged_page_views_list) * (top_x_percent / 100))
    ordered_df = df.sort_values(by=page_views_title, ascending=False).head(number_of_top_articles)
    top_x_dataframes_list.append(ordered_df)

combined_df = pd.concat(top_x_dataframes_list)
combined_df.to_csv("combined_popular_conflicts.csv", index=False)