#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
File: /workspace/temp_feedback/Temp_Feedback/dataset_collection/crawler/main.py
Project: /workspace/temp_feedback/Temp_Feedback/dataset_collection/crawler
Created Date: Tuesday November 21st 2023
Author: Kaixu Chen
-----
Comment:

Have a good code time :)
-----
Last Modified: Tuesday November 21st 2023 2:07:54 pm
Modified By: the developer formerly known as Kaixu Chen at <chenkaixusan@gmail.com>
-----
Copyright (c) 2023 The University of Tsukuba
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

24-11-2023	Kaixu Chen	the crawler can run successfully, but also have some bugs.
                        
'''


import os, yaml
from typing import Any
import requests
import shutil
from multiprocessing import Pool
import signal
import argparse
from collect_links import CollectLinks
import imghdr
import base64
from pathlib import Path
import random
from pyvirtualdisplay import Display


class Sites:
    GOOGLE = 1
    NAVER = 2
    GOOGLE_FULL = 3
    NAVER_FULL = 4

    @staticmethod
    def get_text(code):
        if code == Sites.GOOGLE:
            return 'google'
        elif code == Sites.NAVER:
            return 'naver'
        elif code == Sites.GOOGLE_FULL:
            return 'google'
        elif code == Sites.NAVER_FULL:
            return 'naver'

    @staticmethod
    def get_face_url(code):
        if code == Sites.GOOGLE or Sites.GOOGLE_FULL:
            return "&tbs=itp:face"
        if code == Sites.NAVER or Sites.NAVER_FULL:
            return "&face=1"


class AutoCrawler:
    def __init__(self, skip_already_exist=True, n_threads=4, do_google=True, do_naver=True, download_path='download',
                 full_resolution=False, face=False, no_gui=False, limit=0, proxy_list=None, keywords_file='keywords.txt'):
        """
        :param skip_already_exist: Skips keyword already downloaded before. This is needed when re-downloading.
        :param n_threads: Number of threads to download.
        :param do_google: Download from google.com (boolean)
        :param do_naver: Download from naver.com (boolean)
        :param download_path: Download folder path
        :param full_resolution: Download full resolution image instead of thumbnails (slow)
        :param face: Face search mode
        :param no_gui: No GUI mode. Acceleration for full_resolution mode.
        :param limit: Maximum count of images to download. (0: infinite)
        :param proxy_list: The proxy list. Every thread will randomly choose one from the list.
        """

        self.skip = skip_already_exist
        self.n_threads = n_threads
        self.do_google = do_google
        self.do_naver = do_naver
        self.download_path = download_path
        self.full_resolution = full_resolution
        self.face = face
        self.no_gui = no_gui
        self.limit = limit
        self.proxy_list = proxy_list if proxy_list and len(proxy_list) > 0 else None
        self.keywords_file = keywords_file

        os.makedirs('{}'.format(self.download_path), exist_ok=True)

    @staticmethod
    def all_dirs(path):
        paths = []
        for dir in os.listdir(path):
            if os.path.isdir(path + '/' + dir):
                paths.append(path + '/' + dir)

        return paths

    @staticmethod
    def all_files(path):
        paths = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if os.path.isfile(path + '/' + file):
                    paths.append(path + '/' + file)

        return paths

    @staticmethod
    def get_extension_from_link(link, default='jpg'):
        splits = str(link).split('.')
        if len(splits) == 0:
            return default
        ext = splits[-1].lower()
        if ext == 'jpg' or ext == 'jpeg':
            return 'jpg'
        elif ext == 'gif':
            return 'gif'
        elif ext == 'png':
            return 'png'
        else:
            return default

    @staticmethod
    def validate_image(path):
        ext = imghdr.what(path)
        if ext == 'jpeg':
            ext = 'jpg'
        return ext  # returns None if not valid

    @staticmethod
    def make_dir(dirname):
        current_path = os.getcwd()
        path = os.path.join(current_path, dirname)
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def get_keywords(keywords_file:str ='keywords.txt'):
        # read search keywords from file
        if keywords_file.endswith('.txt'):
            # * load txt file
            with open(keywords_file, 'r', encoding='utf-8-sig') as f:
                text = f.read()
                lines = text.split('\n')
                lines = filter(lambda x: x != '' and x is not None, lines)
                keywords = sorted(set(lines))
        elif keywords_file.endswith('.yaml'):
            # * load yaml file
            with open(keywords_file, 'r', encoding='utf-8-sig') as f:
                text = yaml.load(f, Loader=yaml.FullLoader)

            group = text.keys()
            lan_group = text['EN'].keys()

        print('{} lans found: {}'.format(len(group), group))
        print('{} group found: {}'.format(len(lan_group), lan_group))

        # re-save sorted keywords
        # with open(keywords_file, 'w+', encoding='utf-8') as f:
        #     for keyword in keywords:
        #         f.write('{}\n'.format(keyword))

        return text
        # return keywords

    @staticmethod
    def save_object_to_file(object, file_path, is_base64=False):
        try:
            with open('{}'.format(file_path), 'wb') as file:
                if is_base64:
                    file.write(object)
                else:
                    shutil.copyfileobj(object.raw, file)
        except Exception as e:
            print('Save failed - {}'.format(e))

    @staticmethod
    def base64_to_object(src):
        header, encoded = str(src).split(',', 1)
        data = base64.decodebytes(bytes(encoded, encoding='utf-8'))
        return data

    def download_images(self, keyword, links, site_name, max_count=0, down_info: list = ['EN', 'spring']):

        down_lan = down_info[0]
        down_class = down_info[1]

        down_class = down_lan + '_' + down_class

        self.make_dir('{}/{}/{}'.format(self.download_path, down_class, keyword.replace('"', '')))
        total = len(links)
        success_count = 0

        if max_count == 0:
            max_count = total

        for index, link in enumerate(links):
            if success_count >= max_count:
                break

            try:
                print('Downloading {} from {}: {} / {}'.format(keyword, site_name, success_count + 1, max_count))

                if str(link).startswith('data:image/jpeg;base64'):
                    response = self.base64_to_object(link)
                    ext = 'jpg'
                    is_base64 = True
                elif str(link).startswith('data:image/png;base64'):
                    response = self.base64_to_object(link)
                    ext = 'png'
                    is_base64 = True
                else:
                    response = requests.get(link, stream=True, timeout=10)
                    ext = self.get_extension_from_link(link)
                    is_base64 = False

                no_ext_path = '{}/{}/{}/{}_{}_{}_{}'.format(self.download_path.replace('"', ''), down_class, keyword, site_name, down_class, keyword.replace(' ', '-'), 
                                                   str(index).zfill(4))
                path = no_ext_path + '.' + ext
                self.save_object_to_file(response, path, is_base64=is_base64)

                success_count += 1
                del response

                ext2 = self.validate_image(path)
                if ext2 is None:
                    print('Unreadable file - {}'.format(link))
                    os.remove(path)
                    success_count -= 1
                else:
                    if ext != ext2:
                        path2 = no_ext_path + '.' + ext2
                        os.rename(path, path2)
                        print('Renamed extension {} -> {}'.format(ext, ext2))

            except KeyboardInterrupt:
                break
                        
            except Exception as e:
                print('Download failed - ', e)
                continue

    def download_from_site(self, keyword, site_code, down_info: list):
        """download images from site, by keyword.
        This function is the main logic for the python crawler.

        Args:
            keyword (dict): the keyword dict, which contains the keyword in different class with detail keywords.
            site_code (int): the site code.
        """ 

        site_name = Sites.get_text(site_code)
        add_url = Sites.get_face_url(site_code) if self.face else ""

        # ! in no gui mode, chromedriver is not initialized in main thread
        try:
            proxy = None
            if self.proxy_list:
                proxy = random.choice(self.proxy_list)
            collect = CollectLinks(no_gui=self.no_gui, proxy=proxy)  # initialize chrome driver
        except Exception as e:
            print('Error occurred while initializing chromedriver - {}'.format(e))
            return

        try:
            print('Collecting links... {} from {}'.format(keyword, site_name))

            if site_code == Sites.GOOGLE:
                links = collect.google(keyword, add_url)

            elif site_code == Sites.NAVER:
                links = collect.naver(keyword, add_url)

            elif site_code == Sites.GOOGLE_FULL:
                links = collect.google_full(keyword, add_url, self.limit)

            elif site_code == Sites.NAVER_FULL:
                links = collect.naver_full(keyword, add_url)

            else:
                print('Invalid Site Code')
                links = []

            print('Downloading images from collected links... {} from {}'.format(keyword, site_name))
            self.download_images(keyword, links, site_name, max_count=self.limit, down_info=down_info)
            Path('{}/{}/{}_done'.format(self.download_path, keyword.replace('"', ''), site_name)).touch()

            print('Done {} : {}'.format(site_name, keyword))

        except Exception as e:
            print('Exception {}:{} - {}'.format(site_name, keyword, e))
            return

    def download(self, args):
        
        self.download_from_site(keyword=args[0], site_code=args[1], down_info=args[2])

    def init_worker(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    def do_crawling(self, keywords: dict, one_class: str, language: str = 'EN'):

        # keywords = self.get_keywords(self.keywords_file)
        keyword_list = keywords.split(' ')

        tasks = []

        down_info = [language, one_class]

        for keyword in keyword_list:
            dir_name = '{}/{}'.format(self.download_path, keyword)
            google_done = os.path.exists(os.path.join(os.getcwd(), dir_name, 'google_done'))
            naver_done = os.path.exists(os.path.join(os.getcwd(), dir_name, 'naver_done'))
            if google_done and naver_done and self.skip:
                print('Skipping done task {}'.format(dir_name))
                continue
            
            keyword = keyword.replace('_', ' ')

            if self.do_google and not google_done:
                if self.full_resolution:
                    tasks.append([keyword, Sites.GOOGLE_FULL, down_info])
                else:
                    tasks.append([keyword, Sites.GOOGLE, down_info])

            if self.do_naver and not naver_done:
                if self.full_resolution:
                    tasks.append([keyword, Sites.NAVER_FULL, down_info])
                else:
                    tasks.append([keyword, Sites.NAVER, down_info])

        try:
            pool = Pool(self.n_threads, initializer=self.init_worker)
            pool.map(self.download, tasks)
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
        else:
            pool.terminate()
            pool.join()
        print('Task ended. Pool join.')

        # FIXME because change the save path, so the imbalance check is not work.
        self.imbalance_check()

        print('End Program')
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        all_keywords = self.get_keywords(self.keywords_file)

        for lan, value in all_keywords.items():

            for one_class in value:

                self.do_crawling(value[one_class], one_class, lan)

                print('Finish {} class in {} language'.format(one_class, lan))



    def imbalance_check(self):
        print('Data imbalance checking...')

        dict_num_files = {}

        for dir in self.all_dirs(self.download_path):
            n_files = len(self.all_files(dir))
            dict_num_files[dir] = n_files

        avg = 0
        for dir, n_files in dict_num_files.items():
            avg += n_files / len(dict_num_files)
            print('dir: {}, file_count: {}'.format(dir, n_files))

        dict_too_small = {}

        for dir, n_files in dict_num_files.items():
            if n_files < avg * 0.5:
                dict_too_small[dir] = n_files

        if len(dict_too_small) >= 1:
            print('Data imbalance detected.')
            print('Below keywords have smaller than 50% of average file count.')
            print('I recommend you to remove these directories and re-download for that keyword.')
            print('_________________________________')
            print('Too small file count directories:')
            for dir, n_files in dict_too_small.items():
                print('dir: {}, file_count: {}'.format(dir, n_files))

            print("Remove directories above? (y/n)")
            answer = input()

            if answer == 'y':
                # removing directories too small files
                print("Removing too small file count directories...")
                for dir, n_files in dict_too_small.items():
                    shutil.rmtree(dir)
                    print('Removed {}'.format(dir))

                print('Now re-run this program to re-download removed files. (with skip_already_exist=True)')
        else:
            print('Data imbalance not detected.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip', type=str, default='true',
                        help='Skips keyword already downloaded before. This is needed when re-downloading.')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads to download.')
    parser.add_argument('--google', type=str, default='true', help='Download from google.com (boolean)')
    parser.add_argument('--naver', type=str, default='false', help='Download from naver.com (boolean)')
    parser.add_argument('--full', type=str, default='false',
                        help='Download full resolution image instead of thumbnails (slow)')
    parser.add_argument('--face', type=str, default='false', help='Face search mode')
    parser.add_argument('--no_gui', type=str, default='auto',
                        help='No GUI mode. Acceleration for full_resolution mode. '
                             'But unstable on thumbnail mode. '
                             'Default: "auto" - false if full=false, true if full=true')
    parser.add_argument('--limit', type=int, default=0,
                        help='Maximum count of images to download per site.')
    parser.add_argument('--proxy-list', type=str, default='',
                        help='The comma separated proxy list like: "socks://127.0.0.1:1080,http://127.0.0.1:1081". '
                             'Every thread will randomly choose one from the list.')
    parser.add_argument('--keywords', type=str, default='/workspace/temp_feedback/Temp_Feedback/dataset_collection/crawler/keywords.yaml',)
    parser.add_argument('--download_path', type=str, default='/workspace/data/download', help='Download folder path')
    args = parser.parse_args()

    _skip = False if str(args.skip).lower() == 'false' else True
    _threads = args.threads
    _google = False if str(args.google).lower() == 'false' else True
    _naver = False if str(args.naver).lower() == 'false' else True
    _full = False if str(args.full).lower() == 'false' else True
    _face = False if str(args.face).lower() == 'false' else True
    _limit = int(args.limit)
    _proxy_list = args.proxy_list.split(',')

    no_gui_input = str(args.no_gui).lower()
    if no_gui_input == 'auto':
        _no_gui = _full
    elif no_gui_input == 'true':
        _no_gui = True
    else:
        _no_gui = False

    print(
        'Options - skip:{}, threads:{}, google:{}, naver:{}, full_resolution:{}, face:{}, no_gui:{}, limit:{}, _proxy_list:{}'
            .format(_skip, _threads, _google, _naver, _full, _face, _no_gui, _limit, _proxy_list))

    display = Display(visible=0, size=(800, 600))
    display.start()
    print('Virtual display started.')

    crawler = AutoCrawler(skip_already_exist=_skip, n_threads=_threads,
                          do_google=_google, do_naver=_naver, full_resolution=_full,
                          face=_face, no_gui=_no_gui, limit=_limit, proxy_list=_proxy_list,
                          keywords_file=args.keywords, download_path=args.download_path)
    crawler()

    display.stop()
    print('Virtual display stopped.')
