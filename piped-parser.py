#!/home/qq/Applications/miniconda3/bin/python

import argparse
import json
import re
import cchardet
from datetime import datetime

import requests


def check_network():
    try:
        # send a request to google.com
        requests.get('https://www.google.com')
        return True
    except:
        return False
    

def parse_piped_feed(data, domain, separator, stdout):
    sub_el = re.compile(r'\|')
    videos = []
    for item in json.loads(data.content):
        author = sub_el.sub('', item.get('uploaderName')).lower()
        title = sub_el.sub('', item.get('title')).lower()
        if stdout:
            upload_time = str(datetime.now() - datetime.fromtimestamp(item.get('uploaded') * 0.001))[:-7]
        else:
            upload_time = str(datetime.fromtimestamp(item.get('uploaded') * 0.001))
        link = domain+item.get('url')
        duration_time = item.get('duration')
        videos.append(separator.join((author,title,duration_time,upload_time,link)))
    return videos


def parse_yt_search(data, domain, separator):
    # это как раз реквест для продолжения фетчинга видосов при скролле, если я правильно понял
    #json_data.get('contents').get('twoColumnSearchResultsRenderer').get('primaryContents').get('sectionListRenderer').get('contents')[1].get('continuationItemRenderer')
    sub_el = re.compile(r'\|')
    videos = []
    # Detect the character encoding of the bytes data
    encoding = cchardet.detect(data.content)['encoding']
    # Decode the bytes to a string using the detected encoding
    str_data = data.content.decode(encoding)

    json_data = re.search('var ytInitialData = ({.*?});', str_data).group(1)
    json_data = json.loads(json_data)

    search_result = json_data.get('contents').get('twoColumnSearchResultsRenderer').get('primaryContents').get('sectionListRenderer').get('contents')[0].get('itemSectionRenderer').get('contents')
    for item in search_result:
        if 'videoRenderer' in item.keys():
            title = item.get('videoRenderer').get('title').get('runs')[0].get('text')
            title = sub_el.sub('', title)
            publish_time = item.get('videoRenderer').get('publishedTimeText').get('simpleText')
            duration_time = item.get('videoRenderer').get('lengthText').get('simpleText')
            video_url = item.get('videoRenderer').get('navigationEndpoint').get('commandMetadata').get('webCommandMetadata').get('url')
            creator_name = item.get('videoRenderer').get('ownerText').get('runs')[0].get('text')
            creator_url = item.get('videoRenderer').get('ownerText').get('runs')[0].get('navigationEndpoint').get('commandMetadata').get('webCommandMetadata').get('url')
            videos.append(separator.join((creator_name,title,duration_time,publish_time,domain+video_url,domain+creator_url)))
        
        elif 'reelShelfRenderer' in item.keys():
            if item.get('reelShelfRenderer').get('title').get('simpleText') == "Shorts":
                continue
            else:
                raise "не shorts в item.get('reelShelfRenderer')"
        
        elif 'shelfRenderer' in item.keys():
            for el in item.get('shelfRenderer').get('content').get('verticalListRenderer').get('items'):
                if el.get('videoRenderer').get('badges'):
                    if 'LIVE' in el.get('videoRenderer').get('badges')[0].get('metadataBadgeRenderer').get('style'):  # live stream
                        continue
                
                title = el.get('videoRenderer').get('title').get('runs')[0].get('text')
                title = sub_el.sub('', title)
                publish_time = el.get('videoRenderer').get('publishedTimeText').get('simpleText')
                duration_time = el.get('videoRenderer').get('lengthText').get('simpleText')
                video_url = el.get('videoRenderer').get('navigationEndpoint').get('commandMetadata').get('webCommandMetadata').get('url')
                creator_name = el.get('videoRenderer').get('ownerText').get('runs')[0].get('text')
                creator_url = el.get('videoRenderer').get('ownerText').get('runs')[0].get('navigationEndpoint').get('commandMetadata').get('webCommandMetadata').get('url')
                videos.append(separator.join((creator_name,title,duration_time,publish_time,domain+video_url,domain+creator_url)))
    return videos


def get_list_of_videos(domain, token, path_to_output=None, separator=" | ", mode='none', stdout=1, append=0, rewrite=0, search_query=''):
    if not check_network():
        print('Maybe problem with network?')
        print('Will read the output file, if was provided.')
        if path_to_output:
            with open(path_to_output, 'r') as f:
                videos = f.read().split('\n')
        return print('\n'.join(videos))

    if mode == 'none':
        return print('Please choose `mode` parameter. You can use: ["feed", "search", "channel"]')
    
    elif mode == 'search':
        search_result = requests.get('https://www.youtube.com/results?search_query='+ search_query)
        list_of_videos = parse_yt_search(search_result, domain, separator, stdout)

    elif mode == 'feed':
        feed = requests.get('https://pipedapi.kavin.rocks/feed?authToken='+token)
        list_of_videos = parse_piped_feed(feed, domain, separator, stdout)
    
    if stdout:
        return print('\n'.join(list_of_videos))
    
    if append:
        with open(path_to_output, 'r') as f:
            old_list_of_videos = f.read().split('\n')
        
        list_of_videos.extend(old_list_of_videos)
        list_of_videos = list(dict.fromkeys(list_of_videos))
        list_of_videos[-1] += '\n'
        
        print(f"Appending to the file: {path_to_output}")
        with open(path_to_output, 'w') as f:
            f.write('\n'.join(list_of_videos))
        return 
    
    if rewrite:
        list_of_videos[-1] += '\n'
        print(f"Rewriting the file: {path_to_output}")
        with open(path_to_output, 'w') as f:
            f.write('\n'.join(list_of_videos))
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain",
                        help="domain of piped to use", required=True)
    parser.add_argument(
        "-m", "--mode", default='none', help="in which mode to run the parser. You can use: ['feed', 'search', 'channel']", required=True)
    parser.add_argument(
        "-q", "--search-query", help="will be used to make a search request via piped")
    parser.add_argument(
        "-t", "--token", help="token to fetch your feed")
    parser.add_argument(
        "-o", "--output", default='/home/qq/.local/share/qq/list-from-feed', help="file for the output")
    parser.add_argument("-s", "--separator", default=' | ',
                        help="which separator to use")
    parser.add_argument("-S", "--stdout", action="store_true",
                        help="pass result to stdout")
    parser.add_argument("-A", "--append", action="store_true",
                        help="appending result to the file")
    parser.add_argument("-R", "--rewrite", action="store_true",
                        help="rewrite the file with result")
    args = parser.parse_args()

    get_list_of_videos(
        domain=args.domain,
        mode=args.mode,
        search_query=args.search_query,
        token=args.token,
        path_to_output=args.output,
        separator=args.separator,
        stdout=args.stdout,
        append=args.append,
        rewrite=args.rewrite
    )
    # get_list_from_feed(
    #     domain='https://piped.kavin.rocks',
    #     token='108ea972-6152-41b0-87ef-7ce71dd2d636',
    #     path_to_output='/home/qq/.local/share/qq/list_from_feed',
    #     # separator,
    #     stdout=0,
    #     append=1,
    #     rewrite=0
    # )