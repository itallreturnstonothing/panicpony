# panicpony
Some tools to help discover at-risk videos for archiving before the YouTube apocalypse on July 23, 2021.

# Requirements
Please use python 3.  
These scripts **require the requests library**. Make sure you have it installed.  
All other requirements should be in the standard library.  

# Usage
Each script takes an input list and outputs to the console or a machine-readable file.  

Specify the input file with `-i <file/path>`.  
Input lines that are empty space or that start with # are ignored.  

Specify the output file with `-o <file/path>`.  

If you want to use a different API key pass `--key <your key>`.  

## `get_playlists_for_channel.py`
Find all the associated playlists for a list of channel **urls**.  
See channellist.txt for an example input file format. 3 channel url formats are supported.  
### Examples
Process channellist.txt (the default) and output findings to the console  
`python3 get_playlists_for_channel.py`  
Process mychannels.txt and output to both the console and playlists.txt  
`python3 get_playlists_for_channel.py -i mychannels.txt -o playlists.txt`  
Process mychannels.txt and output only to playlists.txt  
`python3 get_playlists_for_channel.py -i mychannels.txt -o playlists.txt -q`  
## find_unlisted_videos.py
Identify at-risk videos given a list of **youtube video IDs** (not urls).  
A video ID is an 11-character unique identifier. In a youtube link it's the thing that comes after `watch?v=`  

