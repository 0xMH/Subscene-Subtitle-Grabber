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

def create_folder():
    '''Search for MP4, MKV, AVI extensions inside the current
    directory and If any of the files ending with such
    extensions are found (not in folder), create folder
    for them and paste the respective file in the corresponding
    folder.'''
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


def simple_search():
    '''Takes the name of the file (containing metadata)
    for example:-
    >>> Doctor.Strange.2016.BrRip.720p.YIFY.mp4
    and search the name on subscene site, if subtitle found for
    this name, download subtitles for it. Preffered for (Auto-Sync).'''
    pass


def get_year(filename):
    '''Obtains year from the movie filename.
    For example:-
    >>> Doctor.Strange.2016.BrRip.720p.YIFY.mp4
    gets (2016) from the media file.'''
    yearRegex = re.compile(r'\d{4}')
    searchItems = yearRegex.search(filename)
    year = searchItems.group()
    return year

def get_imdb_year():
    '''If move file doesn't contain year then searches the movie
    on IMDB and obtains year. For better precision, movie runtime
    is obtained and then on IMDB the movie name is searched and if
    the movie runtime matches with the movie (on IMDB), year is obtained.'''
    pass


def get_movie_runtime(moviefile):
    '''Gets Movie Runtime for better search at IMDB site for
    obtaining movie year.'''
    cmd = 'ffprobe -show_entries format=duration -v quiet -of csv="p=0"'
    args = shlex.split(cmd)  # Creating a List of the Command and its Parameters
    args.append(file_path_with_file_name)  # Appending File to the Arguments list
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobe_output = subprocess.check_output(args).decode('utf-8')

    ffprobe_output = json.loads(ffprobe_output)  # Returns Duration in Seconds
    minutes = ffprobe_output // 60
    hours = minutes // 60
    print 'Hours %s and Minutes %s' % (hours, minutes)


def name_finder(name, year, parameter):
    '''Searches for movie on IMDB site. If [Name and Year] (Of Movie)
    are matched on Subscene site, movie (title) is obtained and searched in.'''
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


def downlink_finder(page_link, count = 1):
    '''Finds Download Links on the obtained page from Name Finder (function).'''
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


def zip_extractor(name):
    '''Extracts zip file obtained from the Subscene site (which contains Subtitles)'''
    try:
        with zipfile.ZipFile(name, "r") as z:
            z.extractall(".")
        os.remove(name)
    except:
        pass

def downloader(dl_links):
    '''Downloads Subtitles for the links obtained from the Download Link Finder (function)'''
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
        zip_extractor(name)

def remove_extension(name):
    '''Removes extension from the movie file name.
    For example:-
    >>> Doctor.Strange.2016.mp4
    becomes Doctor.Strange.2016'''
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


def movie_subdl(mediaName = '', mediaYear = ''):
    '''A function which runs Name Finder, Download link Finder and
    Downloader functions.'''
    # For Downloading Subtitle For Required Movie
    mediaName = remove_extension(mediaName) # Removes Extension eg. --> .mp4
    parameters = mediaName + ' ' + mediaYear
    parameters = parameters.strip(' ')
    query = name_finder(mediaName, mediaYear, parameters)  # List Of Elements
    if query != None:
        downlinks = downlink_finder(query, 1)
        for elements in downlinks:
            print '[*] - Downloading Subtitle For %s' % (mediaName + mediaYear)
            downloader(elements)
            print '[+] - Subtitle Downloaded!'


def name_grabber(medialst):
    '''Gets the name of the movies whose subtitles are to be Downloaded.'''
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
    nameslist = [i.strip(' ') for i in nameslist]
    return nameslist


def directory_obtainer():
    '''Gets movies names contained in a directory.'''
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


def file_locator(name):
    '''Locates the file for moving the downloading subtitles to the
    right place.'''
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


def directory_subdl(movieNames, movieDirectory):
    '''Downloads Subtitles for the Directory.'''
    # For Downloading Subtitles for movies in a Directory
    cwd = os.getcwd()
    num = 0
    for elements in movieNames:
        # os.chdir(elements)
        location = file_locator(real_directory[num])
        os.chdir(location)
        try:
            yearRegex = re.compile(r'\d{4}')
            searchItems = yearRegex.search(movies)
            movieYear = searchItems.group()
        except:
            movieYear = ''
        movie_subdl(elements, movieYear)
        os.chdir(cwd)
        if num != len(real_directory) - 1:
            num += 1
        else:
            break


def sub_checker(directory):
    '''Checks for the subtitles if they are already in the movie folder, it
    skips the movie.'''
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



def sub_renamer():
    '''Rename the downloaded subtitles to the movie name for auto-sync with
    media player.'''
    pass


if __name__ == "__main__":
    makeChoice = int(raw_input("Press [1] - For Downloading Subtitles in A Directory.\n\
Press [2] - For Download Subtitles For a Custom Movie:\n\
Your Input [-]:  "))
    search = "https://subscene.com/subtitles/title"
    if makeChoice == 1:
        create_folder()
        real_directory = directory_obtainer()
        newdir = sub_checker(real_directory)
        names = name_grabber(newdir)
        directory_subdl(names, newdir)
    elif makeChoice == 2:
        movieName = raw_input('Enter Movie Name: ')
        movieYear = raw_input('Enter Movie Release Year: ')
        movie_subdl(movieName, movieYear)
    else:
        print 'Invalid Choice!'
