import subprocess
import shlex
import json
import shutil
import zipfile
import re
import requests
import bs4
import os
import fnmatch
from time import sleep

real_directory = []

def urlGenerator(name, year = ''):
    # Generates Url for Site
    if name[-1] != ' ' and year != '':
        return search + name.replace(' ', '+') + '+' + year
    elif year == '':
        if name[-1] == ' ':
            return search + name.replace(' ', '+')[:-1]
        else:
            return search + name.replace(' ', '+')
    else:
        return search + name.replace(' ', '+')[:-1] + '+' + year

def createFolder():
    # Create Folders For Movies
    for folders, subfolders, files in os.walk('.'):
        try:
            for element in files:
                if fnmatch.fnmatch(element, '*.mp4'):
                    os.mkdir(element.strip('.mp4'))
                    shutil.move(element, element.strip('.mp4'))
                elif fnmatch.fnmatch(element, '*.mkv'):
                    os.mkdir(element.strip('.mkv'))
                    shutil.move(element, element.strip('.mkv'))
                elif fnmatch.fnmatch(element, '*.avi'):
                    os.mkdir(element.strip('.avi'))
                    shutil.move(element, element.strip('.avi'))
                else:
                    break
        except:
            pass


def deepSearch():
    # Slow But More Precise Method.
    # If Len of title matches about 80 % of the search query name download the subtitle
    pass


def simpleSearch():
    # Fast But Less Precise Method.
    '''Takes Direct Movie Name for eg: Doctor.Strange.2016.Bluray.H.264-Nezu.mp4
    and Search on the site, if found Download Subtitle for it'''
    pass


def imdbYearObtainer():
    # If there is no Year in the Movie Name File, Get the Year From Imdb by checking the Runtime of the movie
    pass


def getMovieRuntime(moviefile):
    # Obtains movie Runtime For Cross-Check from IMDB i.e. Obtaining Movie Year
    cmd = 'ffprobe -show_entries format=duration -v quiet -of csv="p=0"'
    args = shlex.split(cmd)  # Creating a List of the Command and its Parameters
    args.append(file_path_with_file_name)  # Appending File to the Arguments list
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobe_output = subprocess.check_output(args).decode('utf-8')

    ffprobe_output = json.loads(ffprobe_output)  # Returns Duration in Seconds
    minutes = ffprobe_output // 60
    hours = minutes // 60
    print 'Hours %s and Minutes %s' % (hours, minutes)


def nameFinder(name, year, link):
    r = requests.get(link)
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    foundUrl = ''
    for movieName in soup.find_all('div', {'class': 'title'}):
        for searchQuery in movieName.find_all('a'):
            searchStr = searchQuery.text.replace(':', '').lower()
            if name in searchStr and year in searchStr:
                foundUrl = searchQuery.get('href')  # Obtaining First URL
                break
            elif name.lower() not in searchStr and year not in searchStr:
                continue
        if foundUrl != '':
            break
    if foundUrl == '':
        print 'Subtitles Not Found For The Movie (%s).' % name.capitalize()
    return 'https://subscene.com' + foundUrl


def downLinkFinder(link, count = 1):
    # Interaction with Site using Requests
    r = requests.get(link)
    subtitlesLst = []
    # Searching Page For Getting the Correct Movie Name
    num = 1
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    for link in soup.find_all('td', {'class': 'a1'}):
        for engLink in link.find_all('span', {'class': 'l r positive-icon'}):
            for downLink in link.find_all('a'):
                if num <= count:
                    if 'Trailer' not in link.text and 'English' in engLink.text:
                        if downLink.get('href') not in subtitlesLst:
                            subtitlesLst.append(downLink.get('href'))
                            num += 1
    return ['https://subscene.com' + i for i in subtitlesLst]


def zipExtractor(name):
    # Extracts Zip File Downloaded from Subscene
    try:
        with zipfile.ZipFile(name, "r") as z:
            z.extractall(".")
        os.remove(name)
    except:
        pass

