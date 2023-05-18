import argparse
import json
import re
from datetime import datetime
import requests


api_dict = {
    "watch.whatever.social": "watchapi.whatever.social",
    "piped.kavin.rocks": "pipedapi.kavin.rocks"
}


class RequestError(Exception):
    pass


def check_network():
    try:
        # send a request to google.com
        requests.get('https://www.google.com')
        return True
    except:
        return False
    

def ckeck_answer(func):
    def wrapper(*args, **kwargs):
        answer = args[0] if args else kwargs.get('data')
        if answer.status_code != 200:
            raise RequestError('Get from request:code={}\nanswer={}'.format(answer.status_code, str(answer.content)))
        return func(*args, **kwargs)
    return wrapper


@ckeck_answer
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
        duration_time = str(item.get('duration') / 60)
        videos.append(separator.join((author,title,duration_time,upload_time,link)))
    return videos


@ckeck_answer
def parse_piped_search(data, domain, separator, stdout):
    # это как раз реквест для продолжения фетчинга видосов при скролле, если я правильно понял
    sub_el = re.compile(r'\|')
    videos = []
    for item in json.loads(data.content).get('items'):
        author = sub_el.sub('', item.get('uploaderName')).lower()
        title = sub_el.sub('', item.get('title')).lower()
        if stdout:
            upload_time = str(datetime.now() - datetime.fromtimestamp(item.get('uploaded') * 0.001))[:-7]
        else:
            upload_time = str(datetime.fromtimestamp(item.get('uploaded') * 0.001))
        link = domain+item.get('url')
        duration_time = str(item.get('duration') / 60)
        videos.append(separator.join((author,title,duration_time,upload_time,link)))
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
        search_results = requests.get(f'https://{api_dict.get(domain)}/search?q={search_query}&filter=all')
        list_of_videos = parse_piped_search(search_results, domain, separator, stdout)

    elif mode == 'feed':
        if not token:
            token = input('Write your token in piped\n>')
        feed_data = requests.get(f'https://{api_dict.get(domain)}/feed?authToken=' + token)
        list_of_videos = parse_piped_feed(feed_data, domain, separator, stdout)
    
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
    parser.add_argument(
        "-d", "--domain",
        choices=['watch.whatever.social', 'piped.kavin.rocks'],
        help="domain of piped to use",
        required=True,
    )
    parser.add_argument(
        "-m", "--mode", 
        choices=['feed', 'search'],
        help="in which mode to run the parser. You can use: ['feed', 'search', 'channel']. 'channel' option in work", 
        required=True
    )
    parser.add_argument(
        "-q", "--search-query", 
        help="will be used to make a search request via piped"
    )
    parser.add_argument(
        "-t", "--token", help="token to fetch your feed from piped")
    parser.add_argument(
        "-o", "--output", 
        default='/home/qq/.local/share/qq/list-from-feed', 
        help="file for the output"
    )
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
