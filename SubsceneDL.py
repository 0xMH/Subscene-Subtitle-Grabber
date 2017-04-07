'''Version = 1
Author = Rafay Ghafoor
Email = rafayghafoor@protonmail.com
Date Created = Feb 19, 2017 (Version 1)
Updated = March 26, 2017
'''
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
ext = ['.mp4', '.mkv', '.avi']

def createFolder():
    # Create Folders For Movies
    global ext
    for files in os.listdir('.'):
        for extension in ext:
            try:
                if files.endswith(extension):
                    os.mkdir(files.strip(extension))
                    shutil.move(files, files.strip(extension))
                else:
                    continue
            except:
                pass


def deepSearch():
    # Slow But More Precise Method.
    # If Len of title matches about 80 % of the search query name download the subtitle
    pass


def simpleSearch():
    # Fast But Lesss Precise Method.
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


def nameFinder(name, year, parameter):
    r = requests.get(search, {'q': parameter})
    print 'Generated URL is ---> %s\n' % r.url
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    foundUrl = ''
    for movieName in soup.find_all('div', {'class': 'title'}):
        for searchQuery in movieName.find_all('a'):
            searchStr = searchQuery.text.replace(':', '').lower()
            if name.lower() in searchStr and year in searchStr:
                foundUrl = searchQuery.get('href')  # Obtaining First URL
                break
            elif name.lower() not in searchStr and year not in searchStr:
                continue
        if foundUrl != '':
            break
    if foundUrl == '':
        print 'Subtitles Not Found for the Movie (%s).\n' % name.title()
    else:
        return 'https://subscene.com' + foundUrl


def downLinkFinder(page_link, count = 1):
    # Interaction with Site using Requests
    r = requests.get(page_link)
    sub_list = []   # Subtitles List
    # Searching Page For Getting the Correct Movie Name
    link_num = 1
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    for link in soup.find_all('td', {'class': 'a1'}):
        for eng_link in link.find_all('span', {'class': 'l r positive-icon'}):
            for down_link in link.find_all('a'):
                if link_num <= count:
                    if 'Trailer' not in link.text and 'English' in eng_link.text:
                        if down_link.get('href') not in sub_list:
                            sub_list.append(down_link.get('href'))
                            link_num += 1
    return ['https://subscene.com' + i for i in sub_list]


def zipExtractor(name):
    # Extracts Zip File Downloaded from Subscene
    try:
        with zipfile.ZipFile(name, "r") as z:
            z.extractall(".")
        os.remove(name)
    except:
        pass

def downloader(dl_links):
    r = requests.get(dl_links)
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    for div in soup.find_all('div', {'class': 'download'}):
        for link in div.find_all('a'):
            down_link = 'https://subscene.com' + link.get('href')
    r = requests.get(down_link, stream=True)
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

def removeExtension(name):
    global ext
    newvar = ''
    for extension in ext:
        if extension in name:
            newvar = name.replace(extension,'')
            break
        else:
            continue
    if newvar == '':
        return name
    else:
        return newvar


def movieSubDL(mediaName = '', mediaYear = ''):
    # For Downloading Subtitle For Required Movie
    mediaName = removeExtension(mediaName) # Removes Extension eg. --> .mp4
    if mediaYear != '':
        mediaName = mediaName.strip(mediaYear)
    parameters = mediaName.strip(' ')
    query = nameFinder(mediaName, mediaYear, parameters)  # List Of Elements
    if query != None:
        downlinks = downLinkFinder(query, 1)
        for elements in downlinks:
            print '[*] - Downloading Subtitle For %s' % (mediaName.title() + mediaYear)
            downloader(elements)
            print '[+] - Subtitle Downloaded!'


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
                nameslist.append(prev.lower() + found)
            else:
                nameslist.append(prev.lower()[:-1] + found)
        except:
            nameslist.append(movies.lower() + found)
            continue
    nameslist = [i.strip(' ') for i in nameslist]
    return nameslist


def directoryObtainer():
    global real_directory
    global ext

    for folders, subfolders, files in os.walk('.'):
        for elements in files:
            for extension in ext:
                if elements.endswith(extension):
                    if './' in elements:
                        real_directory.append(elements.replace('./', ''))
                    else:
                        real_directory.append(elements)
    return real_directory


def fileLocator(name):
    for files in os.listdir('.'):
        if files.endswith('.py') == False:
            # if os.path.isdir(elements) == True:
            count = 0
            for folders, subfolders, files in os.walk('.'):
                for elem in files:
                    if name == elem:
                        return folders.replace('./', '')
                        count += 1
                        break
                if count == 1:
                    break


def directorySubDL(movieNames, movieDirectory):
    # For Downloading Subtitles for movies in a Directory
    cwd = os.getcwd()
    num = 0
    for elements in movieNames:
        # os.chdir(elements)
        location = fileLocator(real_directory[num])
        os.chdir(location)
        try:
            yearRegex = re.compile(r'\d{4}')
            searchItems = yearRegex.search(elements)
            movieYear = searchItems.group()
        except:
            movieYear = ''
        movieSubDL(elements, movieYear)
        os.chdir(cwd)
        if num != len(real_directory) - 1:
            num += 1
        else:
            break


def subChecker(directory):
    for folders, subfolders, files in os.walk('.'):
        for elements in files:
            if elements.endswith('.srt') or elements.endswith('.ass'):
                try:
                    for movies in files:
                        if movies.endswith('.mkv') or movies.endswith('.avi') or movies.endswith('.mp4'):
                            directory.remove(movies)
                except:
                    pass
            elif elements.endswith('.py'):
                try:
                    directory.remove(elements)
                except:
                    pass
    directory = [i.replace('.', ' ') for i in directory]
    return directory



def subRenamer():
    # Rename Subtitle Downloaded To the Media File Name for auto-Sync
    pass


def main():
    makeChoice = int(raw_input("Press [1] - For Downloading Subtitles in A Directory.\n\
Press [2] - For Download Subtitles For a Custom Movie:\n\
Your Input [-]:  "))
    search = "https://subscene.com/subtitles/title"
    if makeChoice == 1:
        createFolder()
        real_directory = directoryObtainer()
        newdir = subChecker(real_directory)
        names = nameGrabber(newdir)
        directorySubDL(names, newdir)
    elif makeChoice == 2:
        movieName = raw_input('Enter Movie Name: ')
        movieYear = raw_input('Enter Movie Release Year: ')
        movieSubDL(movieName, movieYear)
    else:
        print 'Invalid Choice!'
