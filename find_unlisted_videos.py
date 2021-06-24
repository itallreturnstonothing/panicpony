import requests
import json
import math
from datetime import datetime
import sys
from find_unlisted_videos_in_playlist import critical_datetime, api_key, upload_date_for_video


list_of_videos_file = "testdata.txt"
batch_size = 50

sys.setrecursionlimit(10**4)

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
        
        big_list_of_ids = list(line.replace("\n", "") for line in video_list)



        # batch them up
        # a batch is a bunch of videos to get the metadata for all at once


        # distribute the video ids into the required number of batches
        num_batches = math.ceil(len(big_list_of_ids) / batch_size)
        def unneccesary_recursion(build):
            if not len(big_list_of_ids):
                # no more ids to distribute
                return build
            vid_id = big_list_of_ids.pop()
            front = build[1:]
            end = [build[0] + [vid_id]]
            return unneccesary_recursion(front + end)

        batches = unneccesary_recursion([[] for _ in range(num_batches)])

        # this works but you get no feedback
        # all_video_data = (x for flatten_list in map(get_videos, batches) for x in flatten_list)


        # process each batch, collecting the videos that are
        # unlisted and uploaded earlier than Jan 1 2017
        all_in_danger = []
        for i, batch in enumerate(batches):
            print(f"processing batch {i+1} of {num_batches} (size {len(batch)})")

            vid_metadata = get_videos(batch)

            in_danger = list(filter(
                    lambda x: ( 
                                x["status"]["privacyStatus"] == "unlisted" 
                                and 
                                upload_date_for_video(x) < critical_datetime
                            ),
                    vid_metadata
                ))
            all_in_danger.extend(in_danger)

        # inform the bad news
        print(f"{len(all_in_danger)} in danger")
        for vid in all_in_danger:
            print(f'{vid["id"]} -- {vid["snippet"]["title"]} ')

