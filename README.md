# panicpony
Some tools to help discover at-risk videos for archiving before the YouTube apocalypse on July 23, 2021.

# Requirements
Please use python 3.  
These scripts **require the requests library**. Make sure you have it installed.  
All other requirements should be in the standard library.  

# Usage
Each script takes an input list and outputs to the console or a machine-readable file.  

Specify the input file with `-i <path/to/input/file>`.  
Input lines that are empty space or that start with # are ignored.  

Specify the output file with `-o <path/to/output/file>`.  
If the file exists it will be overwritten!  

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



## `find_unlisted_videos.py`
Identify at-risk videos given a list of **youtube video IDs** (not urls).  
A video ID is an 11-character unique identifier. In a youtube link it's the thing that comes after `v=`.  
For https://www.youtube.com/watch?v=rNu0bt0QjmE the id is `rNu0bt0QjmE`.  
### Examples
Process vidlist.txt (the default) and output findings to the console  
`python3 find_unlisted_videos.py`  
Process myvideos.txt and output to both the console and at-risk.txt  
`python3 find_unlisted_videos.py -i myvideos.txt -o at-risk.txt`  
Process myvideos.txt and output only to at-risk.txt  
`python3 find_unlisted_videos.py -i myvideos.txt -o at-risk.txt -q`  




## `find_unlisted_videos_in_playlist.py`
Search playlists for at-risk videos. Again the input is a list of **youtube playlist IDs** (not urls).  
A playlist ID is a unique identifier, but they're not always the same length. In a youtuble playlist link it's the thing that comes after `list=`.  
### Examples
Process playlists.txt (the default) and output findings to the console  
`python3 find_unlisted_videos_in_playlist.py`  
Process myplaylists.txt and output to both the console and at-risk.txt  
`python3 find_unlisted_videos_in_playlist.py -i myplaylists.txt -o at-risk.txt`  
Process myplaylists.txt and output only to at-risk.txt  
`python3 find_unlisted_videos_in_playlist.py -i myplaylists.txt -o at-risk.txt -q`  


# Advanced
Suppress console output with `-q`. It is an error to use `-q` without an output file, since the script will not do anything useful.  

Pipes are cool. All 3 scripts support reading from stdin and writing to stdout.  
Pass `-i -` and `-o -` to read from/write to the standard input/output.
Writing to stdout implies `-q`.  
Possibly useful in this pattern:  
`python3 get_playlists_for_channel.py -o - | python3 find_unlisted_videos_in_playlist.py -i -`

The `--key` argument will change the API key the scripts use, in case the default key stops working.  
One could also edit `common.py` to change the API key. But be careful if you do this. Committing such a change could expose your (maybe sensitive) API key to the world. 
