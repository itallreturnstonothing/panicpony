import requests
import json
from common import *

batch_size = 50


# retrieve metadata for up to 50 video ids
def get_videos(id_list):
    if len(id_list) > batch_size:
        print_or_not("too many ids")
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
        print_or_not("it's fucked")
        print_or_not(response.text)
        return None

    json_response = json.loads(response.text)

    return json_response["items"]


if __name__ == "__main__":


    helptext = HelpText(
        input = "File containing a list of video IDs, one per line. Default is vidlist.txt. "
        "Pass - to read from stdin.",
        output = "Output file. This script will filter the input list and write only the IDs of unlisted, pre-2017 videos found to the output file, one per line. "
        "Default is no output file, only the typical stdout messages. "
        "Pass - for machine readable output to stdout. Output to stdout implies quiet operation (no human-readable messages).",
        default_input = "vidlist.txt"
    )

    common_args_parsed = parse_args(helptext, lambda x: None)
    from common import api_key # why is this so dumb
    video_list = common_args_parsed.in_file
    output_file = common_args_parsed.out_file

    try:
        real_lines = only_real_lines(video_list)
        big_list_of_ids = list(line.rstrip() for line in real_lines)


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
            print_or_not(" "*70, end="\r")
            print_or_not(f"processing batch {i+1} of {num_batches} (size {len(batch)})", end="\r")

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

        print_or_not("")

        # inform the bad news
        print_or_not(f"{len(all_in_danger)} in danger")
        for vid in all_in_danger:
            vid_id = vid["id"]
            print_or_not(f'{vid_id} -- {vid["snippet"]["title"]}')
            if output_file:
                output_file.write(f"{vid_id}\n")
    finally:
        video_list.close()
        if output_file:
            output_file.close()

