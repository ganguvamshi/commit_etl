#!/usr/bin/env python

import os
import sys
import pandas as pd
from sql import CommitsDB
from pandas.api.types import CategoricalDtype
import seaborn as sns
import matplotlib.pyplot as plt



def find_top_commiters(rec_df):
    top5 = rec_df.groupby(['committer_name']).apply(lambda x: len(x['commit_id'])).rename("num_counts").reset_index()
    top5 = top5.sort_values(by='num_counts', ascending=False).head(5).reset_index(drop=True)
    return top5


def cal_duration(user_df):
    duration = (max(user_df['committer_date']) - min(user_df['committer_date'])) #.total_seconds()/(60)
    return duration


def find_longest_streak_commiter(df):
    res = df.groupby(['committer_name']).apply(lambda x: cal_duration(x)).rename('streak_duration').reset_index()
    res = res.sort_values(by='streak_duration', ascending=False).head(1)
    return res


def calculate_heatmap(df):
    """
    a view called commits_extended is created in database which calculate the day and the hour_block automatically.
    """
    commit_counts = df.groupby(['day','hour_block'])['commit_id'].count().rename('num_commits').reset_index()
    # create categoricalDtypes for Day and hour_block to retain the order
    day_order = CategoricalDtype(['MON','TUE','WED','THU','FRI','SAT','SUN'], ordered=True)
    hour_block_order = CategoricalDtype(['00-03','03-06','06-09','09-12','12-15','15-18','18-21','21-00'], ordered=True)
    commit_counts['day'] = commit_counts['day'].astype(day_order)
    commit_counts['hour_block'] = commit_counts['hour_block'].astype(hour_block_order)
    commit_counts = commit_counts.sort_values(['day','hour_block'])
    # convert the dataframe to wide format that is aligned with the required output
    res = pd.pivot(commit_counts, index=['day'], columns = 'hour_block',values = 'num_commits') 
    return res


if __name__=="__main__":
    # create the sql object for github db 
    dbobj  = CommitsDB()
    
    # get all information from commits table 
    query = "SELECT * FROM commits_extended;"
    commits_df = dbobj.read_query(query)

    # question 1: determine the top 5 committers ranked by count of commits and their number of commits.
    top_commiters = find_top_commiters(commits_df)
    print(f"Top 5 Commiters \n {top_commiters} \n")
    # question 2: determine the committer with the longest commit streak.
    long_streak_commiter = find_longest_streak_commiter(commits_df)
    print(f"Commiter with longest streak: \n {long_streak_commiter}\n")

    # question 3: generate a heatmap of number of commits count by all users by day of the week and by 3 hour blocks.
    heatmap_counts = calculate_heatmap(commits_df)
    print(f"count heatmap by Day and Hour Block:\n {heatmap_counts} \n")
    # plotting heatmap and saving it to file called heatmap_plot.png
    sns.set(style="darkgrid")
    sns.heatmap(heatmap_counts, cmap="YlGnBu", annot=True)
    plt_name = "heatmap_plot.png"
    plt.savefig(plt_name)
    print(f"heatmap plot is saved to {plt_name}")