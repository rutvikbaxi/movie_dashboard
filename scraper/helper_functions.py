from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd
import re
import time


def scroll_page(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)
    cinema_list = driver.find_elements(By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")
    driver.execute_script("window.scrollTo(0, 0);")

def next_day_click(driver):
    a = ActionChains(driver)
    m= driver.find_element(By.CLASS_NAME, "date-filter")
    a.move_to_element(m).perform()

    btn = driver.find_elements(By.CSS_SELECTOR, ".date-item.carousel-cell.ng-star-inserted")
    btn[1].click()
    time.sleep(5)

def get_cinema(driver, i):
    #get cinema list
    scroll_page(driver)
    cinema_list = driver.find_elements(By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")
    try:
        cinema = cinema_list[i]
        return cinema
    except:
        return None 

def cinema_click(cinema):
    cinema_button = cinema.find_element(By.CLASS_NAME, "cinema-title")
    cinema_button.click()

def showtime_click(cinema, show_times, index):
    #get all the h4 elements containing Hindi-2D
    hindi_2d_elements = cinema.find_elements(By.XPATH, '//h4[contains(@class, "type-title") and contains(text(), "HINDI- 2D")]')
    for hindi_2d_element in hindi_2d_elements:
        if len(hindi_2d_element.text)==0:
            continue #there might be empty classes
        ul_element = hindi_2d_element.find_element(By.XPATH, './following-sibling::ul[@class="type-time-slots ng-star-inserted"]')
        
        #get time slots for Hindi 2D in that cinema
        slot_elements = ul_element.find_elements(By.XPATH, './/li[@class="ng-star-inserted"]') 
        for slot in slot_elements:
            #pick the first available slot
            if (len(slot.text.strip()) != 0) and (slot.find_element(By.XPATH, './/span').get_attribute("class").split("-")[1] != "default"):
                show_times[index] = {
                    "Theatre" : cinema.find_element(By.CLASS_NAME, "title").text,
                    "Time" : slot.text.strip(),
                    "type" : slot.find_element(By.XPATH, './/span').get_attribute("class").split("-")[1]
                } 
                break
        break
    slot.click()

def wait_banners(driver):

    try:
        time.sleep(2)
        baggage_btn = driver.find_element(By.CLASS_NAME, "custom-popup-container")
        baggage_btn.find_element(By.CSS_SELECTOR, ".custom-popup-button.ng-star-inserted").click()
    except:
        print("no bag")

    try:
        #open the seating
        time.sleep(2)
        wait = WebDriverWait(driver, 1)
        loaded = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "skip-btn")))

        #press the skip button in case some promo comes
        skip_btn = driver.find_element(By.CLASS_NAME, "skip-btn")
        skip_btn.click()

    except:
        print("no skip")

    #wait for the T&C banner to load and click the close button 
    time.sleep(5)
    close_class = driver.find_element(By.CLASS_NAME, "modal-content-header")
    btn = close_class.find_element(By.CLASS_NAME, "ion-android-close")
    btn.click()

def seat_info(driver, show_times, n):
    #extract seats info
    seat_prices_array = [title.find_element(By.XPATH, ".//span").text for title in driver.find_elements(By.CLASS_NAME, "seats-col") if title.find_element(By.XPATH, ".//span").get_attribute("class")=="area hshshs"]
    seat_prices = [int(float(re.search(r'(\d+\.\d+)', seat).group(1))) for seat in seat_prices_array]

    n_seats = 0
    n_seats_available = 0
    rows = driver.find_elements(By.CSS_SELECTOR, ".seats-row.ng-star-inserted")
    for row in rows:
        n_seats+= len(row.find_elements(By.CSS_SELECTOR, ".seats-col.ng-star-inserted"))
        n_seats_available += len([1 for x in row.find_elements(By.XPATH, './/span') if x.get_attribute("class") == 'seat current'])
    
    show_times[n]["TotalSeats"] = n_seats
    show_times[n]["SeatsAvailable"] = n_seats_available    
    show_times[n]["Cost"] = '/'.join(map(str, seat_prices))

    #close this seat and go back to shows listing
    btn = driver.find_element(By.CLASS_NAME, "ion-arrow-left-c")
    btn.click()

    return show_times