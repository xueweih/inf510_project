#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 14:46:16 2019

@author: yvettehhhuang96
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import copy
from googleplaces import GooglePlaces
import googlemaps
import sqlite3
import argparse


#first class: get basic info from airbnb 
class airbnb_scrapy(object):
    
    def get_ratings(self, url):
        rating_list = []

        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')              

        for i in range(len(soup.select('div[class="_1ebt2xej"]'))):
            rating = soup.select('div[class="_4ntfzh"]')[i].select('span[class ="_ky9opu0"]')
            try:
                rating_list.append(rating[0].text)
            except:
                rating_list.append(0)

        return rating_list


    def get_review_number(self, url):
        review_list = []

        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')              

        for i in range(len(soup.select('div[class="_1ebt2xej"]'))):
            review_number = soup.select('div[class="_4ntfzh"]')[i].select('span[class="_14e6cbz"]')
            try:
                review_list.append(eval(review_number[0].text))
            except:
                review_list.append(0)

        return review_list

    
    def get_names_prices_urls(self, url):
        house_names_list = []
        price_display_list = []
        house_url_list = []

        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')              

        for i in range(len(soup.select('div[class="_1ebt2xej"]'))):
            name = soup.select('div[class="_1ebt2xej"]')[i].text
            house_names_list.append(name)

            price_display = soup.select('span[class="_1p7iugi"]')[i].text
            price = price_display[price_display.rindex('$')+1:]
            price_display_list.append(price)

            str1 = str(soup.select('a[class="_i24ijs"]')[i]).split('"')
            house_url = 'https://www.airbnb.com' + str1[7]
            house_url_list.append(house_url)

        return house_names_list, price_display_list, house_url_list


    def get_next_page_url(self, url):
    
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        href = soup.select('li[class="_r4n1gzb"]')[0].select('a')[0].get("href")
        next_page_url = 'https://www.airbnb.com'+href

        return next_page_url

    
    def get_id_lat_lng_1(self, url):

        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser') 

        t = soup.select('script[id="data-state"]')[0].text
        dict_t = json.loads(t)

        listings_1 = dict_t['bootstrapData']['reduxData']['exploreTab']['response']['explore_tabs'][0]['sections'][1]['listings']
        listings_2 = dict_t['bootstrapData']['reduxData']['exploreTab']['response']['explore_tabs'][0]['sections'][3]['listings']

        id_lat_lng = []
        for i in range(len(listings_1)):
            ternary_tuple = []
            addr_info_list = listings_1[i]['listing']
            h_id = addr_info_list['id']
            ternary_tuple.append(h_id)
            h_lat = addr_info_list['lat']
            h_lng = addr_info_list['lng']
            ternary_tuple.append((h_lat, h_lng))
            id_lat_lng.append(ternary_tuple)

        for i in range(len(listings_2)):
            ternary_tuple = []
            addr_info_list = listings_1[i]['listing']
            h_id = addr_info_list['id']
            ternary_tuple.append(h_id)
            h_lat = addr_info_list['lat']
            h_lng = addr_info_list['lng']
            ternary_tuple.append((h_lat, h_lng))
            id_lat_lng.append(ternary_tuple)

        return id_lat_lng

        
    def get_id_lat_lng_other(self, url):
    
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        t = soup.select('script[id="data-state"]')[0].text
        dict_t = json.loads(t)

        listings = dict_t['bootstrapData']['reduxData']['exploreTab']['response']['explore_tabs'][0]['sections'][0]['listings']

        id_lat_lng = []
        for i in range(len(listings)):
            ternary_tuple = []
            addr_info_list = listings[i]['listing']
            h_id = addr_info_list['id']
            ternary_tuple.append(h_id)
            h_lat = addr_info_list['lat']
            h_lng = addr_info_list['lng']
            ternary_tuple.append((h_lat, h_lng))
            id_lat_lng.append(ternary_tuple)

        return id_lat_lng
    
    
    def get_one_page_data(self, url):

        ratings = self.get_ratings(url)
        review_num = self.get_review_number(url)
        names = self.get_names_prices_urls(url)[0]
        prices = self.get_names_prices_urls(url)[1]
        house_urls = self.get_names_prices_urls(url)[2]

        def get_house_id(url):
            house_url_list = self.get_names_prices_urls(url)[2]
            house_id_list = []
            for each_url in house_url_list:
                house_id = each_url[(each_url.find('rooms')+6):(each_url.find('location')-1)]
                house_id_list.append(house_id)         
            return house_id_list  
            
        house_ids = get_house_id(url)
        
        airbnb_data_list = [house_ids, names, prices, ratings, review_num, house_urls]
        airbnb_data_df_temp = pd.DataFrame(airbnb_data_list)
        airbnb_data_df = pd.DataFrame(airbnb_data_df_temp.values.T, columns = ['house_id','house_name','price_per_night','rating','review_num', 'house_url'])

        return airbnb_data_df


