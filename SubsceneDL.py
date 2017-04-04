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

def createFolder():
    # Create Folders For Movies
    for files in os.listdir('.'):
        try:
            if files.endswith('.mp4'):
                os.mkdir(files.strip('.mp4'))
                shutil.move(files, files.strip('.mp4'))
            elif files.endswith('.mkv'):
                os.mkdir(files.strip('.mkv'))
                shutil.move(files, files.strip('.mkv'))
            elif files.endswith('.avi'):
                os.mkdir(files.strip('.avi'))
                shutil.move(files, files.strip('.avi'))
            else:
                continue
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

def downloader(links):
    r = requests.get(links)
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

def removeExtension(name):
    ext = ['mp4', 'mkv', 'avi']
    newvar = ''
    for elements in ext:
        if elements in name:
            newvar = name.replace(elements,'')
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
    parameters = mediaName
    if parameters[-1] == ' ':
        parameters = parameters[:-1]
    else:
        parameters = mediaName + ' ' + mediaYear
    query = nameFinder(mediaName, mediaYear, parameters)  # List Of Elements
    if query != None:
        downlinks = downLinkFinder(query, 1)
        for elements in downlinks:
            print '[*] - Downloading Subtitle For %s' % (mediaName + mediaYear)
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
            searchItems = yearRegex.search(movies)
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
            if elements.endswith('.srt'):
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
    return directory



def subRenamer():
    # Rename Subtitle Downloaded To the Media File Name for auto-Sync
    pass


if __name__ == "__main__":
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
