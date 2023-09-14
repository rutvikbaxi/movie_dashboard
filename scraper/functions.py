from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from helper_functions import *


def create_cinemas_list(city):
    url = "https://www.pvrcinemas.com/cinemas/"+city
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(1)
    driver.refresh()
    time.sleep(3)
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
    next_day_click(driver)

    scroll_page(driver)
    scroll_page(driver)
    cinema_list = driver.find_elements(By.CSS_SELECTOR, ".cinema-holder.ng-star-inserted")
    show_times=dict()
    n = len(cinema_list[:])

    for i in range(n):
        time.sleep(3)
        scroll_page(driver)
        cinema = get_cinema(driver, i)
        print(i, n, cinema.find_element(By.CLASS_NAME, "title").text)
        if cinema in [show_times[ix]["Theatre"] for ix in show_times.keys()]:
            continue
        cinema_click(cinema)
        index = len(show_times)
        slot = showtime_click(cinema, show_times, index)
        wait_banners(driver)
        seat_info(driver, show_times, index) 

def final_data(shows, theatres, movie_name, city_name):
    final_df = shows.merge(theatres, how="left", on="Theatre")
    final_df["Movie"] = movie_name
    final_df["City"] = city_name
    final_df["Longitude"] = final_df["Longitude"].astype(float)
    final_df["Latitude"] = final_df["Latitude"].astype(float)
    final_df.fillna(0, inplace=True)
    return final_df


