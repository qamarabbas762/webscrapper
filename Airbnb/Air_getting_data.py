import requests
import json
from scrapy import Selector

headers = {
    "Host": "www.airbnb.co.in",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.airbnb.co.in/rooms/1064378968252196651?adults=1&children=0&enable_m3_private_room=true&infants=0&pets=0&check_in=2024-04-07&check_out=2024-04-12&source_impression_id=p3_1710513278_CPyvGpAFKMgv%2B0Tb&previous_page_section_name=1000&federated_search_id=611f4cde-aa5b-457f-9f80-dd0c8defd0fb",
    "X-Airbnb-Supports-Airlock-V2": "true",
    "Content-Type": "application/json",
    "X-Airbnb-API-Key": "d306zoyjsyarp7ifhu67rjxn52tv0t20",
    "X-CSRF-Token": "null",
    "X-CSRF-Without-Token": "1",
    "X-Airbnb-GraphQL-Platform": "web",
    "X-Airbnb-GraphQL-Platform-Client": "minimalist-niobe",
    "X-Niobe-Short-Circuited": "true",
    "X-Client-Version": "6310cb798f26eae4b3d472babcdd361d4b0ef975",
    "x-client-request-id": "0z4hk6g1me1wlp0yc3vqm1xnytgq",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive"
}


with open('all_final_url.json','r') as file:
    data = file.read()
    urls = json.loads(data)

hash_value = '?source_impression_id=p3_1710684022_hY3Zam%2FpTNlGpESQ'

def get_data(url):
    temp_dic = {}
    start_time = time.time()
    s = requests.session()
    headers = {
        "Host": "www.airbnb.co.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.airbnb.co.in/rooms/1064378968252196651?adults=1&children=0&enable_m3_private_room=true&infants=0&pets=0&check_in=2024-04-07&check_out=2024-04-12&source_impression_id=p3_1710513278_CPyvGpAFKMgv%2B0Tb&previous_page_section_name=1000&federated_search_id=611f4cde-aa5b-457f-9f80-dd0c8defd0fb",
        "X-Airbnb-Supports-Airlock-V2": "true",
        "Content-Type": "application/json",
        "X-Airbnb-API-Key": "d306zoyjsyarp7ifhu67rjxn52tv0t20",
        "X-CSRF-Token": "null",
        "X-CSRF-Without-Token": "1",
        "X-Airbnb-GraphQL-Platform": "web",
        "X-Airbnb-GraphQL-Platform-Client": "minimalist-niobe",
        "X-Niobe-Short-Circuited": "true",
        "X-Client-Version": "6310cb798f26eae4b3d472babcdd361d4b0ef975",
        "x-client-request-id": "0z4hk6g1me1wlp0yc3vqm1xnytgq",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Connection": "keep-alive"
    }
    _api_path = '/api/v3/PdpReviews'
    query = {
        'operationName': 'PdpReviews',
        'locale': 'en',
        'currency': 'USD',
        'variables': {
            'request': {
                'fieldSelector': 'for_p3',
                'limit': '7',
                'listingId': str(listing_id),
                'numberOfAdults': '1',
                'numberOfChildren': '0',
                'numberOfInfants': '0'
            }
        },
        'extensions': {
            'persistedQuery': {
                'version': 1,
                'sha256Hash': '4730a25512c4955aa741389d8df80ff1e57e516c469d2b91952636baf6eee3bd'
            }
        }
    }
    # if we are ading fixed headers requets are getting failed -> look later once pipeline is done
    # required_headers.update(fixed_headers)
    output_list = []
    for offset in offset_list:
        offset_dic = {}
        if int(total_reviews) >= 7:  # if total reviews are less than 7 , than we should not pass the offset value
            query['variables']['request']['offset'] = str(offset)
        q = {}
        q['variables'] = json.dumps(query['variables'], separators=(',', ':'))
        q['extensions'] = json.dumps(query['extensions'], separators=(',', ':'))
        query_url = urlencode(q)


    # json_data = json.loads(response.text)
    # print(json_data)
    #
    #
    # hotel_name = json_data['data']['presentation']['stayProductDetailPage']['sections']['sbuiData']['sectionConfiguration']['root']['sections'][0]['sectionData']['title']
    # hotel_furnitures= []
    # hotel_furniture = json_data['data']['presentation']['stayProductDetailPage']['sections']['sbuiData']['sectionConfiguration']['root']['sections'][0]['sectionData']['overviewItems']
    #
    # for i in hotel_furniture:
    #     hotel_furnitures.append(i['title'])
    #
    # hotel_rating = json_data['data']['presentation']['stayProductDetailPage']['sections']['sbuiData']['sectionConfiguration']['root']['sections'][0]['sectionData']['reviewData']['ratingText']
    # hotel_review_count = json_data['data']['presentation']['stayProductDetailPage']['sections']['sbuiData']['sectionConfiguration']['root']['sections'][0]['sectionData']['reviewData']['reviewCountText']
    # hotel_amenities = json_data['data']['presentation']['stayProductDetailPage']['sections']['sections']
    # for amenity in hotel_amenities:
    #     print(amenity)



for url1 in urls[:2]:
    print(url1)
    get_data(url1)


'https://www.airbnb.co.in/rooms/1061463378616582524?adults=1&category_tag=Tag%3A8662&children=0&enable_m3_private_room=true&infants=0&pets=0&photo_id=1813332339&search_mode=flex_destinations_search&check_in=2024-05-07&check_out=2024-05-12&source_impression_id=p3_1710685249_wv4vv9YIHvVnteFp&previous_page_section_name=1000&federated_search_id=26858be9-e40d-4094-af0d-65f512a30c3f'