#second class: some data processing
class data_processing(object):
    
    def drop_duplicate_house(self, df):
        
        origin = list(df.iloc[:,0])
        cop1 = copy.deepcopy(origin)

        uniq_elem = []
        for elem in origin:
            a1 = cop1.index(elem)
            cop1.pop(a1)
            try:
                cop1.index(elem)
            except:
                uniq_elem.append(elem)

        unique_index_list = []
        for elem in uniq_elem:
            ori_index = origin.index(elem)
            unique_index_list.append(ori_index)

        drop_index = [i for i in range(len(origin)) if i not in unique_index_list]
        df_unique = df.drop(drop_index)
        df_unique.reset_index(drop = True, inplace = True)

        return df_unique
    
    
    def delete_mistaken_id(self, df):
    
        for elem in df.iloc[:,0]:
            try:
                elem = eval(elem)
            except:
                df.drop([list(df.iloc[:,0]).index(elem)], inplace = True)
                df.reset_index(drop = True, inplace = True)
                
        return df


#third class: get basic info from agoda (console___api)
class agoda_scrapy(object):
    
    def get_agoda_info(self, url, headers, start, end):
        id_list = []
        name_list = []
        price_list = []
        score_list = []
        review_num_list = []
        url_list = []
        lat_lng_list = []

        for i in range(start, end):
            request_payload = {"AddressName": None, "Adults": 2, "BankCid": None, "BankClpId": None, "CheckIn": "2019-12-25T00:00:00", "CheckOut": "2019-12-26T00:00:00", "CheckboxType": 0, "ChildAges": [], "ChildAgesStr": None, "Children": 0, "Cid": -218, "CityEnglishName": None, "CityId": 12772, "CityName": None, "CountryEnglishName": None, "CountryId": 0, "CountryName": None, "CultureInfo": "en-US", "CurrencyCode": None, "CurrentDate": "2019-11-24T11:55:54.4899738+07:00", "DefaultChildAge": 8, "FamilyMode": False, "FinalPriceView": 0, "FlightSearchCriteria": None, "HasFilter": False, "HashId": None, "IsAllowYesterdaySearch": False, "IsApsPeek": False, "IsComparisonMode": False, "IsCriteriaDatesChanged": False, "IsDateless": False, "IsEnableAPS": False, "IsPollDmc": False, "IsRetina": False, "IsShowMobileAppPrice": False, "IsWysiwyp": False, "LandingParameters": {"HeaderBannerUrl": None, "FooterBannerUrl": None, "SelectedHotelId": 0, "LandingCityId": 0}, "Latitude": 0, "LengthOfStay": 1, "Longitude": 0, "MapType": 0, "MaxPollTimes": 0, "NewSSRSearchType": 0, "NumberOfBedrooms": [], "ObjectID": 0, "ObjectName": "", "PackageToken": None, "PageNumber": i, "PageSize": 20, "PlatformID": 1001, "PointsMaxProgramId": 0, "PollTimes": 0, "PreviewRoomFinalPrice": None, "ProductType": -1, "Radius": 0, "RateplanIDs": None, "RectangleSearchParams": None, "ReferrerUrl": None, "RequestPriceView": None, "RequestedDataStatus": 1, "Rooms": 1, "SearchID": 991111124115554400, "SearchMessageID": "6f3a43e2-91fb-4695-a145-e74656c0af3a", "SearchResultCacheKey": "9d246704-488a-4786-a939-f7126202f547", "SearchType": 1, "SelectedColumnTypes": {"ProductType": [-1]}, "SelectedHotelId": 0, "ShouldHideSoldOutProperty": False, "ShouldShowHomesFirst": False, "SortField": 0, "SortOrder": 1, "Tag": None, "Text": "", "TotalHotels": 0, "TotalHotelsFormatted": "0", "TravellerType": 1, "UnavailableHotelId": 0, "ccallout": False, "defdate": False, "isAgMse": False}

            r = requests.post(url, data = request_payload, headers=headers)
            d = json.loads(r.text)

            results = d["ResultList"]


            for j in range(len(results)):
                id_list.append(results[j]["HotelID"])
                name_list.append(results[j]["EnglishHotelName"])
                price_list.append(results[j]["DisplayPrice"])
                score_list.append(results[j]["ReviewScore"])
                review_num_list.append(results[j]["NumberOfReview"])
                url_list.append('https://agoda.com' + results[j]["HotelUrl"])
                lat_lng_list.append((results[j]["Latitude"], results[j]["Longitude"]))
            time.sleep(60)

        return id_list, name_list, price_list, score_list, review_num_list, url_list, lat_lng_list

    
    def get_agoda_basic_info_df(self, url, headers, start, end):
        
        agoda_results = self.get_agoda_info(url, headers, start, end)
        id_agoda = agoda_results[0]
        names_agoda = agoda_results[1]
        price_agoda = agoda_results[2]
        score_agoda = agoda_results[3]
        review_agoda = agoda_results[4]
        url_agoda = agoda_results[5]
        lat_lng_agoda = agoda_results[6]
        
        agoda_info_list = [id_agoda, names_agoda, price_agoda, score_agoda, review_agoda, url_agoda]
        agoda_info_df_temp = pd.DataFrame(agoda_info_list)
        agoda_info_df = pd.DataFrame(agoda_info_df_temp.values.T, columns = ['hotel_id','hotel_name','price_per_night','rating','review_num', 'url'])

        agoda_addr_df_temp = pd.DataFrame([id_agoda, lat_lng_agoda])
        agoda_addr_0 = pd.DataFrame(agoda_addr_df_temp.values.T, columns = ['hotel_id', 'lat_lng'])
        
        return agoda_info_df, agoda_addr_0
        
    
