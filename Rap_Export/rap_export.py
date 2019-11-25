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

artists = ["Mos Def", "MF DOOM", "Aesop Rock", "Open Mike Eagle", "GZA"]
lyricsFilter = ["[Skit", "[Bridge", "[Prod", "[Intro", "[Hook", "[Chorus", "[Interlude", "[Outro", "[Sample", "[Scratching", "[Verse", "[Part"]
selectiveCount = 1
completeCount = 3

# Output Directory Creation
if not os.path.exists("out"):
	os.makedirs("out")
os.chdir("out")

def Filterer(data, filter, artist):
	split1 = data.split(filter, 1)[0]
	split2 = data.split(filter, 1)[1]
	if filter == "[Verse" or filter == "[Part":
		partEnd = split2.split("\n", 1)[0]
		verse = split2.split("\n", 1)[1]
		if partEnd.find(artist, 0) != -1 or partEnd.find(":", 0) == -1:
			data = split1 + verse
			if data.find(filter, 0, len(data)) != -1:
				data = Filterer(data, filter, artist)
			return data
		else:
			partEndIndex = split2.find("\n\n", 0)
			if partEndIndex != -1:
				partEnd = split2[0:partEndIndex + 2]
			else:
				partEnd = split2
	else:
		partEndIndex = split2.find("\n\n", 0)
		if partEndIndex != -1:
			partEnd = split2[0:partEndIndex + 2]
		else:
			partEnd = split2
	filteredTmp = split2.split(partEnd, 1)[1]
	data = split1 + filteredTmp

	if data.find(filter, 0, len(data)) != -1:
		data = Filterer(data, filter, artist)
	return data

def Untokenize(data):
	split1 = data.split("\n", 1)[0]
	split2 = data.split("\n", 1)[1]
	data = split1 + "<endline>" + split2
	print(data.find("\n", 0, len(data)))
	if data.find("\n", 0, len(data)) != -1:
		data = Untokenize(data)
	return data


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
	untokenizedData = {"songs":[]}
	for j in [f for f in os.listdir(".") if os.path.isfile(os.path.join(".", f))]:
		if j.find("lyrics") != -1:
			with open(j, "r") as currentSong:
				tmp = json.load(currentSong)
				for k in lyricsFilter:
					filterIndex = tmp["songs"][0]["lyrics"].find(k, 0, len(tmp["songs"][0]["lyrics"]))
					if filterIndex != -1: 
						tmp["songs"][0]["lyrics"] = Filterer(tmp["songs"][0]["lyrics"], k, i)

				untokenizedTmp = tmp
				untokenizedTmp["songs"][0]["lyrics"] = Untokenize(untokenizedTmp["songs"][0]["lyrics"])

				data["songs"].append(tmp["songs"][0])
				untokenizedData["songs"].append(untokenizedTmp["songs"][0])

	with open(i + "_Selective.json", "w+") as compiledSongs:
		json.dump(data, compiledSongs)
	with open(i + "_Selective_Untokenized.json", "w+") as compiledSongs:
		json.dump(untokenizedData, compiledSongs)
	os.chdir("../../")

	# Artist Complete Seeking
	os.chdir(i + "/Complete")
	artistDisc = genius.search_artist(i, max_songs = completeCount, sort = "popularity", get_full_info = False)
	artistDisc.save_lyrics()

	# Complete Result Compilation
	data = {"songs":[]}
	untokenizedData = {"songs":[]}
	for j in [f for f in os.listdir(".") if os.path.isfile(os.path.join(".", f))]:
		if j.find("lyrics") != -1:
			with open(j, "r") as currentSong:
				tmp = json.load(currentSong)
				for k in lyricsFilter:
					filterIndex = tmp["songs"][0]["lyrics"].find(k, 0, len(tmp["songs"][0]["lyrics"]))
					if filterIndex != -1: 
						tmp["songs"][0]["lyrics"] = Filterer(tmp["songs"][0]["lyrics"], k, i)

				untokenizedTmp = tmp
				untokenizedTmp["songs"][0]["lyrics"] = Untokenize(untokenizedTmp["songs"][0]["lyrics"])

				data["songs"].append(tmp["songs"][0])
				untokenizedData["songs"].append(untokenizedTmp["songs"][0])
	with open(i + "_Complete.json", "w+") as compiledSongs:
		json.dump(data, compiledSongs)
	with open(i + "_Complete_Untokenized.json", "w+") as compiledSongs:
		json.dump(untokenizedData, compiledSongs)
	os.chdir("../../")

