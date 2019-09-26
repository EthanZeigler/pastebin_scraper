from queue import Queue
import time
from settings import USE_DB, DB_DB, DB_DUMP_TABLE, DB_ACCT_TABLE, REQUEST_SPACING
import logging
from . import helper
import sqlite3
import threading




class Site(object):
    '''
    Site - parent class used for a generic
    'Queue' structure with a few helper methods
    and features. Implements the following methods:

            empty() - Is the Queue empty
            get(): Get the next item in the queue
            put(item): Puts an item in the queue
            tail(): Shows the last item in the queue
            peek(): Shows the next item in the queue
            length(): Returns the length of the queue
            clear(): Clears the queue
            list(): Lists the contents of the Queue
            download(url): Returns the content from the URL

    '''
    # Note from Jordan (original author)
        # I would have used the built-in queue, but there is no support for a peek() method
        # that I could find... So, I decided to implement my own queue with a few
        # changes
    def __init__(self, queue=None):
        if queue is None:
            self.queue = []

    def empty(self):
        return len(self.queue) == 0

    def get(self):
        if not self.empty():
            result = self.queue[0]
            del self.queue[0]
        else:
            result = None
        return result

    def put(self, item):
        self.queue.append(item)

    def peek(self):
        return self.queue[0] if not self.empty() else None

    def tail(self):
        return self.queue[-1] if not self.empty() else None

    def length(self):
        return len(self.queue)

    def clear(self):
        self.queue = []

    def list(self):
        print('\n'.join(url for url in self.queue))

    def monitor(self, t_lock, db_lock, db_client):
        self.update()
        while(1):
            while not self.empty():
                paste = self.get()
                self.ref_id = paste.id
                logging.info('[*] Checking + Spacer ' + paste.url)
                paste.text = self.get_paste_text(paste)
                time.sleep(REQUEST_SPACING)
                interesting = helper.run_match(paste)
                if interesting:
                    logging.info('[*] FOUND ' + (paste.type).upper() + ' ' +  paste.url)
                    if USE_DB:
                        db_lock.acquire()
                        try:
                            cursor =  db_client.cursor()
                            cursor.execute('''INSERT INTO %s (
                                text,
                                emails,
                                hashes,
                                num_emails,
                                num_hashes,
                                type,
                                db_keywords,
                                url,
                                author
                            ) VALUES (
                                ?, ?, ?, ?, ?, ?, ?, ?, ?
                            )''' % (DB_DUMP_TABLE), (paste.text, str(paste.emails), str(paste.hashes), paste.num_emails, paste.num_hashes, paste.type, str(paste.db_keywords), str("https://pastebin.com/"+paste.id), paste.author,))
                        except:
                            logging.info('[*] ERROR: Failed to save paste. Manual review: ' + paste.url)
                        db_lock.release()
            self.update()
            while self.empty():
                logging.debug('[*] No results... sleeping')
                time.sleep(self.sleep)
                self.update()
