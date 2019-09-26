###############################################################################################################
# Original Author: Jordan Wright
# Modified by: Moez @ CriticalStart
# Version: 1.0
# Usage Example: python pastebin_scraper.py
# Description: This tool monitors Pastebin in real time for data leakage
###############################################################################################################

from lib.Pastebin import Pastebin, PastebinPaste
from time import sleep
from settings import log_file, PRINT_LOG, DB_DUMP_TABLE, DB_DB
import sqlite3
import threading
import logging
import sys


def monitor():
    '''
    monitor() - Main function... creates and starts threads

    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="more verbose", action="store_true")
    args = parser.parse_args()
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    #logging to both stdout and file
    file_handler = logging.FileHandler(log_file)
    handlers = [file_handler]
    if PRINT_LOG:
        stdout_handler = logging.StreamHandler(sys.stdout)
        handlers.append(stdout_handler)
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=handlers
    )


    db_client = sqlite3.connect(DB_DB, check_same_thread=False)

    c = db_client.cursor()
    c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (DB_DUMP_TABLE,))
    if c.fetchone() is None:
        c.execute('''CREATE TABLE %s(
            pk INTEGER PRIMARY KEY,
            text CLOB,
            emails CLOB,
            passwords CLOB,
            num_emails INTEGER,
            num_passwords INTEGER,
            type VARCHAR(10),
            db_keywords FLOAT,
            url VARCHAR(60),
            author VARCHAR(30)
        );''' % (DB_DUMP_TABLE))
    db_client.commit()
    c.close()


    logging.info('Monitoring...')
    paste_lock = threading.Lock()
    db_lock = threading.Lock()

    pastebin_thread = threading.Thread(target=Pastebin().monitor, args=[paste_lock, db_lock, db_client])

    # changed threading to not be in a for loop
    # we're only monitoring one site now - Moe
    pastebin_thread.daemon = True
    pastebin_thread.start()

    # Let threads run
    try:
        while(1):
            sleep(5)
    except KeyboardInterrupt:
        logging.warning('Stopped.')


if __name__ == "__main__":
    # banner
    print("""
    ===================================
    PasteBin Scraper
    Originally created by Jordan Wright
    Modified by Moez @ Critical Start
    Version 1.0
    ===================================
    """)
    sleep(5)
    monitor()
