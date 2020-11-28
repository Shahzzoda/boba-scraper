from bs4 import BeautifulSoup
import requests
from typing import List, Dict
import js2py
import googlemaps
import os

"""
using yelp's results to scrape the boba entries from each borough and
scrpaing pages is at 0, and increases by 10 until the last page. The location
aspect returns "near [borough]" so there's two problems this introduces:
    1. repeated values (all boros are near each other)
    2. locations have to be verified
Resepctive solutions:
    1. resturuant entry objects with '==' implemented
    2. google api to verify borough & greater location as a whole:
        geocoding api should suffice -> we need lat & long anyway
"""

boba_places = []
os.environ['GMAP_API_KEY'] = ''
api_key = os.getenv('GMAP_API_KEY')
gmaps = googlemaps.Client(api_key)
counter = 0


class BobaEntry():
    def __init__(self, name: str, location: str):
        self.name = name
        self.location = location

    def __eq__(self, other):
        if self.name == other.name and self.location == other.name:
            return True
        return False


def scrape_page(page_number: int, borough: str) -> None:
    results = make_request(page_number, borough)
    isValidContent = False
    boba_count = 0
    for result in results:
        if (
            'searchResultLayoutType' in result.keys()
            and result['searchResultLayoutType'] == 'separator'
            and 'text' in result['props'].keys()
            and result['props']['text'] == 'All Results'
        ):
            isValidContent = True
        elif(
            'searchResultLayoutType' in result.keys()
            and 'type' in result
            and result['type'] == 'sectionLabel'
            and result['props']['text'] == 'Sponsored Result'
        ):
            isValidContent = False
        elif isValidContent and 'searchResultBusiness' in result.keys():
            name = result['searchResultBusiness']['name']
            location = result['searchResultBusiness']['formattedAddress']
            if len(result['searchResultBusiness']['neighborhoods']) > 1:
                location += result['searchResultBusiness']['neighborhoods'][0]
            print("\tname: ", name, "location: ", location)
            boba_entry = BobaEntry(name, location)
            boba_boros = get_boroughs(location)
            if boba_entry not in boba_places and borough in boba_boros:
                boba_places.append(boba_entry)
                boba_count += 1
    return boba_count


def get_boroughs(location: str) -> List[str]:
    if not location:
        return []
    global counter
    counter += 1
    borough_names = []
    for loc in gmaps.geocode(location):
        aspects = loc["address_components"]
        for aspect in aspects:
            if 'sublocality_level_1' in aspect['types']:
                borough_names.append(aspect['long_name'])
    print("\tBoroughs: ", borough_names)
    return borough_names


def make_request(page_number: int, borough: str) -> None:
    # start: 0 -> 10 -> 20 -> 30 in increments 10 starting at 0
    start = (page_number - 1) * 10
    location = f'{borough}, New York'
    headers = {
        'authority': 'www.yelp.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
        + '(KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'dnt': '1',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.yelp.com/search?find_desc=BOBA&find_loc=Brooklyn%2C%20NY&start=90',
        'accept-language': 'en-US,en;q=0.9',
    }
    params = (
        ('find_desc', 'boba'),
        ('find_loc', location),
        ('start', str(start)),
        ('parent_request_id', '82a76d892e6e8b5e'),
        ('request_origin', 'user'),
    )

    link = 'https://www.yelp.com/search/snippet'
    response = requests.get(link, headers=headers, params=params)
    content = response.json()
    return content['searchPageProps']['searchResultsProps']['searchResults']


def count_pages(link: str) -> int:
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    navigations = soup.find_all(role='navigation')[-1]
    no_of_pages_text = navigations.find_all('span')[-1].text
    no_of_pages = no_of_pages_text.split()[-1]
    return int(no_of_pages)


def scrape_borough(borough: str) -> int:
    link = f'https://www.yelp.com/search?find_desc=boba&find_loc={borough}%2C%20NY&start=0'
    pages_len = count_pages(link)
    borough_boba_spots = 0
    for i in range(pages_len):
        page_number = i + 1
        print("page: ", page_number)
        borough_boba_spots += scrape_page(
            page_number=page_number, borough=borough)
    return borough_boba_spots


def start_scraping() -> None:
    boros = ["The Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
    boba_spots = []
    for borough in boros:
        print()
        print(f"Scraping {borough} Boba Spots")
        boba_spots.append(scrape_borough(borough))
    print(
        "Here's the infromation I have gathered: \n"
        + f"Bronx: {boba_spots[0]}\n"
        + f"Brooklyn: {boba_spots[1]}\n"
        + f"Manhattan: {boba_spots[2]}\n"
        + f"Queens: {boba_spots[3]}\n"
        + f"Staten Island: {boba_spots[4]}\n"
    )


if __name__ == '__main__':
    start_scraping()
