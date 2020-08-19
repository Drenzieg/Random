import requests
import glob
import os
import sys
import moviepy.editor as mp
from bs4 import BeautifulSoup
from pytube import YouTube

##################################
# argv[1]: youtube playlist
# argv[2]: Output path
##################################


def getPlaylistLinks(url):
    sourceCode = requests.get(url).text
    soup = BeautifulSoup(sourceCode, 'html.parser')
    domain = 'https://www.youtube.com'
    links = []
    print("Songs in Playlist:")
    for link in soup.find_all("a", {"dir": "ltr"}):
        href = link.get('href')
        if href.startswith('/watch?'):
            print("\t" + link.string.strip())
            # print(domain + href + '\n')
            links.append([link.string.strip(), domain + href])
    return links


def ripVideos(links, download_dir):
    ignore_list = []
    for downloaded in glob.glob(download_dir + '*.mp4'):
        ignore_list.append(os.path.basename(downloaded)[:-4])

    print("\nDownloading to:")
    reruns = []
    fail_counter = 0
    for link in links:
        if (link[0]
                    .replace(".", "")
                    .replace("'", "")
                    .replace(",", "")
            ) not in ignore_list:
            try:
                print("\t" + link[0])
                yt = YouTube(link[1])
                yt = yt.streams.first().download(download_dir)
                print("\t\t" + yt)
            except:
                fail_counter += 1
                print("\t\tFailed!")
                reruns.append(link)
        else:
            print("\tSkipping", link[0])
    print(fail_counter)
    if len(reruns) != 0:
        ripVideos(reruns, download_dir)


def convertToMp3(videos, output_path):
    print("\nConverting to MP3:")
    for video in glob.glob(videos + '*.mp4'):
        name = output_path + os.path.basename(video)[:-3] + "mp3"
        print("\t", name)
        try:
            clip = mp.VideoFileClip(video)
            clip.audio.write_audiofile(name)
            clip.reader.close()
            clip.audio.reader.close_proc()
        except OSError as e:
            print(e, name)

if __name__ == "__main__":
    if not os.path.isdir(sys.argv[2] + "Video\\"):
        os.mkdir(sys.argv[2] + "Video\\")
    if not os.path.isdir(sys.argv[2] + "Audio\\"):
        os.mkdir(sys.argv[2] + "Audio\\")

    playlist = getPlaylistLinks(sys.argv[1])
    ripVideos(playlist, sys.argv[2] + "Video\\")
    convertToMp3(sys.argv[2] + "Video\\", sys.argv[2] + "Audio\\")

