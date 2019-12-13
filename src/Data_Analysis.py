#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 03:54:14 2019

@author: yvettehhhuang96
"""

from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class data_analysis(object):
    
#open the local files
    def import_csv(self):

        f1 = pd.read_csv('agoda_basic_info.csv', index_col = 0)
        f2 = pd.read_csv('airbnb_basic_info.csv', index_col = 0)
        f3 = pd.read_csv('agoda_addr.csv', index_col = 0)
        f4 = pd.read_csv('airbnb_addr.csv', index_col = 0)

        return f1, f2, f3, f4
    
#get train_X for kmeans    
    def get_kmeans_X(self, df):
        
        attr_1 = []
        attr_2 = []
        mark_del = None
        for i in range(len(df)):
            a = eval(df.iloc[:, 1][i])[0]
            b = eval(df.iloc[:, 1][i])[1]
            attr_1.append(a)
            attr_2.append(b)

            attr_df = pd.concat([pd.DataFrame(attr_1), pd.DataFrame(attr_2)], axis = 1)
            attr_df.columns = range(2)
            mean_lat_agoda = np.mean(attr_df.iloc[:,0])
            mean_lng_agoda = np.mean(attr_df.iloc[:,1])

            for i in range(len(attr_df)):
                attr_df.iloc[:,0][i] = (attr_df.iloc[:,0][i] - mean_lat_agoda)*100
                attr_df.iloc[:,1][i] = (attr_df.iloc[:,1][i] - mean_lng_agoda)*10

            for i in range(len(attr_df)):
                if attr_df.iloc[:,0][i] > 1000 or attr_df.iloc[:,1][i] > 1000:
                    attr_df.drop([i], inplace = True)
                    mark_del = i

        return attr_df, mark_del
    
#hotel and house distribution scatter plot   
    def hotel_house_distribution(self, f3, f4):
        
        lat_lng_agoda = self.get_kmeans_X(f3)[0]
        lat_lng_airbnb = self.get_kmeans_X(f4)[0]
        
        if self.get_kmeans_X(f3)[1] != None:
            f3.drop([self.get_kmeans_X(f3)[1]], inplace = True)
        f3.reset_index(drop = True, inplace = True)
        if self.get_kmeans_X(f4)[1] != None:
            f4.drop([self.get_kmeans_X(f4)[1]], inplace = True)
        f4.reset_index(drop = True, inplace = True)
    
        plt.figure()
        plt.scatter(list(lat_lng_agoda.iloc[:,0]), list(lat_lng_agoda.iloc[:,1]), c = 'red')
        plt.scatter(list(lat_lng_airbnb.iloc[:,0]), list(lat_lng_airbnb.iloc[:,1]), c = 'blue')
        plt.title('hotel/house distribution')
        plt.xlabel('latitude')
        plt.ylabel('longitude')
        plt.show()
        
        return lat_lng_agoda, lat_lng_airbnb
    
#kmeans display
    def kmeans_scatter(self, lat_lng_agoda, lat_lng_airbnb, f3, f4):
        
        all_points = pd.concat([lat_lng_agoda, lat_lng_airbnb], axis = 0)
        all_points.reset_index(drop = True, inplace = True)
        
        kmeans = KMeans(n_clusters= 3, random_state=0).fit(all_points)
        points_with_label = pd.concat([all_points, pd.DataFrame(kmeans.labels_)], axis = 1)
        points_with_label.columns = ['lat', 'lng', 'label']
        
        new_f3 = pd.concat([f3, pd.DataFrame(kmeans.labels_[:315])], axis = 1)
        new_f4 = pd.concat([f4, pd.DataFrame(kmeans.labels_[315:])], axis = 1)
        
        clstr_1 = []
        clstr_2 = []
        clstr_3 = []

        for i in range(len(list(points_with_label.label))):
            if list(points_with_label.label)[i] == 0:
                clstr_1.append(list(points_with_label.iloc[i,:]))
            elif list(points_with_label.label)[i] == 1:
                clstr_2.append(list(points_with_label.iloc[i,:]))
            else:
                clstr_3.append(list(points_with_label.iloc[i,:]))
        
        clstr_1 = pd.DataFrame(clstr_1)
        clstr_2 = pd.DataFrame(clstr_2)
        clstr_3 = pd.DataFrame(clstr_3)
        
        plt.figure()
        plt.scatter(list(clstr_1.iloc[:,0]), list(clstr_1.iloc[:,1]), c = 'red', s=4)
        plt.scatter(list(clstr_2.iloc[:,0]), list(clstr_2.iloc[:,1]), c = 'blue', s=4)
        plt.scatter(list(clstr_3.iloc[:,0]), list(clstr_3.iloc[:,1]), c = 'yellow', s=4)
        plt.title('hotel/house distribution_kmeans')
        plt.xlabel('latitude')
        plt.ylabel('longitude')
        plt.show()
        
        return new_f3, new_f4

#how to transit price, rating and review_num:
#The prices are absolute values, we do not need to process them.
#The rating domains of agoda and airbnb are different, so new agoda rating is devided by 2. 
#The bases of review_num of agoda and airbnb are different, so the data need normalization.

    def original_plots(self, f1, f2, new_f3, new_f4):
        
        agoda_all = pd.merge(f1, new_f3, how='outer', on='hotel_id')
        agoda_all.dropna(axis=0,how='any', inplace = True)
        agoda_all.reset_index(drop = True, inplace = True)
        agoda_all = agoda_all.iloc[:200, :]
        
        for i in range(len(agoda_all.iloc[:,3])):
            agoda_all.iloc[i,3] = agoda_all.iloc[i,3]/2

        sum_review_num_agoda = sum(agoda_all.iloc[:,4])
        for i in range(len(agoda_all.iloc[:,4])):
            agoda_all.iloc[i,4] = agoda_all.iloc[i,4]/sum_review_num_agoda

        platform_1 = ['ago']*200
        agoda_all_1 = pd.concat([agoda_all, pd.DataFrame(platform_1)], axis = 1)
        agoda_all_1.columns = ['id', 'name', 'price_per_night', 'rating', 'review_num', 'url', 'lat_lng', 'address', 'clstr', 'plf']
        
        airbnb_all = pd.merge(f2, new_f4, how='outer', on='house_id')
        airbnb_all.dropna(axis=0,how='any', inplace = True)
        airbnb_all.reset_index(drop = True, inplace = True)

        airbnb_all = airbnb_all.iloc[:200, :]

        sum_review_num_airbnb = sum(airbnb_all.iloc[:,4])
        for i in range(len(airbnb_all.iloc[:,4])):
            airbnb_all.iloc[i,4] = airbnb_all.iloc[i,4]/sum_review_num_airbnb
            
        platform_2 = ['air']*200
        airbnb_all_1 = pd.concat([airbnb_all, pd.DataFrame(platform_2)], axis = 1)
        airbnb_all_1.columns = ['id', 'name', 'price_per_night', 'rating', 'review_num', 'url', 'lat_lng', 'address', 'clstr', 'plf']

        fig = plt.figure(figsize=(10, 20))
        ax1 = fig.add_subplot(321)
        ax2 = fig.add_subplot(322)
        ax3 = fig.add_subplot(323)
        ax4 = fig.add_subplot(324)
        ax5 = fig.add_subplot(325)
        ax6 = fig.add_subplot(326)

        ax1.boxplot(list(agoda_all_1.iloc[:,2]), medianprops={'color':'red'},boxprops=dict(color='red'), whiskerprops = {'color': 'red'},capprops = {'color': 'red'},flierprops={'color':'red','markeredgecolor':'red'})
        ax2.boxplot(list(airbnb_all_1.iloc[:,2]), medianprops={'color':'blue'},boxprops=dict(color='blue'), whiskerprops = {'color': 'blue'},capprops = {'color': 'blue'},flierprops={'color':'blue','markeredgecolor':'blue'})
        ax1.set_xlabel('price per night: agoda')
        ax2.set_xlabel('price per night: airbnb')
        
        ax3.boxplot(list(agoda_all_1.iloc[:,3]), medianprops={'color':'red'},boxprops=dict(color='red'), whiskerprops = {'color': 'red'},capprops = {'color': 'red'},flierprops={'color':'red','markeredgecolor':'red'})
        ax4.boxplot(list(airbnb_all_1.iloc[:,3]), medianprops={'color':'blue'},boxprops=dict(color='blue'), whiskerprops = {'color': 'blue'},capprops = {'color': 'blue'},flierprops={'color':'blue','markeredgecolor':'blue'}) 
        ax3.set_xlabel('rating: agoda')
        ax4.set_xlabel('rating: airbnb')
        
        ax5.boxplot(list(agoda_all_1.iloc[:,4]), medianprops={'color':'red'},boxprops=dict(color='red'), whiskerprops = {'color': 'red'},capprops = {'color': 'red'},flierprops={'color':'red','markeredgecolor':'red'})
        ax6.boxplot(list(airbnb_all_1.iloc[:,4]), medianprops={'color':'blue'},boxprops=dict(color='blue'), whiskerprops = {'color': 'blue'},capprops = {'color': 'blue'},flierprops={'color':'blue','markeredgecolor':'blue'}) 
        ax5.set_xlabel('review_num: agoda')
        ax6.set_xlabel('review_num: airbnb')
        
        plt.show()
        
        return agoda_all_1, airbnb_all_1
    
#get final score of each house/hotel
    def get_final_score(self, agoda_all_1, airbnb_all_1):
        
        ago_air_concat = pd.concat([agoda_all_1, airbnb_all_1], axis = 0)
        ago_air_concat_price = ago_air_concat.sort_values(by = 'price_per_night', ascending = False)
        ago_air_concat_price.reset_index(drop = True, inplace = True)
        
        score = []
        for i in range(400):
            score.append(i)

        ago_air_concat_price_1 = pd.concat([ago_air_concat_price,pd.DataFrame(score)], axis = 1)
        ago_air_concat_price_1.columns = ['id', 'name', 'price_per_night', 'rating', 'review_num', 'url', 'lat_lng', 'address', 'clstr', 'plf', 'score']

        ago_air_concat_rating = ago_air_concat_price_1.sort_values(by = 'rating')
        ago_air_concat_rating.reset_index(drop = True, inplace = True)
        for i in range(400):
            ago_air_concat_rating.iloc[i,10] += i

        ago_air_concat_review = ago_air_concat_rating.sort_values(by = 'review_num')
        ago_air_concat_review.reset_index(drop = True, inplace = True)
        for i in range(400):
            ago_air_concat_review.iloc[i, 10] += i

        ago_air_concat_score = ago_air_concat_review.sort_values(by = 'score')
        ago_air_concat_score.reset_index(drop = True, inplace = True)

        clstr_1_ago = []
        clstr_1_air = []
        clstr_2_ago = []
        clstr_2_air = []
        clstr_3_ago = []
        clstr_3_air = []
        for i in range(400):
            if ago_air_concat_score.iloc[i,8] == 0 and ago_air_concat_score.iloc[i,9] == 'ago':
                clstr_1_ago.append(ago_air_concat_score.iloc[i,10])
            elif ago_air_concat_score.iloc[i,8] == 0 and ago_air_concat_score.iloc[i,9] == 'air':
                clstr_1_air.append(ago_air_concat_score.iloc[i,10])
            elif ago_air_concat_score.iloc[i,8] == 1 and ago_air_concat_score.iloc[i,9] == 'ago':
                clstr_2_ago.append(ago_air_concat_score.iloc[i,10])
            elif ago_air_concat_score.iloc[i,8] == 1 and ago_air_concat_score.iloc[i,9] == 'air':
                clstr_2_air.append(ago_air_concat_score.iloc[i,10])
            elif ago_air_concat_score.iloc[i,8] == 2 and ago_air_concat_score.iloc[i,9] == 'ago':
                clstr_3_ago.append(ago_air_concat_score.iloc[i,10])
            else:
                clstr_3_air.append(ago_air_concat_score.iloc[i,10])

        mean_1_ago = np.mean(clstr_1_ago)
        mean_1_air = np.mean(clstr_1_air)
        mean_2_ago = np.mean(clstr_2_ago)
        mean_2_air = np.mean(clstr_2_air)
        mean_3_ago = np.mean(clstr_3_ago)
        mean_3_air = np.mean(clstr_3_air)

        return mean_1_ago, mean_1_air, mean_2_ago, mean_2_air, mean_3_ago, mean_3_air, ago_air_concat_score

