# Youtube API project
# github.com/SciWilro
# Takes channel url/name/Id and gets information for all videos
# Stores it in a pandas Datafame
# Next step is to store on cloud (AWS micro-instance)

# Get Youtube API key: https://www.slickremix.com/docs/get-api-key-for-youtube/
# Set up micro-instance uswing AWS - Amazon Relational Database Service (RDS) PostgreSQL database

# Import Libraries
import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# ---------------------------------------- #
# Building Stage - To be removed
    # I used http://jsonviewer.stack.hu/ to view json data
    # And then just made this function to view in VSCode - Please suggest better solution if possible
import json # To export json objects
def export_json(filename: str, json_response: json):
    with open( str("example_responses/" + filename), "w") as f:
        f.write(str(json_response))
# export_json("test.json", response)
# ---------------------------------------- #


# Load environment variables (API key) from .env - access using os.environ() or os.getenv()
def configure():
    load_dotenv()

# Function to get video details
def get_video_details(video_id: str, api_key: str):

    url_vid= f"https://youtube.googleapis.com/youtube/v3/videos?id={video_id}&part=statistics&key={api_key}"
    response_vid = requests.get(url_vid).json()

    for item in response_vid['items']:
        vid_views = item['statistics']['viewCount']
        vid_likes = item['statistics']['likeCount']
        vid_comments = item['statistics']['commentCount']

    return (vid_views, vid_likes, vid_comments)

def get_channel_videos(df: pd.DataFrame, api_key: str, channel_id: str, pageToken = None) -> pd.DataFrame:
    # Good pythonic convention for default values.
    if pageToken == None:
        pageToken = ''
    
    # While loop to handle multiple pages in response
    while True:
        url= f"https://youtube.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1000{pageToken}"
        response = requests.get(url).json()
        
        time.sleep(1) # Wait for response - Just to be safe - for loop might start too soon

        # Loop through all of the items in response, store values as vars, and append to df
        for item in response['items']:
            if item['id']['kind'] == "youtube#video":
                video_id = item['id']['videoId']
                # Cleaned Title and Description
                video_title = str(item['snippet']['title']).replace("&amp;","&").replace("&#39;","'")
                video_description = item['snippet']['description']
                # Publish Date and Time
                video_date = str(item['snippet']['publishTime']).split("T")[0]
                video_time = str(item['snippet']['publishTime'])[11:16]
                # Call API for each video using get_video_details()
                vid_views, vid_likes, vid_comments = get_video_details(video_id, api_key)

                # Add to pandas.Dataframe object - .append() replaced with pandas.concat()
                df = pd.concat( [df, pd.DataFrame( {"video_id": video_id, "video_title": video_title, "video_description": video_description, "video_date": video_date, "video_time": video_time, "vid_views": vid_views, "vid_likes": vid_likes, "vid_comments": vid_comments}, index = [len(df)] ) ], axis = 0)

        # Run check for multiple pages - otherwise break out of while loop and return new df
        # If 'nextPageToken' field does not exist we will get KeyError
        try:
            if response['nextPageToken'] != None:
                print("___________________________")
                print("'nextpageToken' found - Proceeding to next request")
                print("___________________________")
                pageToken = f"&pageToken={response['nextPageToken']}"
        except KeyError:
            print("___________________________")
            print("'nextpageToken' does not exist - Last page reached")
            print("___________________________")
            break

    return df



def main():
    configure()
    api_key = os.getenv('API_KEY')
    
    # TODO get_channel_id(channel_url)
    channel_id = 'UCpeGBKn0axOJAcPHkcPiXcg' # SGU
    channel_id = 'UC4yOXRDrOFYfeiTZAeJdcZw' # Empty Channel for debugging
    # channel_id = 'UCywjuI3tf_eA2I3NHPndGEg'

    # Making pandas dataframe
    df = pd.DataFrame(columns=["video_id", "video_title", "video_description", "video_date", "video_time", "vid_views", "vid_likes", "vid_comments"])
    # Call get_channel_videos(), which also calls get_video_details and appends to the df
    df = get_channel_videos(df, api_key, channel_id)
    











    +



main()



# !----! #
#  TODO
# !----! #


def get_channel_id(channel_url: str) -> str:
    '''Get Channel Id from url
    Some channels have unique names that dont include channel ID - For this we need to scrape html data for channel page
    Args:
        url (str): Channel url
    Returns:
        channel_id (str): Unique channel id used for API calls
    '''
    # TODO check url for '/c/' or '/channel/'
    # TODO If '/c/' in url we need to scrape
    # TODO Look for 'externalId' in page source
    # TODO If '/channel/' in url just take last part of url

    # E.g. https://www.youtube.com/c/TheSkepticsGuide -> "externalId":"UCpeGBKn0axOJAcPHkcPiXcg"
    # E.g. https://www.youtube.com/channel/UCywjuI3tf_eA2I3NHPndGEg -> "UCywjuI3tf_eA2I3NHPndGEg"
    channel_id = ''
    return channel_id

# def get_video_comments():
#     see https://github.com/hellotinah/youtube_sentiment_analysis/blob/main/cleaned_get_youtube_comments.py
#     return data

# -------------------------------------------------------- #
# Sources
# # Based on https://www.youtube.com/watch?v=fklHBWow8vE
# -------------------------------------------------------- #


# DEBUGGING
# video_id="VkL-HtJDpSA"


# df = pd.DataFrame(columns=["video_id", "video_title", "video_description", "video_date", "video_time", "vid_views", "vid_likes", "vid_comments"])
# video_id = "a"
# video_title = "a"
# video_description = "a"
# video_date = "a"
# video_time = "a"
# vid_views = "a"
# vid_likes = "a"
# vid_comments = "a"

# type({"video_id": video_id, "video_title": video_title, "video_description": video_description, "video_date": video_date, "video_time": video_time, "vid_views": vid_views, "vid_likes": vid_likes, "vid_comments": vid_comments})
# test_dic = {"video_id": video_id, "video_title": video_title, "video_description": video_description, "video_date": video_date, "video_time": video_time, "vid_views": vid_views, "vid_likes": vid_likes, "vid_comments": vid_comments}
# pd.DataFrame(test_dic, index = [0])
# test = pd.DataFrame({"video_id": video_id, "video_title": video_title, "video_description": video_description, "video_date": video_date, "video_time": video_time, "vid_views": vid_views, "vid_likes": vid_likes, "vid_comments": vid_comments}, index=0)


# df = df.append({"video_id": video_id, "video_title": video_title, "video_description": video_description, "video_date": video_date, "video_time": video_time, "vid_views": vid_views, "vid_likes": vid_likes, "vid_comments": vid_comments}, ignore_index=True)
# df = pd.concat( [df, pd.DataFrame({"video_id": [video_id], "video_title": [video_title], "video_description": [video_description], "video_date": [video_date], "video_time": [video_time], "vid_views": [vid_views], "vid_likes": [vid_likes], "vid_comments": [vid_comments]})], axis = 0)
# df = pd.concat( [df, pd.DataFrame( {"video_id": video_id, "video_title": video_title, "video_description": video_description, "video_date": video_date, "video_time": video_time, "vid_views": vid_views, "vid_likes": vid_likes, "vid_comments": vid_comments}, index = [len(df)] ) ], axis = 0)
