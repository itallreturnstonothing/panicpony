import json
import os


if __name__ == "__main__":
    usable_path = os.path.expanduser("~/Documents/ponyvideodata/comment_metadata")
    walk = os.walk(usable_path)
    # metadata_files = [x for (_, _, filelist) in walk for x in filelist]
    metadata_files = [path + "/" + filename for (path, _, filelist) in walk for filename in filelist]
    channels = set()
    for filename in metadata_files:
        with open(filename) as metadata_file:
            data = json.load(metadata_file)
            if data["comment_count"]:
                channels.update(comment["author_id"] for comment in data["comments"] if "author_id" in comment)

    with open("many_channels.txt", "w") as outfile:
        for channel_id in channels:
            outfile.write(f"https://www.youtube.com/channel/{channel_id}\n")