#forth class: deploy google maps api using packages
class GoogleMaps(object):

    def __init__(self):

        self._GOOGLE_MAPS_KEY = "AIzaSyAK99pIbBZx-5sQOWBfhIKg0qTf1HomAtA"
        self._Google_Places = GooglePlaces(self._GOOGLE_MAPS_KEY)
        self._Google_Geocod = googlemaps.Client(key=self._GOOGLE_MAPS_KEY)

    def _reverse_geocode(self, lat, lng, language = None):

        list_reverse_geocode_result = self._Google_Geocod.reverse_geocode((lat, lng), language = language)
        return list_reverse_geocode_result

    def _return_reverse_geocode_info(self, lat, lng, language = None):

        list_reverse_geocode = self._reverse_geocode(lat, lng, language = language)
        if list_reverse_geocode:
            formatted_address = list_reverse_geocode[0]['formatted_address']
            
            return formatted_address
        else:
            
            return None


#fifth class: 
class diff_ways_get_data(object):
    
    def __init__(self):
        
        self.x_1 = airbnb_scrapy()
        self.x_2 = data_processing()
        self.x_3 = agoda_scrapy()
        self.x_4 = GoogleMaps()
        
    def grab_data_by_scraping_and_api_requests(self, url_airbnb, url_agoda, headers, start, end):
