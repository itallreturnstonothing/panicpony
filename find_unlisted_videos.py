import requests
import json
import sys
from common import *

list_of_videos_file = "testdata.txt"
batch_size = 50


# retrieve metadata for up to 50 video ids
def get_videos(id_list):
    if len(id_list) > batch_size:
        print("too many ids")
        return None

    response = requests.get(
            (   
                f'https://www.googleapis.com/youtube/v3/videos?'
                f'id={",".join(id_list)}'
                f'&part=snippet,status'
                f'&key={api_key}'
            )
        )

    if not response.status_code == 200:
        print("it's fucked")
        print(response.text)
        return None

    json_response = json.loads(response.text)

    return json_response["items"]


if __name__ == "__main__":

    with open(list_of_videos_file) as video_list:
        
        big_list_of_ids = list(line.rstrip() for line in video_list)



        # batch them up
        # a batch is a bunch of videos to get the metadata for all at once
        
        batches = make_batches_of_size(big_list_of_ids, batch_size)
        num_batches = len(batches)

        # this works but you get no feedback
        # all_video_data = (x for flatten_list in map(get_videos, batches) for x in flatten_list)


        # process each batch, collecting the videos that are
        # unlisted and uploaded earlier than Jan 1 2017
        all_in_danger = []
        for i, batch in enumerate(batches):
            print(" "*70, end="\r")
            print(f"processing batch {i+1} of {num_batches} (size {len(batch)})", end="\r")

            vid_metadata = get_videos(batch)

            in_danger = list(filter(
                    lambda x: ( 
                                x["status"]["privacyStatus"] == "unlisted" 
                                and 
                                parse_date_format(x["snippet"]["publishedAt"]) < critical_datetime
                            ),
                    vid_metadata
                ))
            all_in_danger.extend(in_danger)

        print()

        # inform the bad news
        print(f"{len(all_in_danger)} in danger")
        for vid in all_in_danger:
            print(f'{vid["id"]} -- {vid["snippet"]["title"]}')

