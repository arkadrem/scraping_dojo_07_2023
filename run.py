import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
import json


def get_url_data(url, page_number, proxy_url):
    proxies = {"http": proxy_url, "https": proxy_url}

    # Get request from website with proxy
    try:
        response = requests.get(f"{url}page/{page_number}/", proxies=proxies)
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    quotes_to_scrape = soup.find("script", string=lambda text: text and "var data" in text)

    if quotes_to_scrape:
        # Get data from scraped part
        data_start = quotes_to_scrape.text.find("{") + 2
        data_end = quotes_to_scrape.text.rfind("}\n];") + 3
        data = quotes_to_scrape.text[data_start:data_end].lstrip()

        # Make data in JSON format
        new_data_start = data.find("[")
        new_data = data[new_data_start:]
        json_data = json.loads(new_data)

        # Get the text, names, and tags from the data.
        texts = [item["text"] for item in json_data]
        no_quotes = []
        for text in texts:
            no_quotes.append(re.sub(r"\u201c|\u201d", "", text))

        names = [item["author"]["name"] for item in json_data]

        tags = [item["tags"] for item in json_data]

        return no_quotes, names, tags
    else:
        # Return None if the scraped part is not found.
        return None


def get_json(no_quotes, names, tags, output):
    # Create dictionary of the scraped data.
    dictionary = []
    for i in range(len(no_quotes)):
        item = {"text": no_quotes[i], "by": names[i], "tags": tags[i]}
        dictionary.append(item)

    # Create JSON file
    with open(output, "a") as outfile:
        json.dump(dictionary, outfile, indent=4)


if __name__ == "__main__":
    load_dotenv()
    url = os.getenv("INPUT_URL")
    proxy_url = "http://" + os.getenv("PROXY")
    output = os.getenv("OUTPUT_FILE")

    # Iterate over the pages on website to get JSON file
    for page_start in range(1, 11):
        no_quotes, names, tags = get_url_data(url, page_start, proxy_url)
        get_json(no_quotes, names, tags, output)