#airbnb               
        df1 = self.x_1.get_one_page_data(url_airbnb)
        df_airbnb_addr_1 = pd.DataFrame(self.x_1.get_id_lat_lng_1(url_airbnb))
        
        for i in range(20):
            url_airbnb = self.x_1.get_next_page_url(url_airbnb)
            df2 = self.x_1.get_one_page_data(url_airbnb)
            df1 = pd.concat([df1, df2], axis = 0)
            df_airbnb_addr_2 = pd.DataFrame(self.x_1.get_id_lat_lng_other(url_airbnb))
            df_airbnb_addr_1 = pd.concat([df_airbnb_addr_1, df_airbnb_addr_2], axis = 0)
        
        df1.reset_index(drop = True, inplace = True)
        df_airbnb_addr_1.reset_index(drop = True, inplace = True)
        df_airbnb_addr_1.columns = ['house_id', 'lat_lng']
        
        airbnb_basic_info = self.x_2.drop_duplicate_house(df1)
        airbnb_basic_info = self.x_2.delete_mistaken_id(airbnb_basic_info)
        airbnb_addr = self.x_2.drop_duplicate_house(df_airbnb_addr_1)
#agoda        
        agoda_data_sets = self.x_3.get_agoda_basic_info_df(url_agoda, headers, start, end)
        agoda_info_df = agoda_data_sets[0]
        agoda_basic_info = self.x_2.drop_duplicate_house(agoda_info_df)
        agoda_addr = self.x_2.drop_duplicate_house(agoda_data_sets[1])
#using google maps    
        address_list_1 = []
        for i in range(len(airbnb_addr.iloc[:,1])):
            address = self.x_4._return_reverse_geocode_info(airbnb_addr.iloc[i,1][0], airbnb_addr.iloc[i,1][1], 'en')
            address_list_1.append(address)
        
        address_list_2 = []
        for i in range(len(agoda_addr.iloc[:,1])):
            address = self.x_4._return_reverse_geocode_info(agoda_addr.iloc[i,1][0], agoda_addr.iloc[i,1][1], 'en')
            address_list_2.append(address)
    
        airbnb_addr_f = pd.concat([airbnb_addr, pd.DataFrame(address_list_1)], axis = 1)
        airbnb_addr_f.columns = ['house_id', 'lat_lng', 'address']
        agoda_addr_f = pd.concat([agoda_addr, pd.DataFrame(address_list_2)], axis = 1)
        agoda_addr_f.columns = ['hotel_id', 'lat_lng', 'address']
    
        airbnb_basic_info.to_csv("airbnb_basic_info.csv")
        airbnb_addr_f.to_csv("airbnb_addr.csv")
        agoda_basic_info.to_csv("agoda_basic_info.csv")
        agoda_addr_f.to_csv("agoda_addr.csv")
        
        return airbnb_basic_info, agoda_basic_info, airbnb_addr_f, agoda_addr_f

        
    def grab_data_from_downloaded_raw_files(self):
        
        airbnb_basic_info = pd.read_csv("airbnb_basic_info.csv", index_col = 0)
        airbnb_addr_f = pd.read_csv("airbnb_addr.csv", index_col = 0)
        agoda_basic_info = pd.read_csv("agoda_basic_info.csv", index_col = 0)
        agoda_addr_f = pd.read_csv("agoda_addr.csv", index_col = 0)
        
        return airbnb_basic_info, agoda_basic_info, airbnb_addr_f, agoda_addr_f

    def grab_subset_of_data_to_test(self, url_airbnb, url_agoda, headers, start, end):
#airbnb        
        df1 = self.x_1.get_one_page_data(url_airbnb)
        df_airbnb_addr_1 = pd.DataFrame(self.x_1.get_id_lat_lng_1(url_airbnb))
        df_airbnb_addr_1.columns = ['house_id', 'lat_lng']
        
        airbnb_basic_info = self.x_2.drop_duplicate_house(df1)
        airbnb_basic_info = self.x_2.delete_mistaken_id(airbnb_basic_info)
        airbnb_addr = self.x_2.drop_duplicate_house(df_airbnb_addr_1)
