from common import *
import requests
import json
import re
import io
import math
import time
from more_itertools import flatten
import argparse

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
        for playlist in playlist_response["items"]: # Fixes the issue where channelId is missing
            if playlist["snippet"].get("channelId") == None:
                playlist["snippet"]["channelId"] = channel_id
        return (
                playlist_response["items"],
                playlist_response["nextPageToken"] if "nextPageToken" in playlist_response else None
                )
    elif response.status_code == 404 and json.loads(response.text)["error"]["message"] == "Channel not found.":
        return ([], None)
    else:
        print(f"failed getting playlists for {channel_id} (pageToken {page_token})")
        print(response.text)
        print("retry?")
        if input() == "y":
            return get_single_page_of_playlists(channel_id, page_token)
        else:
            return ([], None)


def get_all_playlists_for_channel(channel_id):
    # print(f"collecting playlist for channel {channel_id}")
    def get_all_playlists(channel_id, next_page):
        while(next_page):
            next_playlists, next_page = get_single_page_of_playlists(channel_id, next_page)
            yield next_playlists
    first_playlists, next_page = get_single_page_of_playlists(channel_id)
    # return [x for flatten_list in [first_playlists] + list(get_all_playlists(channel_id, next_page)) for x in flatten_list]
    return flatten([first_playlists] + list(get_all_playlists(channel_id, next_page)))



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
        print(response.text)
        print("retry?")
        if input() == "y":
            return get_upload_playlists_for_channels(channel_ids)
        else:
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

def special_parse_args():
    global api_key
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Optional API key to use. There is a default key.")

    parser.add_argument(
        "channel_list",
        help="File containing a list of channel links, one per line.",
        metavar="channel-list"
    )
    parser.add_argument(
        "output_file",
        help="append playlist information to this file",
        metavar="output-file"
    )

    args = parser.parse_args()
    print(args)

    if args.key:
        api_key = args.key
    

    input_filename = args.channel_list
    output_filename = args.output_file
    
    # try to set up the input file
    try:
        if input_filename.startswith("~"):
            import os
            input_filename = os.path.expanduser(input_filename)
        input_file = open(input_filename)
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
        input_file.close()
        exit()

    return (input_file, output_file)



if __name__ == "__main__":

    (channels_file, output_file) = special_parse_args()
    from common import api_key # why is this so dumb


    def get_id_from_basic_url(url):
        return basic_channel_url_matcher.search(url).group(1)
    def get_id_from_user_url(url):
        return get_channel_id_for_user(user_channel_url_matcher.search(url).group(1))

    def process_urls(url_list):
        for url in url_list:
            # print(f"retrieving channel id for {url}")
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


    with channels_file:
        with output_file:
            start_position = 608
            # line_length = len("https://www.youtube.com/channel/UCdMRGwr7vb9o1jcYFgz2CAg\n")
            line_length = len("UCdMRGwr7vb9o1jcYFgz2CAg\n")
            # figure out how many lines there are in total
            channels_file.seek(0, io.SEEK_END)
            file_size = channels_file.tell()
            line_count = file_size // line_length
            print(f"channels file has {line_count} lines")
            channels_file.seek(start_position * line_length)
            batches_to_process = math.ceil((line_count - start_position) / batch_size)

            def get_batches():
                while True:
                    chunk = channels_file.read(batch_size * line_length)
                    # batch = list(process_urls(chunk[:-1].split("\n")))
                    if chunk:
                        batch = list(chunk[:-1].split("\n"))
                        yield batch
                        if len(chunk) < batch_size * line_length:
                            break
                    else:
                        break

            for (i, batch) in enumerate(get_batches()):
                print(f"processing batch {i+1} of {batches_to_process} ({len(batch)})")
                channel_upload_playlists = get_upload_playlists_for_channels(batch)
                channel_playlists = list(flatten(get_all_playlists_for_channel(channel_id) for channel_id in batch))
                all_playlists = channel_upload_playlists + channel_playlists


                for channel_id in batch:
                    playlists = list(filter(lambda x: x["snippet"]["channelId"] == channel_id, all_playlists))
                    if len(playlists):
                        channel_name = playlists[0]["snippet"]["channelTitle"]
                        output_file.write(f"{channel_name}\n")
                        for playlist in playlists:
                            output_file.write(f'    {playlist["id"]} -- {playlist["snippet"]["title"]}\n')
                    else:
                        output_file.write(f"channel {channel_id} has no playlists\n")
                
                
