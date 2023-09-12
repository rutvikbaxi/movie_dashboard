from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import copy


def create_cinemas_list(city):
    url = "https://www.pvrcinemas.com/cinemas/"+city
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)

    theatres = dict()
    container = driver.find_element(By.CSS_SELECTOR, ".cinema-locator-carousel")
    theatre_list = container.find_elements(By.CLASS_NAME, "cinema-box")

    for theatre in theatre_list:
        name = theatre.find_element(By.CLASS_NAME, "box-title").text
        
        gmap_add = theatre.find_element(By.CSS_SELECTOR, "ul.options li a")
        href_value = gmap_add.get_attribute("href")
        lat_start = href_value.find("lat=") + 4
        lat_end = href_value.find("&", lat_start)
        lng_start = href_value.find("lng=") + 4
        latitude = href_value[lat_start:lat_end].strip()
        longitude = href_value[lng_start:].strip()

        theatres[len(theatres)]={
            "Theatre": name,
            "Latitude":latitude,
            "Longitude":longitude
        }

    cinema_df=pd.DataFrame(theatres).T
    driver.quit()
    return cinema_df


def open_booking_page(movie_name, driver):
    
    url = "https://www.pvrcinemas.com/Bengaluru/cinemas/showtimes"
    driver.get(url)

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "movie-box")))

    movie_elements = driver.find_elements(By.CLASS_NAME, "movie-box")
    for movie_element in movie_elements:
        movie_title = movie_element.find_element(By.CLASS_NAME, "m-title")
        if movie_title and movie_name in movie_title.text:

            booking_button = movie_element.find_element(By.CSS_SELECTOR, ".btn.btn-primary-white.text-uppercase.ng-star-inserted")
            driver.get(booking_button.get_attribute("href"))
            break 

def create_show_list(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    cinema_list = driver.find_elements(By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    cinema_list = driver.find_elements(By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")
    driver.execute_script("window.scrollTo(0, 0);")
    len(cinema_list)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    cinema_list = driver.find_elements(By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")
    driver.execute_script("window.scrollTo(0, 0);")

    show_times=dict()
    n = len(copy.deepcopy(cinema_list))
    # n = 3
    try:
        for i in range(n):
            time.sleep(2)
            #get cinema list
            cinema_list = driver.find_elements(By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")
            try:
                cinema = cinema_list[i]
            except:
                break 

            print(i, n, cinema.find_element(By.CLASS_NAME, "title").text)

            #click on the cinema to get seating
            cinema_button = cinema.find_element(By.CLASS_NAME, "cinema-title")
            cinema_button.click()

            #get all the h4 elements containing Hindi-2D
            hindi_2d_elements = cinema.find_elements(By.XPATH, '//h4[contains(@class, "type-title") and contains(text(), "HINDI- 2D")]')
            for hindi_2d_element in hindi_2d_elements:
                if len(hindi_2d_element.text)==0:
                    continue #there might be empty classes
                ul_element = hindi_2d_element.find_element(By.XPATH, './following-sibling::ul[@class="type-time-slots ng-star-inserted"]')
                
                #get time slots for Hindi 2D in that cinema
                slot_elements = ul_element.find_elements(By.XPATH, './/li[@class="ng-star-inserted"]') 
                for slot in slot_elements:
                    n=len(show_times)
                    #pick the first available slot
                    if (len(slot.text.strip()) != 0) and (slot.find_element(By.XPATH, './/span').get_attribute("class").split("-")[1] != "default"):
                        show_times[n] = {
                            "Theatre" : cinema.find_element(By.CLASS_NAME, "title").text,
                            "Time" : slot.text.strip(),
                            "type" : slot.find_element(By.XPATH, './/span').get_attribute("class").split("-")[1]
                        } 
                        break
                break

            try:
                #open the seating
                slot.click()
                time.sleep(3)
                wait = WebDriverWait(driver, 5)
                loaded = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "skip-btn")))

                #press the skip button in case some promo comes
                skip_btn = driver.find_element(By.CLASS_NAME, "skip-btn")
                skip_btn.click()

            except:
                print("no offers")

            #wait for the T&C banner to load and click the close button 
            time.sleep(5)
            wait = WebDriverWait(driver, 5)
            loaded = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modal-content-header")))

            close_class = driver.find_element(By.CLASS_NAME, "modal-content-header")
            btn = close_class.find_element(By.CLASS_NAME, "ion-android-close")
            btn.click()

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
            wait = WebDriverWait(driver, 5)
            element_on_next_page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")))
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            cinema_list = driver.find_elements(By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")
            driver.execute_script("window.scrollTo(0, 0);")

    except:
        print("error")
        return pd.DataFrame(show_times).T
    return pd.DataFrame(show_times).T

def final_data(shows, theatres, movie_name, city_name):
    final_df = shows.merge(theatres, how="left", on="Theatre")
    final_df["Movie"] = movie_name
    final_df["City"] = city_name
    return final_df