def downloader(elements):
    r = requests.get(elements)
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    for div in soup.find_all('div', {'class': 'download'}):
        for link in div.find_all('a'):
            downLink = 'https://subscene.com' + link.get('href')
    r = requests.get(downLink, stream=True)
    d = r.headers['content-disposition']
    fname = re.findall("filename=(.+)", d)  # File Name
    for found_sub in fname:
        name = found_sub.replace('-', ' ')
        with open(name, 'wb') as f:
            for chunk in r.iter_content(
                    chunk_size=150):
                if chunk:
                    f.write(chunk)
        zipExtractor(name)

def getExtension(name):
    ext = ['.mp4', '.mkv', '.avi']
    if '.mp4' in name or '.mkv' in name or '.avi' in name:
        for elements in ext:
            if elements in name:
                return name.replace(elements,'')
    else:
        return name



def movieSubDL(mediaName, mediaYear = ''):
    # For Downloading Subtitle For Required Movie
    mediaName = getExtension(mediaName) # Removes Extension eg. --> .mp4
    firstUrl = urlGenerator(mediaName, mediaYear)
    print 'Search URL is ', firstUrl
    query = nameFinder(mediaName, mediaYear, firstUrl)  # List Of Elements
    print 'Query is ', query
    downlinks = downLinkFinder(query, 1)
    for elements in downlinks:
        downloader(elements=elements)

def nameGrabber(medialst):
    # Gets the Name of the movie whose subtitle needs to be Downloaded!
    nameslist = []
    for movies in medialst:
        try:
            yearRegex = re.compile(r'\d{4}')
            searchItems = yearRegex.search(movies)
            year = searchItems.group()
            # This is 2016 Movie --> This is | 2016 | Movie
            prev, found, removal = movies.partition(year)
            if prev[-1] == ' ':
                nameslist.append(prev.lower())
            else:
                nameslist.append(prev.lower()[:-1])
        except:
            nameslist.append(movies.lower())
            continue
    nameslist = [i.replace('.', ' ') for i in nameslist]
    return nameslist


def directoryObtainer():
    global real_directory
    for folders, subfolders, files in os.walk('.'):
        for elements in files:
            if fnmatch.fnmatch(elements, '*.mp4'):
                if './' in elements: # Linux OS
                    real_directory.append(elements.replace('./', ''))
                else: # Windows OS
                    real_directory.append(elements)
            elif fnmatch.fnmatch(elements, '*.mkv'):
                if './' in elements:
                    real_directory.append(elements)
                else:
                    real_directory.append(elements)
            elif fnmatch.fnmatch(elements, '*.avi'):
                if './' in elements:
                    real_directory.append(elements)
                else:
                    real_directory.append(elements)
    return real_directory


def locateFileFolder(filename):
    for folders, subfolders, files in os.walk('.'):
        if filename in files:
            os.chdir('../')
            return os.getcwd()


def directorySubDL(movieNames, movieDirectory):
    # For Downloading Subtitles for movies in a Directory
    cwd = os.getcwd()
    for elements in movieNames:
        os.chdir(elements)
        movieSubDL(elements)
        os.chdir(cwd)


def subChecker(directory):
    for folders, subfolders, files in os.walk(directory):
        for elements in files:
            if fnmatch.fnmatch(elements, '*.srt'):
                real_directory.remove(folders.replace('./', ''))
            elif fnmatch.fnmatch(elements, '*.py'):
                real_directory.remove(folders.replace('./', ''))


def subRenamer():
    # Rename Subtitle Downloaded To the Media File Name for auto-Sync
    pass


if __name__ == "__main__":
    makeChoice = int(raw_input("For Downloading Subtitles in A Directory Press 1\nPress 2 For Download Subtitles For a Custom Movie: "))
    search = "https://subscene.com/subtitles/title?q="
    if makeChoice == 1:
        createFolder()
        real_directory = directoryObtainer()
        names = nameGrabber(real_directory)
        directorySubDL(names, real_directory)
    elif makeChoice == 2:
        movieName = raw_input('Enter Movie Name: ')
        movieYear = raw_input('Enter Movie Release Year: ')
        movieSubDL(movieName, movieYear)
    else:
        print 'Invalid Choice!'
