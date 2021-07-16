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
        input = "do not use",
        output = "do not use",
        default_input = "playlists.txt"
    )

    def add_input_output(parser):
        parser.add_argument(
            "playlists",
            help="File containing a list of playlist ids, one per line.",
            metavar="playlists"
        )
        parser.add_argument(
            "output_file",
            help="append unlisted video information to this file",
            metavar="output-file"
        )

    common_args_parsed = parse_args(helptext, add_input_output)
    from common import api_key # why is this so dumb



    input_filename = common_args_parsed.more_args.playlists
    output_filename = common_args_parsed.more_args.output_file
    
    # try to set up the input file
    try:
        if input_filename.startswith("~"):
            import os
            input_filename = os.path.expanduser(input_filename)
        playlists = open(input_filename)
    except Exception as e:
        print(f"failed to open input file {input_filename}")
        print(e)
        exit()

    try:
        if output_filename.startswith("~"):
            import os
            output_filename = os.path.expanduser(output_filename)
        output_file = open(output_filename, "a")
    except Exception as e:
        print(f"failed to open output file {output_filename}")
        print(e)
        playlists.close()
        exit()

    resume_from_line = 0

    try:
        real_lines = only_real_lines(playlists)
        for (i, pl_id) in enumerate(x.rstrip() for x in real_lines):
            if i < resume_from_line:
                continue

            # print_or_not(f"===== processing {pl_id} =====")


            videos = get_all_videos_from_playlist(pl_id)
            # print_or_not(f"{len(videos)} videos")


            # find all the unlisted videos in the playlist
            unlisted = list(filter(lambda x: x["status"]["privacyStatus"] == "unlisted", videos))
            # print_or_not(f"{len(unlisted)} unlisted")

            # parse the upload time for each unlisted video
            # (god damn datetime is a PITA)
            unlisted_plus_upload_time = [
                (x, parse_date_format(x["contentDetails"]["videoPublishedAt"])) for x in unlisted
            ]

            # find all the videos uploaded before the critical time
            in_danger = list(filter(lambda x: x[1] < critical_datetime, unlisted_plus_upload_time))

            # print findings to the console
            # print_or_not(f"{len(in_danger)} in danger")
            for (vid, _) in in_danger:
                vid_id = vid["snippet"]["resourceId"]["videoId"]
                title = vid["snippet"]["title"]
                thumbnails = vid["snippet"]["thumbnails"]
                useful = {k : thumbnails[k]["url"] for k in thumbnails.keys() if "url" in thumbnails[k]}
                thumb_str = json.dumps(useful)
                # print_or_not(f'    {vid_id} -- {vid["snippet"]["title"]} ')
                output_file.write(f"{vid_id} -- {thumb_str} -- {title}\n")
                # write channel name and ID too, to better fit metadata.json
            info =  f"finished index {i} ({pl_id})"
            pad = 80 - len(info)
            if pad > 0:
                print(info + (" " * pad), end="\r")
            else:
                print(info)
        print()
    finally:
        playlists.close()
        if output_file:
            output_file.close()