import requests
from scrapy.selector import Selector
import json
import os
import time
from unidecode import unidecode
from urllib.parse import urlencode, urlunparse
from datetime import date
import glob


def deep_search(needles, haystack):
    found = {}
    if type(needles) != type([]):
        needles = [needles]

    if type(haystack) == type(dict()):
        for needle in needles:
            if needle in haystack.keys():
                found[needle] = haystack[needle]
            elif len(haystack.keys()) > 0:
                for key in haystack.keys():
                    result = deep_search(needle, haystack[key])
                    if result:
                        for k, v in result.items():
                            found[k] = v
    elif type(haystack) == type([]):
        for node in haystack:
            result = deep_search(needles, node)
            if result:
                for k, v in result.items():
                    found[k] = v
    return found


def findalloccurance(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findalloccurance(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findalloccurance(j, kv):
                yield x


proxy_host = "proxy.crawlera.com"
proxy_port = "8011"
proxy_auth = "d1d3dfa7dc4444a88a253a0263be5877:"  # Make sure to include ':' at the end
proxies = {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
           "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}
proxies = {
    "http": "http://d1d3dfa7dc4444a88a253a0263be5877:@proxy.crawlera.com:8011/",
    "https": "http://d1d3dfa7dc4444a88a253a0263be5877:@proxy.crawlera.com:8011/",
}

# username = "forager999"
# password = "58f9a1-aa4dce-cab4ad-ce5942-809a27"

# PROXY_RACK_DNS = "premium.residential.proxyrack.net:10000"
# proxies = {"http":"http://{}:{}@{}".format(username, password, PROXY_RACK_DNS)}


fixed_headers = {
    'Referer': 'https://www.airbnb.com/',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    "Accept-Language": "en-US,en;q=0.5",
    "Cache-Control": "max-age=0",
    'X-Airbnb-GraphQL-Platform-Client': 'minimalist-niobe',
    'X-CSRF-Token': 'V4$.airbnb.com$88klQ0-SkSk$f0wWUrY3M_I37iPj33S8w3-shUgkwi4Dq63e19JPlGQ=',
    'X-CSRF-Without-Token': '1',
}


def load_url(query_url, headers):
    # try to load the url 5 times if still not getting than mark it as pending
    for i in range(5):
        try:
            try:
                response = requests.get(query_url, headers=headers, proxies=proxies, verify="zyte-proxy-ca.crt",
                                        timeout=10)
            except:
                pass
            data = response.text
            if 'All download attempts failed' in data:
                raise Exception('This is the exception you expect to handle')
            return data, 'success'
        except:
            pass
    # we tried but failed so send a failed status
    return '', 'fail'


def load_listing_page(listing_dic):
    temp_dic = {}
    start_time = time.time()
    url = listing_dic['info']['href']
    path = listing_dic['info']['path']
    try:
        # response=s.get(url,headers=fixed_headers,verify=False).text
        # response=requests.get(url,headers=fixed_headers).text
        data, st = load_url(url, fixed_headers)
        hxs = Selector(text=data)
        # lisitng html page dump
        f = open(path + "webpage.html", 'w')
        f.write(unidecode(data))
        f.close()
        temp_dic['webpage'] = {'status': st, 'href': url, 'headers': fixed_headers, 'path': path + "webpage.html"}
    except:
        temp_dic['webpage'] = {'status': 'fail', 'href': url, 'headers': fixed_headers, 'path': path + "webpage.html"}
    try:
        # get all jsons and add them inside a new json dic as
        count = 0
        all_json = {}
        for json_data in hxs.xpath(".//*[@type='application/json']//text()").extract():
            all_json[count] = json.loads(json_data)
            count = count + 1
            # exracted json from the webpage
        f = open(path + "webpage_json.json", 'w')
        f.write(json.dumps(all_json))
        f.close()
        temp_dic['webpage_json'] = {'status': 'success', 'href': url, 'headers': fixed_headers,
                                    'path': path + "webpage_json.json", "json_xpath": ".//*[@id='data-state']//text()"}
    except:
        temp_dic['webpage_json'] = {'status': 'fail', 'href': url, 'headers': fixed_headers,
                                    'path': path + "webpage_json.json", "json_xpath": ".//*[@id='data-state']//text()"}
    try:
        # extraction of api_key and total count of reviews
        api_key = deep_search('api_config', all_json)['api_config']['key']
    except:
        pass

    end_time = time.time()
    temp_dic['execution_time'] = end_time - start_time
    temp_dic['api_key'] = api_key
    return temp_dic


def load_listing_calendar(listing_dic):
    '''
    pending ->
    1) sha26HASH - try to convert page into a hash value with diff algo and see if we can achieve this
    2) _cb - whats this? looks like some call back value - check javascript callbacks in traffic
    3) are the variables fixed in all listings ? what if we modify?
    '''
    temp_dic = {}
    start_time = time.time()
    s = requests.session()
    s.proxies.update(proxies, verify=False)
    path = listing_dic['info']['path']
    api_key = listing_dic['info']['api_key']
    listing_id = listing_dic['info']['listing_id']
    required_headers = {
        'X-Airbnb-API-Key': api_key,
        'X-Airbnb-GraphQL-Platform': 'web',
        'X-Airbnb-GraphQL-Platform-Client': 'minimalist-niobe',
        'X-Airbnb-Supports-Airlock-V2': 'true',
        # 'X-CSRF-Token':'V4$.airbnb.com$UXeKgVkvS0Q$2Udee5jit3pljOZ0S9IcSYj8hEELNlUvLz9lYa_YmTk=',
        'X-CSRF-Without-Token': '1'
    }
    # if we are ading fixed headers requets are getting failed -> look later once pipeline is done
    # required_headers.update(fixed_headers)
    today = date.today()
    url_calendar = 'https://www.airbnb.com/api/v3/PdpAvailabilityCalendar?\
    operationName=PdpAvailabilityCalendar&locale=en&currency=USD\
    &variables={"request":{"count":12,"listingId":"' + str(listing_id) + '","month":' + str(
        today.month) + ',"year":' + str(today.year) + '}}\
    &extensions={"persistedQuery":{"version":1,"sha256Hash":"dc360510dba53b5e2a32c7172d10cf31347d3c92263f40b38df331f0b363ec41"}}\
    &_cb=1iyg0jf1jmcby40yidbz60s77mks'
    try:
        # response=s.get(url_calendar,headers=required_headers,verify=False).text
        data, st = load_url(url_calendar, required_headers)
        f = open(path + "calendar_json.json", 'w')
        f.write(json.dumps(data))
        f.close()
        temp_dic['json'] = {'status': st, 'href': url_calendar, 'headers': required_headers,
                            'path': path + "calendar_json.json"}
    except:
        temp_dic['json'] = {'status': 'fail', 'href': url_calendar, 'headers': required_headers,
                            'path': path + "calendar_json.json"}
    end_time = time.time()
    temp_dic['execution_time'] = end_time - start_time
    return temp_dic


def load_listing_photos(listing_dic):
    '''
    pending ->
    1) sha26HASH - try to convert page into a hash value with diff algo and see if we can achieve this
    2) _cb - whats this? looks like some call back value - check javascript callbacks in traffic
    3) are the variables fixed in all listings ? what if we modify?
    '''
    temp_dic = {}
    start_time = time.time()
    path = listing_dic['info']['path']
    api_key = listing_dic['info']['api_key']
    listing_id = listing_dic['info']['listing_id']
    required_headers = {
        'X-Airbnb-API-Key': api_key,
        'X-Airbnb-GraphQL-Platform': 'web',
        'X-Airbnb-GraphQL-Platform-Client': 'minimalist-niobe',
        'X-Airbnb-Supports-Airlock-V2': 'true',
        # 'X-CSRF-Token':'V4$.airbnb.com$UXeKgVkvS0Q$2Udee5jit3pljOZ0S9IcSYj8hEELNlUvLz9lYa_YmTk=',
        'X-CSRF-Without-Token': '1'
    }
    # if we are ading fixed headers requets are getting failed -> look later once pipeline is done
    # required_headers.update(fixed_headers)
    url_photos = 'https://www.airbnb.com/api/v3/PdpPhotoTour?\
        operationName=PdpPhotoTour&locale=en&currency=USD\
        &variables={"request":{"id":"' + str(listing_id) + '","translateUgc":null}}\
        &extensions={"persistedQuery":{"version":1,"sha256Hash":"f353bec94b2133c542011751957561b36fb0adb20def2d3466f897a18b0e7320"}}\
        &_cb=flhefjhnew1e'

    try:
        # response=s.get(url_photos,headers=required_headers,verify=False).text
        data, st = load_url(url_photos, required_headers)
        f = open(path + "photos_json.json", 'w')
        f.write(json.dumps(data))
        f.close()
        temp_dic['json'] = {'status': st, 'href': url_photos, 'headers': required_headers,
                            'path': path + "photos_json.json"}
    except:
        temp_dic['json'] = {'status': 'fail', 'href': url_photos, 'headers': required_headers,
                            'path': path + "photos_json.json"}
    end_time = time.time()
    temp_dic['execution_time'] = end_time - start_time
    return temp_dic


def load_listing_stays(listing_dic):
    '''
    pending ->
    1) sha26HASH - try to convert page into a hash value with diff algo and see if we can achieve this
    2) _cb - whats this? looks like some call back value - check javascript callbacks in traffic
    3) are the variables fixed in all listings ? what if we modify?
    '''
    temp_dic = {}
    start_time = time.time()
    s = requests.session()
    s.proxies.update(proxies, verify=False)
    path = listing_dic['info']['path']
    api_key = listing_dic['info']['api_key']
    listing_id = listing_dic['info']['listing_id']
    required_headers = {
        'X-Airbnb-API-Key': api_key,
        'X-Airbnb-GraphQL-Platform': 'web',
        'X-Airbnb-GraphQL-Platform-Client': 'minimalist-niobe',
        'X-Airbnb-Supports-Airlock-V2': 'true',
        # 'X-CSRF-Token':'V4$.airbnb.com$UXeKgVkvS0Q$2Udee5jit3pljOZ0S9IcSYj8hEELNlUvLz9lYa_YmTk=',
        'X-CSRF-Without-Token': '1'
    }
    _api_path = '/api/v3/StaysPdpSections'
    query = {
        'operationName': 'StaysPdpSections',
        'locale': 'en-IN',
        'currency': 'USD',
        'variables': {
            'request': {
                'id': listing_id,
                'layouts': ['SIDEBAR', 'SINGLE_COLUMN'],
                'pdpTypeOverride': None,
                'translateUgc': None,
                'preview': False,
                'bypassTargetings': False,
                'displayExtensions': None,
                'adults': '1',
                'children': None,
                'infants': None,
                'causeId': None,
                'disasterId': None,
                'priceDropSource': None,
                'promotionUuid': None,
                'selectedCancellationPolicyId': None,
                'forceBoostPriorityMessageType': None,
                'privateBooking': False,
                'invitationClaimed': False,
                'discountedGuestFeeVersion': None,
                'staysBookingMigrationEnabled': False,
                'useNewSectionWrapperApi': False,
                'previousStateCheckIn': None,
                'previousStateCheckOut': None,
                'federatedSearchId': None,
                'interactionType': None,
                'searchId': None,
                'sectionIds': None,
                'checkIn': None,
                'checkOut': None,
                'p3ImpressionId': 'p3_1608841700_z2VzPeybmBEdZG20'
            }
        },
        'extensions': {
            'persistedQuery': {
                'version': 1,
                'sha256Hash': '625a4ba56ba72f8e8585d60078eb95ea0030428cac8772fde09de073da1bcdd0'
            }
        }
    }
    q = {}
    q['variables'] = json.dumps(query['variables'], separators=(',', ':'))
    q['extensions'] = json.dumps(query['extensions'], separators=(',', ':'))
    query_url = urlencode(q)
    url_stays = urlunparse(['https', 'www.airbnb.com', _api_path, None, query_url, None])
    # if we are ading fixed headers requets are getting failed -> look later once pipeline is done
    # required_headers.update(fixed_headers)
    try:
        # response=s.get(url_stays,headers=required_headers,verify=False).text
        data, st = load_url(url_stays, required_headers)
        f = open(path + "stays_json.json", 'w')
        f.write(json.dumps(data))
        f.close()
        temp_dic['json'] = {'status': st, 'href': url_stays, 'headers': required_headers,
                            'path': path + "stays_json.json"}
    except:
        temp_dic['json'] = {'status': 'fail', 'href': url_stays, 'headers': required_headers,
                            'path': path + "stays_json.json"}
    end_time = time.time()
    temp_dic['execution_time'] = end_time - start_time
    return temp_dic


def load_listing_reviews(listing_dic):
    '''
    pending ->
    1) sha26HASH - try to convert page into a hash value with diff algo and see if we can achieve this
    2) _cb - whats this? looks like some call back value - check javascript callbacks in traffic
    3) are the variables fixed in all listings ? what if we modify?
    '''
    temp_dic = {}
    start_time = time.time()
    s = requests.session()
    s.proxies.update(proxies, verify=False)
    path = listing_dic['info']['path']
    api_key = listing_dic['info']['api_key']
    listing_id = listing_dic['info']['listing_id']
    total_reviews = listing_dic['info']['total_reviews']
    offset_list = [i for i in range(int(total_reviews)) if i % 7 == 0 and i < int(total_reviews) and i != 0]
    if not offset_list:
        offset_list = [7]
    required_headers = {
        'Referer': 'https://www.airbnb.com/',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        'TE': 'Trailers',
        'X-Airbnb-API-Key': api_key,
        'X-Airbnb-GraphQL-Platform': 'web',
        'X-Airbnb-GraphQL-Platform-Client': 'minimalist-niobe',
        'X-Airbnb-Supports-Airlock-V2': 'true',
        # 'X-CSRF-Token':'V4$.airbnb.com$UXeKgVkvS0Q$2Udee5jit3pljOZ0S9IcSYj8hEELNlUvLz9lYa_YmTk=',
        'X-CSRF-Without-Token': '1'
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
        url_review = urlunparse(['https', 'www.airbnb.com', _api_path, None, query_url, None])
        try:
            # response=s.get(url_review,headers=required_headers,verify=False).text
            data, st = load_url(url_review, required_headers)
            f = open(path + "reviews_json_" + str(offset) + ".json", 'w')
            f.write(json.dumps(data))
            f.close()
            offset_dic['json'] = {'status': st, 'href': url_review, 'headers': required_headers,
                                  'path': path + "reviews_json_" + str(offset) + ".json", "offset": offset}
        except:
            offset_dic['json'] = {'status': 'fail', 'href': url_review, 'headers': required_headers,
                                  'path': path + "reviews_json_" + str(offset) + ".json", "offset": offset}
        output_list.append(offset_dic)
    end_time = time.time()
    temp_dic['output_list'] = output_list
    temp_dic['execution_time'] = end_time - start_time
    return temp_dic


def call_and_validate_functions(listing_dic, function_name):
    for r in range(5):
        try:
            if function_name == 'load_listing_page':
                listing_dic['load_listing_page'] = load_listing_page(listing_dic)
                return listing_dic
            if function_name == 'load_listing_stays':
                listing_dic['load_listing_stays'] = load_listing_stays(listing_dic)
                return listing_dic
            if function_name == 'load_listing_calendar':
                listing_dic['load_listing_calendar'] = load_listing_calendar(listing_dic)
                return listing_dic
            if function_name == 'load_listing_photos':
                listing_dic['load_listing_photos'] = load_listing_photos(listing_dic)
                return listing_dic
            if function_name == 'load_listing_reviews':
                listing_dic['load_listing_reviews'] = load_listing_reviews(listing_dic)
                return listing_dic
        except:
            pass
    return listing_dic


def get_all_listings(search_string, placeId):
    required_headers = {
        'Referer': 'https://www.airbnb.com/',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        'TE': 'Trailers',
        'X-Airbnb-API-Key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20',
        'X-Airbnb-GraphQL-Platform': 'web',
        'X-Airbnb-GraphQL-Platform-Client': 'minimalist-niobe',
        'X-Airbnb-Supports-Airlock-V2': 'true',
        # 'X-CSRF-Token':'V4$.airbnb.com$UXeKgVkvS0Q$2Udee5jit3pljOZ0S9IcSYj8hEELNlUvLz9lYa_YmTk=',
        'X-CSRF-Without-Token': '1'
    }
    _api_path = '/api/v3/ExploreSearch'
    s = requests.Session()
    query_curr = {
        'operationName': 'ExploreSearch',
        'locale': 'en',
        'currency': 'USD',
        'variables': {
            'request': {
                'metadataOnly': False,
                'version': '1.7.9',
                'itemsPerGrid': 20,
                # 'priceMin': ,
                # 'priceMin': price_max,
                'tabId': 'home_tab',
                'refinementPaths': ['/homes'],
                'source': 'structured_search_input_header',
                'searchType': 'search_query',
                'query': search_string,
                'cdnCacheSafe': False,
                'simpleSearchTreatment': 'simple_search_only',
                'treatmentFlags': [
                    # 'storefronts_january_2022_homepage_desktop_web',
                    'flexible_dates_options_extend_one_three_seven_days',
                    'super_date_flexibility',
                    'search_input_placeholder_phrases',
                    'listings_per_page_25'
                ],
                'screenSize': 'large'
            }
        },
        'extensions': {
            'persistedQuery': {
                'version': 1,
                'sha256Hash': '65ab82189c798fb15bf4d94de3fd2fd3e8d1c92dc418b7da4b3677ce3408e70e'
            }
        }
    }
    c = 0
    search_results = {}
    for r in list(range(0, 1100, 5)):
        print('price range --', str(r))
        price_min = r
        price_max = r + 5
        query_curr['variables']['request']['priceMin'] = price_min
        query_curr['variables']['request']['priceMin'] = price_max
        all_offset = [i for i in range(0, 300) if i % 20 == 0]
        for offset in all_offset:
            query = query_curr
            if offset != 0:
                query['variables']['request']['itemsOffset'] = offset
                query['variables']['request']['searchType'] = 'pagination'
                query['variables']['request']['placeId'] = placeId  # 'ChIJm0xQOaul4IgRntFVevWwC7s'
                query['variables']['request']['sectionOffset'] = '3'
                query['variables']['request']['sectionOffset'] = '3'
            q = {}
            q['variables'] = json.dumps(query['variables'], separators=(',', ':'))
            q['extensions'] = json.dumps(query['extensions'], separators=(',', ':'))
            query_url = urlencode(q)
            url_search = urlunparse(['https', 'www.airbnb.com', _api_path, None, query_url, None])
            # data,st=load_url(url_search,required_headers)
            data = s.get(url_search, headers=required_headers).text
            json_data = json.loads(data)
            # f=open(r"C:\Users\admin\Desktop\sandeep_aaron_projects\p4_airbnb\search_strings_dumps\\"+search_string+'_'+str(offset)+'.json','w')
            # f.write(json.dumps(json.loads(data)))
            # f.close()
            for items in list(findalloccurance(json_data, 'items')):
                for l in items:
                    if l['__typename'] == 'DoraListingItem':
                        listing_id = l['listing']['id']
                        total_reviews = l['listing']['reviewsCount']
                        pricing_factor = l['pricingQuote']['monthlyPriceFactor']
                        canInstantBook = l['pricingQuote']['canInstantBook']

                        priceString = l['pricingQuote']['priceString']
                        rateType = l['pricingQuote']['rateType']
                        weeklyPriceFactor = l['pricingQuote']['weeklyPriceFactor']
                        verified = l['verified']['__typename']
                        search_results[c] = {'listing_id': listing_id, 'total_reviews': total_reviews, 'offset': offset,
                                             'pricing_factor': pricing_factor, 'canIn stantBook': canInstantBook,
                                             'priceString': priceString, 'rateType': rateType,
                                             'weeklyPriceFactor': weeklyPriceFactor,
                                             'verified': verified}
                        c = c + 1
    return search_results


from distutils.dir_util import copy_tree
import os

# a=[search_results[s]['listing_id'] for s in search_results]
import pandas as pd
from datetime import date

today = date.today()
d1 = today.strftime("%b-%d-%Y")

placeId = "ChIJm0xQOaul4IgRntFVevWwC7s"

search_string = 'Cape Canaveral'

######resume above this

search_results_temp = get_all_listings(search_string, placeId)
# search_results_temp1=json.loads(open('search_results.json').read())
unique_listing_ids = list(set([search_results_temp[s]['listing_id'] for s in search_results_temp]))
done = [file.split('\\')[-1] for file in glob.glob('listing_dumps_bck\*')]
search_results = {}
count = 0
for u in unique_listing_ids:
    if u in done:
        copy_tree('listing_dumps_bck\\' + str(u), 'listing_dumps\\' + str(u))
        continue
    for s in search_results_temp:
        if u == search_results_temp[s]['listing_id']:
            search_results[count] = search_results_temp[s]
            count += 1
            break

open("search_results.json", "w").write(json.dumps(search_results))

##$start
search_results = json.loads(open("search_results.json").read())
# search_results=[search_results[int(l)] for l in unique_listing_ids]
'''
import collections
all_unique_ids=list(set([search_results[s]['listing_id'] for s in search_results]))
all_ids=[search_results[s]['listing_id'] for s in search_results]

duplicates=[x for x, y in collections.Counter(all_ids).items() if y > 1]
for s in search_results:
    if search_results[s]['listing_id']=='37594524':
        print(search_results[s])
'''

already_done = [file.split('\\')[-1].replace(".pdf", "") for file in glob.glob('listing_dumps\*')]
home_path = os.path.join('listing_dumps')
count = 0
for i in search_results:
    # break
    print(i)
    result = search_results[i]
    # href='https://www.airbnb.com/rooms/37514380?federated_search_id=6bf7d5c6-aa82-4116-bfb5-4a128b212dc6&locale=en&_set_bev_on_new_domain=1620282064_MDAwZWMxYjFlMWJh&source_impression_id=p3_1621329107_JMPS6lDKj4LMwJEJ&guests=1&adults=1'
    listing_dic = {'info': result}
    listing_dic['info']['href'] = "https://www.airbnb.com/rooms/" + result['listing_id']
    listing_id = result['listing_id']
    if listing_id in already_done:
        continue
    count += 1
    listing_dic['info']['listing_id'] = listing_id
    listing_dic['info']['total_reviews'] = result['total_reviews']
    os.makedirs(os.path.join(home_path, str(listing_id)), exist_ok=True)
    path = os.path.join(home_path, listing_id) + '\\'
    listing_dic['info']['path'] = path
    # lets load listing page
    listing_dic = call_and_validate_functions(listing_dic, 'load_listing_page')
    # lets also store api_key in the info key
    if 'api_key' in listing_dic['load_listing_page']:
        listing_dic['info']['api_key'] = listing_dic['load_listing_page']['api_key']
    else:
        print('not able to get the key => mark the status and move on')
        break  # just only for testing purpose -> longer run - put a count - if 5 consecutive request no able to fetch api, stop code and raise and alert

    # lets load calender page
    listing_dic = call_and_validate_functions(listing_dic, 'load_listing_calendar')

    # lets load photos
    listing_dic = call_and_validate_functions(listing_dic, 'load_listing_photos')

    # get list of all reveiws
    listing_dic = call_and_validate_functions(listing_dic, 'load_listing_reviews')

    # get list of all reveiws
    listing_dic = call_and_validate_functions(listing_dic, 'load_listing_stays')

    listing_dic['info']['status_json'] = path + 'listing_dic.json'

    f = open(path + 'listing_dic.json', 'w')
    f.write(json.dumps(listing_dic))
    f.close()

    ##### temporary - get all the listings for a search results