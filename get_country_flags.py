import return_country_flag
import pandas as pd
from tqdm import tqdm
from return_country_flag import return_country_flag
from time import sleep

#PDFList = ["wars_before_1000.pdf", "wars_1000-1499.pdf", "wars_1500-1799.pdf", "wars_1800-1899.pdf", "wars_1900-1944.pdf", "wars_1945-1989.pdf", 
           #"wars_1990-2002.pdf", "wars_2003-2019.pdf", "wars_2020-present.pdf"] # all of em
#PDFList = ["wars_before_1000.pdf"]
PDFList = ["wars_1800-1899.pdf"]

for pdf_name in PDFList:
    csv_path_string = f"tables/{pdf_name}_tables.csv"
    df = pd.read_csv(csv_path_string)

    victors_links = df["Victors links"].to_list()
    defeated_links = df["Defeated links"].to_list()
    victors_links = [eval(link_list) for link_list in victors_links]
    defeated_links = [eval(link_list) for link_list in defeated_links]

    victors_flag_links = []
    defeated_flag_links = []

    for i in tqdm(range(len(victors_links)), desc=f"Fetching Wikipedia victors flag images for {pdf_name}"):
        flag_links = []
        for link in victors_links[i]:
            if link.startswith("https://en.wikipedia.org/wiki/"):
                article_title = link.split("/")[-1]  # Extract the article title from the URL
                hashtag_index = article_title.find("#")
                article_title = article_title[:hashtag_index] if hashtag_index != -1 else article_title
                flag_link = return_country_flag(article_title)
                #print("Flag link victory:", flag_link)
                flag_links.append(flag_link)
                sleep(0.1)
            else:
                flag_links.append(-1)
    
    for i in tqdm(range(len(defeated_links)), desc=f"Fetching Wikipedia defeated flag images for {pdf_name}"):
        flag_links = []
        for link in defeated_links[i]:
            if link.startswith("https://en.wikipedia.org/wiki/"):
                article_title = link.split("/")[-1]  # Extract the article title from the URL
                hashtag_index = article_title.find("#")
                article_title = article_title[:hashtag_index] if hashtag_index != -1 else article_title
                flag_link = return_country_flag(article_title)
                #print("Flag link defeated:", flag_link)
                flag_links.append(flag_link)
                sleep(0.1)
            else:
                flag_links.append(-1)

    df["Victors flag image links"] = pd.Series(victors_flag_links)
    df["Defeated flag image links"] = pd.Series(defeated_flag_links)
