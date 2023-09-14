from functions import * 

movie_name = "JAWAN"
city_name = "Bengaluru"
theatres = create_cinemas_list(city_name)
driver = webdriver.Chrome()
open_booking_page(movie_name, driver)
shows = create_show_list(driver)
final_df = final_data(shows, theatres, movie_name, city_name)

table_name = movie_name+city_name
import pandas as pd
import sqlite3
conn = sqlite3.connect('todo.db')
# final_df.to_sql("movie_shows", conn, if_exists='append', index=True)
# conn.commit()
conn.close()