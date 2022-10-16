# Seperate for now, while I work out how to do this 😁

import psycopg2 as ps
import pandas as pd
from dotenv import load_dotenv
import os

# ------------------------- #
# Set up env variables from `.env` file
def configure():
    '''_summary_
    Setup to Load environment variables (API key) from `.env`
    Access using `os.environ()` or `os.getenv()`
    '''
    load_dotenv()


# ------------------------- #
# Connect to DB
# https://simplebackups.com/blog/allow-a-remote-ip-to-connect-to-your-amazon-rds-mysql-instance/
# Also note that database name is not the same as database instance name that you see on RDS Dashboard
def connect_to_db(hostname: str, dbname: str, username: str, password: str, port: str):
    try:
        conn = ps.connect(host=hostname, dbname=dbname, user=username, password=password, port=port)
    except ps.OperationalError as e:
        raise e
    else:
        print("Connected Successfully")
    return conn

def create_table(curr):
    create_table_command = ("""CREATE TABLE IF NOT EXISTS videos (
        video_id VARCHAR(255) PRIMARY KEY,
        video_title TEXT NOT NULL,
        video_description TEXT NOT NULL,
        video_date DATE NOT NULL DEFAULT CURRENT_DATE,
        video_time TEXT NOT NULL,
        vid_views INTEGER NOT NULL,
        vid_likes INTEGER NOT NULL,
        vid_comments INTEGER NOT NULL
        )""")
    curr.execute(create_table_command)

#### ! I AM HERE

#video_id = "kP8q62r6ZYs" # Old vid
#video_id = "8YvsTU_eXGE" # Latest vid
def check_if_video_exists(curr, video_id):
    query = ("""SELECT video_id FROM VIDEOS WHERE video_id = %s""")
    curr.execute(query, (video_id,))
    # Return if row was found
    return curr.fetchone() is not None

def update_row(curr, video_id, video_title, vid_views, vid_likes, vid_comments):
    query = ("""UPDATE videos
            SET video_title = %s,
                vid_views = %s,
                vid_likes = %s,
                vid_comments = %s
            WHERE video_id = %s;""")

    vars_to_update = (video_title, vid_views, vid_likes, vid_comments, video_id)
    curr.execute(query, vars_to_update)


def update_db(curr, df) -> pd.DataFrame:
    tmp_df = pd.DataFrame(columns=["video_id", "video_title", "video_description", "video_date", "video_time", "vid_views", "vid_likes", "vid_comments"])

    for i, row in df.iterrows():
        if check_if_video_exists(curr, row['video_id']): # If vid exists in db, we will update row data
            update_row(curr, row['video_id'], row['video_title'], row['vid_views'], row['vid_likes'], row['vid_comments']) # update command
        else: # If video doesnt exist in db we will append row to db
            # Add row to temp df so that we can insert all of them at same time
            tmp_df = tmp_df.append(row)
    
    return tmp_df

# INSERT command
def insert_into_table(curr, video_id, video_title, video_description, video_date, video_time, vid_views, vid_likes, vid_comments):
    insert_into_videos = ("""INSERT INTO videos (video_id, video_title, video_description, video_date, video_time, vid_views, vid_likes, vid_comments)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s);""")

    row_to_insert = (video_id, video_title, video_description, video_date, video_time, vid_views, vid_likes, vid_comments)
    curr.execute(insert_into_videos, row_to_insert)

def append_from_df_to_db(curr, df):
    for i, row in df.iterrows():
        insert_into_table(curr, row['video_id'], row['video_title'], row['video_description'], row['video_date'], row['video_time'], row['vid_views'], row['vid_likes'], row['vid_comments'])



# =========================================================================== #

# TODO This is for building phase. script will be incorporated into main file
df = pd.read_csv('youtube_vids_pull.csv', index_col=0)

# df.head()


# Setup credentials
configure()
hostname, username, password, dbname, port = map(os.getenv, ["DB_HOSTNAME", "DB_USERNAME", "DB_PASSWORD","DB_NAME", "DB_PORT"])
conn = None
# Connect to database
conn = connect_to_db(hostname, dbname, username, password, port)
curr = conn.cursor() # Allows python code to execute SQL commands on db

# Create new Table on DB
# create_table(curr)

#view data in db table
curr.execute("SELECT * FROM VIDEOS")
print(curr.fetchall())

# Check to see if video exists in db - Returns df of videos/rows not in db
new_vid_df = update_db(curr, df)

# Add to db from df
append_from_df_to_db(curr, new_vid_df)

# Run this to commit changes
conn.commit()



