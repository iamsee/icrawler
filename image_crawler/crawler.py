# -*- coding: utf-8 -*-

from .downloader import Downloader
from .feeder import Feeder
import logging
import os
from .parser import Parser
import queue
import requests
import sys
import threading


class ImageCrawler(object):
    """
    Base class for image crawlers

    This class contains basic interfaces for image crawls
    and can only be inherited.

    """

    def __init__(self, img_dir='images', feeder_cls=Feeder, parser_cls=Parser,
                 downloader_cls=Downloader, log_level=logging.INFO):
        self.img_dir = img_dir
        if not os.path.isdir(img_dir):
            os.makedirs(img_dir)
        # init queues
        self.url_queue = queue.Queue()
        self.task_queue = queue.Queue()
        # set session
        self.set_session()
        # set feeder, parser and downloader
        self.feeder = feeder_cls(self.url_queue, self.session)
        self.parser = parser_cls(self.url_queue, self.task_queue, self.session)
        self.downloader = downloader_cls(self.img_dir, self.task_queue, self.session)
        # set logger
        self.set_logger(log_level)

    def set_session(self, headers=None):
        if headers is None:
            self.headers = {
                'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X '
                               '10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/48.0.2564.116 Safari/537.36')
            }
        else:
            self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def set_logger(self, log_level):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',
                            level=log_level, stream=sys.stderr)
        self.logger = logging.getLogger(__name__)

    def crawl(self, feeder_thread_num=1, parser_thread_num=1,
              downloader_thread_num=1, feeder_kwargs={}, parser_kwargs={},
              downloader_kwargs={}):
        self.logger.info('start crawling...')
        self.feeder.start(feeder_thread_num, **feeder_kwargs)
        self.logger.info('feeder started')
        self.parser.start(parser_thread_num, **parser_kwargs)
        self.logger.info('parser started')
        self.downloader.start(downloader_thread_num, **downloader_kwargs)
        while True:
            if threading.active_count() > 1:
                pass
            else:
                break
        self.logger.info('All images downloaded!')
