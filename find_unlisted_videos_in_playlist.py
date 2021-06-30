import requests
import json
from common import *


def get_single_page_of_videos(playlist_id, page_token=None):
    response = requests.get(
            (   
                f'https://www.googleapis.com/youtube/v3/playlistItems?'
                f'playlistId={playlist_id}'
                f'&part=status,snippet,contentDetails'
                f'&maxResults=50'
                f'{"&pageToken=" + page_token if page_token else ""}'
                f'&key={api_key}'
            )
        )

    if not response.status_code == 200:
        print_or_not("it's fucked")
        return ([], None)

    precious_data = json.loads(response.text)
    return (
                precious_data["items"], 
                precious_data["nextPageToken"] if "nextPageToken" in precious_data else None
            )



    
def get_all_videos_from_playlist(playlist_id):
    # voodoo 
    (first_videos, next_page) = get_single_page_of_videos(playlist_id)
    def amazing(next_page):
        while next_page:
            next_videos, next_page = get_single_page_of_videos(playlist_id,next_page)
            yield next_videos

    return [x for flatten_list in [first_videos] + list(amazing(next_page)) for x in flatten_list]





if __name__ == "__main__":

    helptext = HelpText(
        input = "File containing a list of playlist IDs, one per line. Default is playlists.txt. "
        "Pass - to read from stdin.",
        output = "Output file. This script will write only the IDs of unlisted, pre-2017 videos found, one per line. "
        "Default is no output file, only the typical stdout messages. "
        "Pass - for machine readable output to stdout. Output to stdout implies quiet operation (no human-readable messages).",
        default_input = "playlists.txt"
    )

    common_args_parsed = parse_args(helptext, lambda x: None)
    from common import api_key # why is this so dumb
    playlists = common_args_parsed.in_file
    output_file = common_args_parsed.out_file

    try:
        for pl_id in (x.rstrip() for x in playlists):

            print_or_not(f"===== processing {pl_id} =====")


            videos = get_all_videos_from_playlist(pl_id)
            print_or_not(f"{len(videos)} videos")


            # find all the unlisted videos in the playlist
            unlisted = list(filter(lambda x: x["status"]["privacyStatus"] == "unlisted", videos))
            print_or_not(f"{len(unlisted)} unlisted")

            # parse the upload time for each unlisted video
            # (god damn datetime is a PITA)
            unlisted_plus_upload_time = [
                (x, parse_date_format(x["contentDetails"]["videoPublishedAt"])) for x in unlisted
            ]

            # find all the videos uploaded before the critical time
            in_danger = list(filter(lambda x: x[1] < critical_datetime, unlisted_plus_upload_time))

            # print findings to the console
            print_or_not(f"{len(in_danger)} in danger")
            for (vid, _) in in_danger:
                vid_id = vid["snippet"]["resourceId"]["videoId"]
                print_or_not(f'    {vid_id} -- {vid["snippet"]["title"]} ')
                if output_file:
                    output_file.write(f"{vid_id}\n")
    finally:
        playlists.close()
        if output_file:
            output_file.close()