#agoda
        agoda_data_sets = self.x_3.get_agoda_basic_info_df(url_agoda, headers, start, end)
        agoda_info_df = agoda_data_sets[0]
        agoda_basic_info = self.x_2.drop_duplicate_house(agoda_info_df)
        agoda_addr = self.x_2.drop_duplicate_house(agoda_data_sets[1])
#using google maps
        address_list_1 = []
        for i in range(len(airbnb_addr.iloc[:,1])):
            address = self.x_4._return_reverse_geocode_info(airbnb_addr.iloc[i,1][0], airbnb_addr.iloc[i,1][1], 'en')
            address_list_1.append(address)
        
        address_list_2 = []
        for i in range(len(agoda_addr.iloc[:,1])):
            address = self.x_4._return_reverse_geocode_info(agoda_addr.iloc[i,1][0], agoda_addr.iloc[i,1][1], 'en')
            address_list_2.append(address)
    
        airbnb_addr_f = pd.concat([airbnb_addr, pd.DataFrame(address_list_1)], axis = 1)
        airbnb_addr_f.columns = ['house_id', 'lat_lng', 'address']
        agoda_addr_f = pd.concat([agoda_addr, pd.DataFrame(address_list_2)], axis = 1)
        agoda_addr_f.columns = ['hotel_id', 'lat_lng', 'address']
        
        airbnb_basic_info.to_csv("airbnb_basic_info.csv")
        airbnb_addr_f.to_csv("airbnb_addr.csv")
        agoda_basic_info.to_csv("agoda_basic_info.csv")
        agoda_addr_f.to_csv("agoda_addr.csv")
        
        return airbnb_basic_info, agoda_basic_info, airbnb_addr_f, agoda_addr_f
        

#sixth class: save all the data to Database 
class insert_to_DB(object):
    
    def __init__(self):    
        
        self.conn = sqlite3.connect('house_hotel.db')
        self.cur = self.conn.cursor()
        
    def create_table(self):
        try:
            self.cur.execute('CREATE TABLE agoda(hotel_id INTEGER NOT NULL PRIMARY KEY, name TEXT, price_per_night FLOAT, rating FLOAT, review_num INTEGER, url TEXT)')
        except:
            print('table has already exist!')
        try:
            self.cur.execute('CREATE TABLE airbnb(house_id INTEGER NOT NULL PRIMARY KEY, name TEXT, price_per_night INTEGER, rating FLOAT, review_num INTEGER, url TEXT)')
        except:
            print('table has already exist!')
        try:
            self.cur.execute('CREATE TABLE addrs(hid INTEGER NOT NULL PRIMARY KEY, lat_lng TEXT, address TEXT)')
        except:
            print('table has already exist!')
            
        return
        
    def insert_agoda(self, hid, name, price, rating, review_num, url):
        
        self.cur.execute('SELECT * FROM agoda WHERE (hotel_id = ? AND name = ? AND price_per_night = ? AND rating = ? AND review_num = ? AND url = ?)', (hid, name, price, rating, review_num, url))
        entry = self.cur.fetchone()
    
        if entry is None:
            self.cur.execute('INSERT INTO agoda(hotel_id, name, price_per_night, rating, review_num, url) VALUES (?,?,?,?,?,?)', (hid, name, price, rating, review_num, url))
        else:
            print('Entry found')
            
        self.conn.commit()
    
    def insert_airbnb(self, hid, name, price, rating, review_num, url):
        
        self.cur.execute('SELECT * FROM airbnb WHERE (house_id = ? AND name = ? AND price_per_night = ? AND rating = ? AND review_num = ? AND url = ?)', (hid, name, price, rating, review_num, url))
        entry = self.cur.fetchone()
    
        if entry is None:
            self.cur.execute('INSERT INTO airbnb(house_id, name, price_per_night, rating, review_num, url) VALUES (?,?,?,?,?,?)', (hid, name, price, rating, review_num, url))
        else:
            print('Entry found')
            
        self.conn.commit()
        
    def insert_addrs(self, hid, lat_lng, address):
        
        self.cur.execute('SELECT * FROM addrs WHERE (hid = ? AND lat_lng = ? AND address = ?)', (hid, lat_lng, address))
        entry = self.cur.fetchone()
    
        if entry is None:
            self.cur.execute('INSERT INTO addrs(hid, lat_lng, address) VALUES (?,?,?)', (hid, lat_lng, address))
        else:
            print('Entry found')
            
        self.conn.commit()
        
    def add_info(self, df_1, df_2, df_3, df_4):
        
        for i in range(len(df_1)):
            self.insert_airbnb(int(df_1.iloc[:, 0][i]), df_1.iloc[:, 1][i], int(df_1.iloc[:, 2][i]), float(df_1.iloc[:, 3][i]), int(df_1.iloc[:, 4][i]), df_1.iloc[:, 5][i])
        for i in range(len(df_2)):
            self.insert_agoda(int(df_2.iloc[:, 0][i]), df_2.iloc[:, 1][i], float(df_2.iloc[:, 2][i]), float(df_2.iloc[:, 3][i]), int(df_2.iloc[:, 4][i]), df_2.iloc[:, 5][i])
        for i in range(len(df_3)):
            self.insert_addrs(int(df_3.iloc[:, 0][i]), str(df_3.iloc[:, 1][i]), df_3.iloc[:, 2][i])
        for i in range(len(df_4)):
            self.insert_addrs(int(df_4.iloc[:, 0][i]), str(df_4.iloc[:, 1][i]), df_4.iloc[:, 2][i])
        
        

