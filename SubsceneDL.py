'''Version = 1 (Beta)
Author = Rafay Ghafoor
Email = rafayghafoor@protonmail.com
Date Created = Feb 19, 2017 (Version 1)
Updated = April 10, 2017
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
from time import sleep

real_directory = []
ext = ['.mp4', '.mkv', '.avi', '.flv']


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
                    # Creates a folder of same name as file (excluding file extension)
                    os.mkdir(files.strip(extension))
                    # Moves the file to the new folder
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
    >>> Doctor.Strange.[2016].BrRip.720p.YIFY.mp4
    gets (2016) from the media file.'''
    # Searches for FOUR digits in the movie name, if found returns them.
    yearRegex = re.compile(r'\d{4}')
    searchItems = yearRegex.search(filename)
    return searchItems.group()


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
    '''Searches for movie on Subscene site. If [Name and Year] (Of Movie)
    are matched in the searched results, movie (title) is obtained and searched in.'''
    r = requests.get(search, {'q': parameter})
    print 'Generated URL is ---> %s\n' % r.url
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    found_url = ''
    for movie_name in soup.find_all('div', {'class': 'title'}):
        for search_query in movie_name.find_all('a'):
            search_str = search_query.text.replace(':', '').lower()
            if name.lower() in search_str and year in search_str:
                found_url = search_query.get('href')  # Obtaining First URL
                break
            elif name.lower() not in search_str and year not in search_str:
                continue
        if found_url != '':
            break
    if found_url == '':
        print 'Subtitles Not Found for the Movie (%s).\n' % name.title()
    else:
        # the link returned would be like: https://subscene.com/subtitles/Movie-Name
        return 'https://subscene.com' + found_url


def downlink_finder(page_link, sub_count = 1):
    # Change sub_count argument if you want to download more than
    # 1 subtitle for a movie
    '''Finds download links on the obtained page from [Name Finder] (function).'''
    r = requests.get(page_link)
    sub_list = []   # Subtitles List
    active_sub = 0  # Subtitle Number which is being appended
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    for link in soup.find_all('td', {'class': 'a1'}):
        for eng_link in link.find_all('span', {'class': 'l r positive-icon'}):
            for down_link in link.find_all('a'):
                if active_sub < sub_count:
                    if 'Trailer' not in link.text and 'English' in eng_link.text:
                        if down_link.get('href') not in sub_list:
                            sub_list.append(down_link.get('href'))
                            active_sub += 1
    # For Movie 'Kong Skull Island ["/subtitles/skull-island/english/1525314"]
    # the list is like:- ["/subtitles/Movie-Name/Language/Sub-ID0",
    #                      /subtitles/Movie-Name/Language/Sub-ID1]
    return ['https://subscene.com' + i for i in sub_list]


def zip_extractor(name):
    '''Extracts zip file obtained from the Subscene site (which contains subtitles).'''
    try:
        with zipfile.ZipFile(name, "r") as z:
            z.extractall(".")
        os.remove(name)
    except:
        pass


def downloader(dl_links):
    '''Downloads subtitles for the links obtained from the [Download Link Finder] (function).'''
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


def remove_ext(name):
    '''Removes extension from the movie file name.
    For example:-
    >>> Doctor.Strange.2016.mp4 [INPUT]
    >>> Doctor.Strange.2016 [RETURN]'''
    global ext
    for extension in ext:
        if extension in name:
            return name.replace(extension,'')
            break
    return name


def movie_subdl(mediaName = '', mediaYear = ''):
    '''A function which runs [Name Finder], [Download Link Finder] and
    [Downloader] (functions).'''
    # For Downloading Subtitle For Required Movie
    mediaName = remove_ext(mediaName) # Removes Extension eg. --> .mp4
    parameters = mediaName + ' ' + mediaYear
    parameters = parameters.strip(' ')
    query = name_finder(mediaName, mediaYear, parameters)  # List Of Elements
    if query != None:
        downlinks = downlink_finder(query, 1)
        for elements in downlinks:
            print '[*] - Downloading Subtitle For %s' % (mediaName.title())
            downloader(elements)
            print '[+] - Subtitle Downloaded!\n'


def name_grabber(medialst):
    '''Gets the Movie Name and Year from the filename and other meta
    data is removed.
    For Example:
    >>> Doctor.Strange.2016.720p.BrRip.mkv [INPUT]
    >>> Doctor Strange 2016 [RETURN]
    This is done for obtaining better search result from the subscene site.'''
    nameslist = []
    for movies in medialst:
        try:
            year = get_year(movies)
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
            count = 0
            for folders, subfolders, files in os.walk('.'):
                for elem in files:
                    if name == elem:
                        return folders.replace('./', '')
                        count += 1
                        break
                if count == 1:
                    break


def directory_subdl(movieNames):
    '''Downloads subtitles for the movies contained in directory.'''
    cwd = os.getcwd()
    num = 0
    for elements in movieNames:
        location = file_locator(real_directory[num])
        os.chdir(location)
        try:
            movieYear = get_year(elements)
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
    global ext
    for folders, subfolders, files in os.walk('.'):
        for elements in files:
            if elements.endswith('.srt'):
                for movies in files:
                    for extension in ext:
                        if movies.endswith(extension):
                            directory.remove(movies)
                        else:
                            pass
    return directory


def sub_renamer():
    '''Rename the downloaded subtitles to the movie name for auto-sync with
    media player. For Example:
    >>> Doctor.Strange.2016.720p.BrRip.mp4 [Movie-FileName]
    >>> Doctor Strange 2016 720 BrRip [ENG].srt [Downloaded-SubFile]
    Renames [Downloaded-SubFile] to [Movie-FileName].
    '''
    pass


if __name__ == "__main__":
    makeChoice = int(raw_input("Press [1] - To download subtitles for movies in a directory.\n\
Press [2] - To download subtitles For a custom movie:\n\
Your Input [-]:  "))
    print ''
    search = "https://subscene.com/subtitles/title"
    if makeChoice == 1:
        create_folder()
        '''First runs directory obtainer function and a list of movies is returned
        then on the returned list sub_checker function is returned and a filtered list
        is returned (movies which don't have subtitles already).'''
        newdir = sub_checker(directory_obtainer())
        # Runs name_grabber function first gets the movie names (removes meta data)
        # Then runs directory_subdl function to download subtitles for the movies.
        directory_subdl(name_grabber(newdir))
    elif makeChoice == 2:
        movieName = raw_input('Enter Movie Name: ')
        movieYear = raw_input('Enter Movie Release Year: ')
        movie_subdl(movieName, movieYear)
    else:
        print 'Invalid Choice!'
