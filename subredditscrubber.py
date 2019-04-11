#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This code was written for /r/piracy
Written by /u/Redbiertje
Reviewed and tweaked by /u/dbzer0
24 March 2019
"""

#Imports
import botData as bd #Import for login data, obviously not included in this file. Put it in a file called botData.py in the same folder.
import datetime
import praw
import time
from psaw import PushshiftAPI


#Define proper starting variables
testing_mode = True # Change this to False to do the dirty.
remove_comments = True # Also remove comments or just the posts
submission_count = 1 #Don't touch.

#Login
r = praw.Reddit(client_id=bd.app_id, client_secret=bd.app_secret, password=bd.password,user_agent=bd.app_user_agent, username=bd.username)
if(r.user.me()=="scrubber"): #Or whatever username your privileged account has
    print("Successfully logged in")
api = PushshiftAPI(r)

deadline = int(datetime.datetime(2018, 9, 24).timestamp()) # Change accordingly to the period you want to start the scrub
#deadline = 1472771669 # In case you want to stop the script and restart later, copy the latest epoch from the stdout and increase it by one here.

try:
    while submission_count > 0: #Check if we're still doing useful things
        #Obtain new posts
        submissions = list(api.search_submissions(before=deadline,subreddit='piracy',filter=['url','author','title','subreddit'],limit=10))
        #Count how many posts we've got
        submission_count = len(submissions)

        #Iterate over posts
        for sub in submissions:
            #Obtain data from post
            deadline = int(sub.created_utc)
            sub_id = sub.id
            
            #Better formatting to post the sub title before the comments
            sub_title = sub.title
            if len(sub_title) > 40:
                sub_title = sub_title[:40]+"..."
            print(f"[{sub_id}] Removing submission from {datetime.datetime.fromtimestamp(deadline)} [{deadline}]: {sub_title}")

            #Iterate over comments if required
            if remove_comments:
                #Obtain comments
                sub.comments.replace_more(limit=None)
                comments = sub.comments.list()
                #Remove comments
                print(f'-[{sub_id}] Found {len(comments)} comments to delete')
                for comment in comments:
                    comment_body = comment.body.replace("\n", "")
                    if len(comment_body) > 50:
                        comment_body = "{}...".format(comment_body[:50])
                    print("--[{}] Removing comment: {}".format(sub_id, comment_body))
                    delRetry = True
                    delIter = 1
                    while delRetry:
                        try:
                            if not testing_mode: comment.mod.remove()
                            delRetry = False
                        except: 
                            print(f'[Error] Service unavailable while trying to delete comment. Retry No #{delIter}')
                            delIter += 1
                            time.sleep(5)
                            continue

            #Remove post
            if not testing_mode: sub.mod.remove()
                
except KeyboardInterrupt:
    print("Stopping due to impatient human.")
