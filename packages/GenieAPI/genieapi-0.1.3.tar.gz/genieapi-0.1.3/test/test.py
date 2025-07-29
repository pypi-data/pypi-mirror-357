from genieapi import GenieAPI

genie = GenieAPI()
song = genie.search_song("파도혁명",limit=1)

genie.get_lyrics(song[0][1])