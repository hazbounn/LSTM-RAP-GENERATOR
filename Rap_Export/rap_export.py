# Rap Lyrics Exporter for INF8801A Project
# Using LyricsGenius Framework https://github.com/johnwmillr/LyricsGenius
# Simon Felteau
# Nicolas Hazboun

from LyricsGenius import lyricsgenius
import os
import json

genius = lyricsgenius.Genius("RnQTAFx2K7ec8RZu_ZTB9oCaUniy23M-HSXn8CryW8l1qqfRfuL6pAIj6E_SHhh6")
genius.verbose = True
genius.remove_section_headers = False
genius.skip_non_songs = True
genius.excluded_terms = [("(Instrumental)", "(Remix)", "(Live)")]

artists = ["MF DOOM", "Mos_Def", "Aesop Rock", "Open Mike Eagle", "GZA"]
lyricsFilter = ["[Skit", "[Bridge", "[Prod"]
selectiveCount = 3
completeCount = 12

# Output Directory Creation
if not os.path.exists("out"):
	os.makedirs("out")
os.chdir("out")

for i in artists:
	# Artist Integration and Directory Creation
	if not os.path.exists(i):
		os.makedirs(i)
		if not os.path.exists(i + "/Selective"):
				os.makedirs(i + "/Selective")
		if not os.path.exists(i + "/Complete"):
				os.makedirs(i + "/Complete")

	# Artist Selective Seeking
	os.chdir(i + "/Selective")
	artistDisc = genius.search_artist(i, max_songs = selectiveCount, sort = "popularity", get_full_info = False)
	artistDisc.save_lyrics()

	# Selective Result Compilation
	data = {"songs":[]}
	for j in [f for f in os.listdir(".") if os.path.isfile(os.path.join(".", f))]:
		with open(j, "r") as currentSong:
			tmp = json.load(currentSong)
			# Selective Result Filtering (TODO)
			#for k in lyricsFilter:
			#	if k in tmp["songs"][0]["lyrics"]:
					
			data["songs"].append(tmp["songs"][0])
	with open(i + "_Selective.json", "w+") as compiledSongs:
		json.dump(data, compiledSongs)
	os.chdir("../../")

	# Artist Complete Seeking
	os.chdir(i + "/Complete")
	artistDisc = genius.search_artist(i, max_songs = completeCount, sort = "popularity", get_full_info = False)
	artistDisc.save_lyrics()

	# Complete Result Compilation
	data = {"songs":[]}
	for j in [f for f in os.listdir(".") if os.path.isfile(os.path.join(".", f))]:
		with open(j, "r") as currentSong:
			tmp = json.load(currentSong)
			data["songs"].append(tmp["songs"][0])
	with open(i + "_Complete.json", "w+") as compiledSongs:
		json.dump(data, compiledSongs)
	os.chdir("../../")