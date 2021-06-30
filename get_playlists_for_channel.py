from common import *
import requests
import json
import re
import sys

channels_list = "channellist.txt"
batch_size = 50


basic_channel_url_matcher = re.compile(r"youtube.com/channel/(.{24})")
user_channel_url_matcher = re.compile(r"youtube.com/user/([^/]+)")
custom_url_matcher = re.compile(r"(youtube.com/c/[^/]+)")

# a channel's uploaded videos playlist can be obtained
# from the channel id just by replacing a character
def transform_to_uploads_id(channel_id):
    return "UU" + channel_id[2:]


def get_channel_id_for_user(username):
    # TODO can a username have characters that are invalid for a url?
    #      does the username need to be urlencoded?
    response = requests.get(
            (
                f'https://www.googleapis.com/youtube/v3/channels?'
                f'forUsername={username}'
                f'&part=id'
                f'&key={api_key}'
            )

        )
    if response.status_code == 200:
        channel_response = json.loads(response.text)
        if "items" in channel_response and len(channel_response["items"]):
            return channel_response["items"][0]["id"]
        else:
            print("problem!")
            print(username)
            print(response.text)
    else:
        print(f"bad response for {username}")
        print(response.text)
    # fallthrough
    return None


def get_channel_id_for_custom_url(custom_url):
    url_to_use = "https://" + custom_url_matcher.search(custom_url).group(1)
    response = requests.get(custom_url, cookies=consent_cookies)
    if response.status_code == 200:
        # thanks Anon
        # grep -oP "(?<=externalId\":)[[:graph:]]+(?=,)
        match1 = re.search(r'externalId":"(.*?)"', response.text)
        # grep -oP "(?<=channel\-external\-id=\")[[:graph:]]+(?=\")"
        match2 = re.search(r'channel-external-id="(.*?)"', response.text)
        if match1:
            return match1.group(1)
        elif match2:
            return match2.group(1)
        else:
            print(f"can't get channel id: {custom_url}")
            print(response.text)
    else:
        print(f"bad url {custom_url}")
        print(response.text)
    return None



def get_single_page_of_playlists(channel_id, page_token=None):
    response = requests.get(
            (
                f'https://www.googleapis.com/youtube/v3/playlists?'
                f'part=id,snippet'
                f'&maxResults=50'
                f'&channelId={channel_id}'
                f'{"&pageToken=" + page_token if page_token else ""}'
                f'&key={api_key}'
            )
        )
    if response.status_code == 200:
        playlist_response = json.loads(response.text)
        return (
                playlist_response["items"],
                playlist_response["nextPageToken"] if "nextPageToken" in playlist_response else None
                )
    else:
        print(f"failed getting playlists for {channel_id} (pageToken {page_token})")
        print(response.text)
        return None


def get_all_playlists_for_channel(channel_id):
    def get_all_playlists(channel_id, next_page):
        print(f"Getting playlists from {channel_id}", file=sys.stderr)
        while(next_page):
            next_playlists, next_page = get_single_page_of_playlists(channel_id, next_page)
            yield next_playlists
    first_playlists, next_page = get_single_page_of_playlists(channel_id)
    return [x for flatten_list in [first_playlists] + list(get_all_playlists(channel_id, next_page)) for x in flatten_list]



def get_upload_playlists_for_channels(channel_ids):
    if len(channel_ids) > batch_size:
        print("woah pardner")
        return None
    playlist_ids = map(transform_to_uploads_id, channel_ids)
    response = requests.get(
            (
                f'https://www.googleapis.com/youtube/v3/playlists?'
                f'part=id,snippet'
                f'&id={",".join(playlist_ids)}'
                f'&maxResults=50'
                f'&key={api_key}'
            )
        )
    if not response.status_code == 200:
        print("problem getting channel upload playlists")
        print(resposne.text)
        return None

    playlists_response = json.loads(response.text)
    return playlists_response["items"]

# unnecessary
''' 
def get_channel_names(channel_ids):
    if len(channel_ids) > batch_size:
        print("woah pardner")
        return None
    response = requests.get(
            (
                f'https://www.googleapis.com/youtube/v3/channels?'
                f'part=id,snippet'
                f'&id={",".join(channel_ids)}'
                f'&maxResults=50'
                f'&key={api_key}'
            )
        )
    if not response.status_code == 200:
        print("problem getting channel names")
        print(resposne.text)
        return None

    channel_names_response = json.loads(response.text)
    return {c["id"] : c["snippet"]["title"] for c in playlists_response["items"]}
'''
    


if __name__ == "__main__":
    with open(channels_list) as channels_file:
        def get_id_from_basic_url(url):
            return basic_channel_url_matcher.search(url).group(1)
        def get_id_from_user_url(url):
            return get_channel_id_for_user(user_channel_url_matcher.search(url).group(1))

        def process_urls(url_list):
            for url in url_list:
                if not url or url.startswith("#"):
                    continue
                print(f"Processing {url}...", file=sys.stderr)
                if basic_channel_url_matcher.search(url):
                    yield get_id_from_basic_url(url)
                elif user_channel_url_matcher.search(url):
                    c_id = get_id_from_user_url(url)
                    if c_id:
                        yield c_id
                elif custom_url_matcher.search(url):
                    c_id = get_channel_id_for_custom_url(url) 
                    if c_id:
                        yield c_id
                else:
                    print(f"can't handle url {url}")

        channel_ids = list(process_urls(x.replace("\n", "") for x in channels_file))

    # get the channels' uploads playlists
    channel_id_batches = make_batches_of_size(channel_ids, batch_size)
    channel_upload_playlists = [x for flatten_list in map(get_upload_playlists_for_channels, channel_id_batches) for x in flatten_list]

    # get other playlists associated with channels
    channel_playlists = [x for flatten_list in map(get_all_playlists_for_channel, channel_ids) for x in flatten_list]

    all_playlists = channel_upload_playlists + channel_playlists

    # channel title exists in the snippet for each playlist
    # don't need to do this vvvv 

    # get channel names for more readable output
    # channel_names = {}
    # for batch in channel_id_batches:
    #     channel_names.update(get_channel_names(batch))


    for channel_id in channel_ids:
        playlists = list(filter(lambda x: x["snippet"]["channelId"] == channel_id, all_playlists))
        if len(playlists):
            channel_name = playlists[0]["snippet"]["channelTitle"]
            print(f"{channel_name}")
            for playlist in playlists:
                print(f'    {playlist["id"]} -- {playlist["snippet"]["title"]}')
        else:
            print(f"channel {channel_id} has no playlists")
