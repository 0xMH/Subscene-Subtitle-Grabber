import subprocess
import shlex
import json
import shutil
import zipfile
import os
import fnmatch
import requests
import bs4
import re
from time import sleep

func_caller = ''
directory_crawler = 0
real_directories = [
    elements for elements in os.listdir('.') if os.path.isdir(elements) == True
]
real_directories.append(os.getcwd())
site = 'https://subscene.com'
print ''
print('1\t Or\t 2\t Or\t 3\t Or\t anyNUMBER\t\n')
sub_num = int(raw_input('Enter Number Of Subtitles Files To Be Downloaded: '))
print ''
'''Requesting Content For Subtitles
Pages using requests Module'''


def request_Launcher(link, name='', year=''):
    if func_caller == '':
        global directory_crawler
        os.chdir(real_directories[-1])
    print 'Requesting for %s %s\n' % (name.upper(), year)
    r = requests.get(link)
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    found_URL = ''
    '''Obtains First URL of the Search
    Literal on the Webpage (Keyword Searched For). If
    no Url Found found_URL remains empty string.'''
    for link in soup.find_all('div', {'class': 'title'}):
        for nlink in link.find_all('a'):
            if name.strip(year).lower() in nlink.text.replace(':', '').lower() and year in nlink.text.replace(':', '').lower():
                found_URL = nlink.get('href')  # Obtaining First URL
                break
            elif name.lower() not in nlink.text.replace(':', '').lower() and year not in nlink.text.replace(':', '').lower():
                continue
    if found_URL == '':
        os.chdir(real_directories[-1])
        directory_crawler += 1
        print 'Subtitles For (%s) [Not Found]\n' % name
    elif found_URL != '':
        if func_caller == '':
            os.chdir(real_directories[directory_crawler])
        # Site URL + Obtained URL --> https://site.com +
        # /subtitles/name_for_movie
        obt_url = site + found_URL
        r = requests.get(obt_url)  # Scraping the New URL
        soup1 = bs4.BeautifulSoup(r.content, 'html.parser')
        lst = [
        ]  # Creating an Empty List and appending Download Links Of Subtitles To It
        count = 1
        '''Looks For Direct Links Of Subtitles from the page
    	appends them to the list (English Language Subtitles)
    	Count Variable checks for the number of links to be downloaded
    	(Subtitles Number To Be Downloaded)'''
        for links in soup1.find_all('a'):
            for nlinks in links.find_all('span', {'class': 'l r positive-icon'}):
                    if 'English' in nlinks.text and count <= sub_num:
                        if links.get('href') not in lst:
                            lst.append(links.get('href'))
                            count += 1
                    else:
                        continue
        sublist = ['https://subscene.com' + i for i in lst]
        num_of_sub = 1
        for subtitles in sublist:
            if num_of_sub <= sub_num:
                r = requests.get(subtitles)
                soup2 = bs4.BeautifulSoup(r.content, 'html.parser')
                for div in soup2.find_all('div', {'class': 'download'}):
                    for a in div.find_all('a'):
                        url = 'https://subscene.com' + a['href']
                        r = requests.get(url, stream=True)
                        d = r.headers['content-disposition']
                        fname = re.findall("filename=(.+)", d)  # File Name
                        for found_sub in fname:
                            name = found_sub.replace('-', ' ')
                            with open(name, 'wb') as f:
                                for chunk in r.iter_content(
                                        chunk_size=150):
                                    if chunk:
                                        f.write(chunk)
                print 'File Name Generated is ---> %s\n' % name
            num_of_sub += 1
            try:
                with zipfile.ZipFile(name, "r") as z:
                    z.extractall(".")
                os.remove(name)
            except:
                pass
        if func_caller == '':
            os.chdir(real_directories[-1])
            os.chdir(real_directories[directory_crawler + 1])
            directory_crawler += 1
        r.close()
        num_of_sub += 1
    else:
        pass


'''Function for Downloading Subtitles
For all the media contained in a
directory'''


