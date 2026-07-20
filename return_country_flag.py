import requests
from time import sleep

recursion_count = 0
max_recursion = 3

def return_country_flag(wiki_title):
    title = wiki_title

    headers = {
        'User-Agent': 'WarWordleWebsite (serg.rozalenbreton@gmail.com)'
    }

    # Step 1: Get the Wikidata ID from the Wikipedia article
    params = {
        "action": "query",
        "titles": title,
        "prop": "pageprops",
        "format": "json"
    }

    response_1 = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params=params,
        headers=headers
    )

    if response_1.status_code != 200:
        print(f"HTTP {response_1.status_code} for '{wiki_title}' during step 1: {response_1.text[:200]}")
        if response_1.status_code == 429:
            if recursion_count >= 3:
                print(f"Page not responding, skipping '{wiki_title}'")
                return -1
            retry_after = response_1.headers.get("Retry-After")
            print(f"Rate limited. Retrying after: {retry_after} seconds")
            sleep(float(retry_after))  # Sleep for a short duration to avoid hitting the API too quickly
            recursion_count += 1
            return return_country_flag(wiki_title)
        return -1
    
    data = response_1.json()


    page = next(iter(data["query"]["pages"].values()))
    try:
        wikidata_id = page["pageprops"]["wikibase_item"]
    except:
        print(f"No wikidata found for '{wiki_title}'")
        return -1

    # Step 2: Query Wikidata for the flag image (P41)
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    response_2 = requests.get(url, headers=headers)

    if response_2.status_code != 200:
        print(f"HTTP {response_2.status_code} for '{wiki_title}' during step 2: {response_2.text[:200]}")
        if response_2.status_code == 429:
            if recursion_count >= 3:
                print(f"Page not responding, skipping '{wiki_title}'")
                return -1
            retry_after = response_2.headers.get("Retry-After")
            print(f"Rate limited. Retrying after: {retry_after} seconds")
            sleep(float(retry_after))  # Sleep for a short duration to avoid hitting the API too quickly
            recursion_count += 1
            return return_country_flag(wiki_title)
        return -1

    entity = response_2.json()

    claims = entity["entities"][wikidata_id]["claims"]

    # Check if flag exists for title
    flag_claims = claims.get("P41")
    if not flag_claims:
        print(f"No flag available for '{title}'")
        return -1
    
    flag_filename = (
    flag_claims[0]
    .get("mainsnak", {})
    .get("datavalue", {})
    .get("value")
)

    if not flag_filename:
        print(f"Flag couldn't be accessed for '{wiki_title}'")
        return -1

    # Step 3: Get the direct Wikimedia Commons image URL
    params = {
        "action": "query",
        "titles": f"File:{flag_filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }

    response_3 = requests.get(
        "https://commons.wikimedia.org/w/api.php",
        params=params,
        headers=headers
    )

    if response_3.status_code != 200:
        print(f"HTTP {response_3.status_code} for '{wiki_title}' during step 3: {response_3.text[:200]}")
        if response_3.status_code == 429:
            if recursion_count >= 3:
                print(f"Page not responding, skipping '{wiki_title}'")
                return -1
            retry_after = response_3.headers.get("Retry-After")
            print(f"Rate limited. Retrying after: {retry_after} seconds")
            sleep(float(retry_after))  # Sleep for a short duration to avoid hitting the API too quickly
            recursion_count += 1
            return return_country_flag(wiki_title)
        return -1

    data = response_3.json()

    page = next(iter(data["query"]["pages"].values()))
    flag_url = page["imageinfo"][0]["url"]

    return flag_url