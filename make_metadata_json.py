import argparse
import json
import os
import requests
import math
from datetime import datetime, timezone

batch_size = 50
api_key = "AIzaSyA-dlBUjVQeuc4a6ZN4RkNUYDFddrVLxrA"

# take an iterable and distribute it about evenly
# into some number of batches with at most batch_size items
def make_batches(big_list):
    big_list = list(big_list) if not isinstance(big_list, list) else big_list
    num_batches = math.ceil(len(big_list) / batch_size)
    def unnecessary_recursion(remain, build):
        if not len(remain):
            # no more ids to distribute
            return build
        curr = remain.pop()
        front = build[1:]
        end = [build[0] + [curr]]
        return unnecessary_recursion(remain, front + end)

    kickstart = [big_list[i*(batch_size - 1):(i + 1)*(batch_size - 1)] for i in range(num_batches)]
    remain = big_list[num_batches*(batch_size - 1):]
    return unnecessary_recursion(remain, kickstart)

def only_real_lines(iterable_lines):
    return (line for line in iterable_lines if not (line.isspace() or line.strip()[0] == "#"))

def parse_date_format(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

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

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        help="list of video ids, one per line.",
        metavar="input-file",
    )
    parser.add_argument(
        "output_file",
        help="metadata.json file.",
        metavar="output-file"
    )

    args = parser.parse_args()
    in_filename = os.path.expanduser(args.input_file)
    out_filename = os.path.expanduser(args.output_file)


    all_vid_data = []

    with open(in_filename) as video_list:

        print("gathering IDs")
        real_lines = only_real_lines(video_list)
        all_ids = (line.strip() for line in real_lines)
        batches = make_batches(all_ids)

        for i, batch in enumerate(batches):
            vid_metadata = get_videos(batch)
            all_vid_data.extend(vid_metadata)
            # print("\r" + " " * 50, end="\r")
            print(f"processed batch {i+1}", end="\r")
        print()

    def make_dictionaries():
        for vid in all_vid_data:
            # print(f'{vid_id} -- {vid["snippet"]["title"]}')
            vid_id = vid["id"]
            channel_id = vid["snippet"]["channelId"]
            date_obj = parse_date_format(vid["snippet"]["publishedAt"])
            thumbnail = vid["snippet"]["thumbnails"]["high"]["url"]
            date_str = date_obj.strftime("%Y%m%d")
            video_browser_format = {
                "id"            : vid_id,
                "uploader"      : vid["snippet"]["channelTitle"],
                "upload_date"   : date_str,
                "thumbnail"     : thumbnail,
                "title"         : vid["snippet"]["title"],
                "uploader_url"  : f"http://www.youtube.com/channel/{channel_id}",
                "webpage_url"   : f"https://youtube.com/watch?v={vid_id}",
                "unavailable"   : None,
                "reupload"      : None,
                "archived"      : {}
            }
            yield video_browser_format
    print("writing metadata")
    with open(out_filename, "w") as output_file:
        json.dump(list(make_dictionaries()), output_file)

    print("done")
            