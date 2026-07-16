import pandas as pd

with open("vars_file.txt", "r") as vars_file:
    lines = vars_file.readlines()
    all_tables_title = lines[0].strip()
    page_views_title = lines[1].strip()
    page_views_list = eval(lines[2].strip())

all_tables_df = pd.read_csv(all_tables_title)
top_x_percent = 10 # Percentage of most viewed conflicts to display
purged_page_views_list = [view for view in page_views_list if view is not None and view > 0]
number_of_top_articles = int(len(purged_page_views_list) * (top_x_percent / 100))
ordered_df = all_tables_df.sort_values(by=page_views_title, ascending=False).head(number_of_top_articles)
ordered_df.to_csv("top_articles.csv", index=False)