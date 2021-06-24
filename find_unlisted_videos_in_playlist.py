import requests
import json
from datetime import datetime, timezone

# const
critical_datetime = datetime(year=2017, month=1, day=2, tzinfo=timezone.utc)
# january 2 just to be safe

###############################
#    CHANGE THESE VARIABLES   #
#    for config adjustments   #
###############################
api_key = "AIzaSyA-dlBUjVQeuc4a6ZN4RkNUYDFddrVLxrA"
list_of_playlists_file = "playlists.txt"


def get_single_page_of_videos(playlist_id, page_token=None):
    response = requests.get(
            (   
                f'https://www.googleapis.com/youtube/v3/playlistItems?'
                f'playlistId={playlist_id}'
                f'&part=status,snippet'
                f'&maxResults=50'
                f'{"&pageToken=" + page_token if page_token else ""}'
                f'&key={api_key}'
            )
        )

    if not response.status_code == 200:
        print("it's fucked")
        return None

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
    with open(list_of_playlists_file) as playlists:
        for pl_id in (x.replace("\n", "") for x in playlists):

            print(f"===== processing {pl_id} =====")


            videos = get_all_videos_from_playlist(pl_id)
            print(f"{len(videos)} videos")


            # find all the unlisted videos in the playlist
            unlisted = list(filter(lambda x: x["status"]["privacyStatus"] == "unlisted", videos))
            print(f"{len(unlisted)} unlisted")

            # parse the upload time for each unlisted video
            # (god damn datetime is a PITA)
            unlisted_plus_upload_time = [
                (x, datetime.strptime(x["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)) for x in unlisted
            ]

            # find all the videos uploaded before the critical time
            in_danger = list(filter(lambda x: x[1] < critical_datetime, unlisted_plus_upload_time))

            # print findings to the console
            print(f"{len(in_danger)} in danger")
            for (vid, _) in in_danger:
                print(f'    title -- {vid["snippet"]["title"]}')
                print(f'    id ----- {vid["snippet"]["resourceId"]["videoId"]}')
