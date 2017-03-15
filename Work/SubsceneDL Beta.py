import shutil
import zipfile
import re
import requests
import bs4
import os
import fnmatch

real_directory = []

def urlGenerator(name, year = ''):
    # Generates Url for Site
    if year != '':
        return search + name.replace(' ', '+') + '+' + year
    else:
        if name[-1] == ' ':
            return search + name.replace(' ', '+')[:-1]
        else:
            return search + name.replace(' ', '+')


def movieTitleFinder(link):
    # Gets Movie Subtitle Name
    pass


def downloadStatus():
    # Progress Bar For Subtitles Completion!
    pass

def imdbYearObtainer():
    # If there is no Year in the Movie Name File, Get the Year From Imdb by checking the Runtime of the movie
    pass


def getMovieRuntime():
    # Obtains movie Runtime For Cross-Check from IMDB i.e. Obtaining Movie Year
    pass


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

def movieSubDL(mediaName, mediaYear = ''):
    # For Downloading Subtitle For Required Movie
    mediaName = mediaName[:-4] # Removes Extension eg. --> .mp4
    firstUrl = urlGenerator(mediaName, mediaYear)
    print 'Search URL is ', firstUrl
    query = nameFinder(mediaName, mediaYear, firstUrl)  # List Of Elements
    print 'Query is ', query
    downlinks = downLinkFinder(query, 3)
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


def directorySubDL(movieNames, movieDirectory):
    # For Downloading Subtitles for movies in a Directory
    for elements in movieNames:
        movieSubDL(elements)


def subChecker(directory):
    for folders, subfolders, files in os.walk(directory):
        for elements in files:
            if fnmatch.fnmatch(elements, '*.srt'):
                print folders.replace('./', '')
            elif fnmatch.fnmatch(elements, '*.py'):
                print folders.replace('./', '')


def subRenamer():
    # Rename Subtitle Downloaded To the Media File Name for auto-Sync
    pass

if __name__ == "__main__":
    search = "https://subscene.com/subtitles/title?q="
    real_directory = directoryObtainer()
    names = nameGrabber(real_directory)
    directorySubDL(names, real_directory)
    # movieName = raw_input('Enter Movie Name: ')
    # movieYear = raw_input('Enter Movie Release Year: ')
    # movieSubDL(movieName, movieYear)
