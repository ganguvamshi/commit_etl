#!/usr/bin/env python

import os
import sys
import pandas as pd
from sql import CommitsDB
from pandas.api.types import CategoricalDtype
import seaborn as sns
import matplotlib.pyplot as plt



def find_top_commiters(rec_df,top_n=5):
    repo_count = rec_df.groupby(['committer_name','commit_repo']).apply(lambda x: len(x['commit_id'])).rename('user_repo_count').reset_index()
    user_count = rec_df.groupby(['committer_name']).apply(lambda x: len(x['commit_id'])).rename('user_commit_count').reset_index()
    commit_counts  = repo_count.set_index('committer_name').join(user_count.set_index('committer_name'))
    commit_counts['total_counts'] = commit_counts['user_repo_count'] + commit_counts['user_commit_count']
    commit_counts = commit_counts.sort_values(['total_counts', 'committer_name'], ascending=[False, True])
    top_rec = commit_counts.groupby(['committer_name']).first().sort_values('total_counts', ascending=False)
    top_rec['user_rank'] = top_rec['total_counts'].rank(ascending=False).tolist()
    commits_counts = commit_counts.join(top_rec[['user_rank']]).sort_values(by='user_rank', ascending=True)
    top5 = commits_counts[commits_counts.user_rank<=top_n].drop(columns=['total_counts'])
    return top5


def cal_duration(user_df):
    duration = (max(user_df['committer_date']) - min(user_df['committer_date'])) #.total_seconds()/(60)
    return duration


def find_longest_streak_commiter(df):
    res = df.groupby(['committer_name', 'commit_repo']).apply(lambda x: cal_duration(x)).rename('streak_duration').reset_index()
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
    # test the connectoon
    dbobj.test_conn()
    
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
    plt_name = "heatmap_plot.png"
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_counts, cmap='coolwarm', square=True, 
                annot=True, fmt=',.0f', annot_kws={'size': 'small', 'alpha': 0.4})
    plt.savefig(plt_name)
    plt.close()   
    print(f"heatmap plot is saved to {plt_name}")