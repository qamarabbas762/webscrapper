from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome(service=Service(r'C:\Users\Ashu\Desktop\TOOLS\chromedriver-win64\chromedriver.exe'))

def hotel(url):
    # driver.get("https://www.airbnb.co.in/rooms/959367233441980708?adults=2&children=1&enable_m3_private_room=true&infants=0&pets=0&check_in=2024-03-11&check_out=2024-03-13&source_impression_id=p3_1710113949_aBBJWTcnym89kE4l&previous_page_section_name=1000&federated_search_id=c1f1945b-26d9-41de-b151-5f17e243237a")
    driver.get(url)
    time.sleep(5)
    desc = driver.find_element(By.XPATH,'//h1').text
    hotel = driver.find_element(By.XPATH,"//div[contains(@class,'toieuka')]//h2").text
    amenities = "".join([i.text for i in driver.find_elements(By.XPATH,"//ol[contains(@class,'lgx66tx')]//li")[:4]])
    price = driver.find_elements(By.XPATH,'//span[@class="_1y74zjx"]')[1].text

    facilities = driver.find_elements(By.XPATH,'//span//span[starts-with(@class,"lrl13de")]')[0].text

    info_dict = {
        'Hotel':hotel,
        'Description':desc,
        'Amenities':amenities
    }
    return info_dict

def main_page():
    driver.get("https://www.airbnb.co.in/s/Goa--India/homes?adults=2&place_id=ChIJQbc2YxC6vzsRkkDzYv-H-Oo&checkin=2024-03-11&checkout=2024-03-14&children=1&tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&query=Goa%2C%20India&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-04-01&monthly_length=3&monthly_end_date=2024-07-01&price_filter_input_type=0&price_filter_num_nights=3&channel=EXPLORE&ne_lat=17.120264505568986&ne_lng=77.21519965312808&sw_lat=14.221303911086254&sw_lng=70.46869119110025&zoom=6.582378543307216&zoom_level=6.582378543307216&search_by_map=true&search_type=user_map_move")
    hotel_url = driver.find_elements(By.XPATH,'//div[@itemprop="itemListElement"]//div[@class="cy5jw6o atm_5j_8todto atm_70_87waog atm_j3_1u6x1zy atm_jb_4shrsx atm_mk_h2mmj6 atm_vy_7abht0  dir dir-ltr"]//a[contains(@class,"atm_uc_glywfm_18zk5v0_pynvjw")]')
    # for hotel in hotel_url:
    links = [hotel.get_attribute("href") for hotel in hotel_url]
    return links


if __name__ =="__main__":
    main_url = main_page()
    time.sleep(10)
    # info= hotel(main_url)
    # print(info)
    for link in main_url:
        info = hotel(link)
        print(info)









time.sleep(15)