def folder_SubDownload():
    filters = [
        '720p', 'aac', 'hevc', 'mkv', '[', ']', '(', ')', 'brrip', 'x264',
        '1080', 'WEB-DL'
    ]
    directories = os.listdir('.')
    folder_removals = []
    for folders, subfolders, files in os.walk('.'):
        for elements in files:  # Searching Files
            if fnmatch.fnmatch(elements, '*.srt'):
                folder_removals.append(folders)
                folder_removals = [
                    i.replace('./', '') for i in folder_removals
                ]
                folder_removals = [i.replace('.', '') for i in folder_removals]
            elif fnmatch.fnmatch(elements, '*.py'):
                for removal in directories:
                    if removal.endswith('.py'):
                        directories.remove(removal)
            elif fnmatch.fnmatch(elements, '*.srt'):
                for removal in directories:
                    if removal.endswith('.srt'):
                        directories.remove(removal)  # Edited
        # Windows OS 'Removing \ (BackSlash) From Direcory List'
    for elements in folder_removals:
        if '\\' in elements:
            folder_removals = [i.replace('\\', '') for i in folder_removals]
        else:
            break
    for elements in folder_removals:
        if elements in directories:
            directories.remove(elements)
            real_directories.remove(elements)
    for keywords in filters:
        directories = [
            i.replace('.', ' ')
            for i in (movies.lower().replace(keywords.lower(), '')
                      for movies in directories)
        ]
    for elements in directories:
        while '  ' in elements:
            directories = [i.replace('  ', ' ') for i in directories]
            break
    for elements in directories:
        try:
            yearRegex = re.compile(r'\d{4}')
            searchItems = yearRegex.search(elements)
            yearFound = searchItems.group()
            lastalpha = yearFound[-1]
            prev, found, removals = elements.partition(yearFound)
            filters.append(removals)
            for words in filters:
                directories = [
                    i.lower().replace('.', ' ')
                    for i in (movies.lower().replace(words.lower(), '')
                              for movies in directories)
                ]
        except:
            continue
    for elements in directories:
        digitsRegex = re.compile(r'(\d\d\d\d)')
        container = digitsRegex.search(elements)
        try:
            mediaYear = container.group()
        except:
            # If there is no pattern match year (var) is set to Empty String
            mediaYear = ''
            pass
        site_GenURL = elements.strip(mediaYear).replace(
            ' ', '+'
        )  # Name To Be Searched in the URL --> 'site.com/?q=Query+Goes+here'
        if site_GenURL[-1] == '+':
            url = 'https://subscene.com/subtitles/title?q=' + site_GenURL[:
                                                                          -1]  # URL Generated According To Site Format
        else:
            url = 'https://subscene.com/subtitles/title?q=' + site_GenURL
        print 'Searching for url --> %s\n' % url
        # request_Launcher('https://something.com/?q=Movie+Name', 'Movie+Name', 'YEAR')
        request_Launcher(url, elements.strip(mediaYear), mediaYear)


def custom_SubGrabber():
    name = raw_input('Please Enter Subtitles Name:\n')
    site_GenURL = name.replace(
        ' ', '+'
    )  # Name To Be Searched in the URL --> 'site.com/?q=Query+Goes+here'
    year = '(' + raw_input('Please Enter Year!:\n') + ')'
    url = 'https://subscene.com/subtitles/title?q=' + site_GenURL
    request_Launcher(url, name, year)


'''Gets Media File Runtime / Duration
to be searched on IMDB for desired movie
name. For Eg: Johnny English (with no year
provided) will be searched on IMDB with it's
Duration as a search string and year will be obtained
from the matched result.'''


def get_duration(file_path_with_file_name):

    cmd = 'ffprobe -show_entries format=duration -v quiet -of csv="p=0"'
    args = shlex.split(
        cmd)  # Creating a List of the Command and its Parameters
    args.append(
        file_path_with_file_name)  # Appending File to the Arguments list
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobe_output = subprocess.check_output(args).decode('utf-8')

    ffprobe_output = json.loads(ffprobe_output)  # Returns Duration in Seconds
    minutes = ffprobe_output // 60
    hours = minutes // 60
    print 'Hours %s and Minutes %s' % (hours, minutes)


def folderCreator():
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
            break


qs = int(
    raw_input(
        'Press 1 For Creating Folders For Movies\nPress 2 For Downloading Subtitles for movies in a Folder\nPress 3 For Downloading Subtitles for a movie.\n'
    ))

if qs == 1:
    folderCreator()
elif qs == 2:
    folder_SubDownload()
elif qs == 3:
    func_caller += 'Custom'
    custom_SubGrabber()
else:
    print('Wrong Option')