def main():
    
    url_airbnb = 'https://www.airbnb.com/s/Los-Angeles--CA/homes?refinement_paths%5B%5D=%2Fhomes&current_tab_id=home_tab&selected_tab_id=home_tab&place_id=ChIJE9on3F3HwoAR9AhGJW_fL-I&source=mc_search_bar&search_type=pagination&screen_size=large&s_tag=BlsrbYF3&hide_dates_and_guests_filters=false&checkin=2019-12-25&checkout=2019-12-26&adults=2&last_search_session_id=3daccb0d-c054-4026-a004-d506420dadf7'
    url_agoda = 'https://www.agoda.com/api/en-us/Main/GetSearchResultList'
    headers = {"origin": "https://www.agoda.com", "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"}
    x_5 = diff_ways_get_data()
    
    
    def add_data_to_my_data_model(data1, data2, data3, data4):
        
        x_6 = insert_to_DB()
        x_6.create_table()    
        x_6.add_info(data1, data2, data3, data4)
        
        return
    
    parser = argparse.ArgumentParser()
#    parser.add_argument("-source", choices=["local", "remote", "test"], nargs=1, help="where data should be gotten from")
    parser.add_argument("-s", "--source", choices=["local", "remote", "test"], help="where data should be gotten from")
    args = parser.parse_args()
    
    location = args.source
    
    if location == "local":
        data_sets = x_5.grab_data_from_downloaded_raw_files()
        
    elif location == "remote":
        start = 0
        end = 20
        data_sets = x_5.grab_data_by_scraping_and_api_requests(url_airbnb, url_agoda, headers, start, end)
        
    else:
        start = 1
        end = 2
        data_sets = x_5.grab_subset_of_data_to_test(url_airbnb, url_agoda, headers, start, end)
        
    airbnb_basic_info_1 = data_sets[0]
    agoda_basic_info_1 = data_sets[1]
    airbnb_addr_f_1 = data_sets[2]
    agoda_addr_f_1 = data_sets[3]  
    
#I have cleaned data before I put them in a DataFrame, so the four datasets returned by cmd are already cleaned and are in the form of DataFrame. 
#I have a data_process class.        
    add_data_to_my_data_model(airbnb_basic_info_1, agoda_basic_info_1, airbnb_addr_f_1, agoda_addr_f_1)


        
if __name__ == "__main__":
    main()

    
