# !/usr/bin/python

import getopt
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
import validators
from requests.adapters import HTTPAdapter, Retry

# logger settings
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger().setLevel(logging.INFO)

# This will get the name of this file
script_name = os.path.basename(__file__)

# settings for threads and requests
MAX_THREADS = 100
MAX_RETRY_FOR_SESSION = 5
BACK_OFF_FACTOR = 0.5
SPECIAL_ERROR_CODES = [403, 404]
ERROR_CODES = tuple(code for code in requests.status_codes._codes if code >= 400 and code not in SPECIAL_ERROR_CODES)


help_message = f"""
    {script_name} -i <input_file> -d <download_directory>

    Downloads a list of URLs from a simple text file into a specified directory.

    -i input_file
    --ifile input_file
        Required - it is the file containing URLs to download.

    -d download_directory
    --directory download_directory
        Required - it is the directory for download destination.

    -h 
    --help 
        print this message

"""


def print_help():
    logging.info(help_message)


class RequiredOptions:
    """Just something to keep track of required options"""

    def __init__(self, options=[]):

        self.required_options = options

    def add(self, option):

        if option not in self.required_options:
            self.required_options.append(option)

    def resolve(self, option):

        if option in self.required_options:
            self.required_options.remove(option)

    def options_resolved(self):
        if len(self.required_options):
            return False
        else:
            return True


def progress_indicator(future):
    sys.stdout.write(".")
    sys.stdout.flush()


def download(
    url,
    retries=MAX_RETRY_FOR_SESSION,
    back_off_factor=BACK_OFF_FACTOR,
    status_force_list=ERROR_CODES,
    session=None,
):
    if not validators.url(url):
        logging.error(f"The following line is not a valid URL: {url}")
        return
    try:
        retry = Retry(
            total=retries,
            backoff_factor=back_off_factor,
            status_forcelist=status_force_list,
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))
        session.mount("http://", HTTPAdapter(max_retries=retry))
        response = session.get(url)
    except requests.exceptions.ConnectionError:
        logging.error(f"The following URL returns Connection error: {url}")
        return

    if response.status_code in SPECIAL_ERROR_CODES:
        logging.error(f"{response.status_code} for: {url}")
        return

    file_name = url.rsplit("/", 1)[1]
    with open(str(file_name), "wb") as f:
        f.write(response.content)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:d:", ["help", "ifile=", "directory="])
    except getopt.GetoptError as e:
        print_help()
        logging.error(e.msg)
        sys.exit(2)

    input_file = ""
    directory = ""
    required_options = RequiredOptions(["ifile", "directory"])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit(0)
        elif opt in ("-i", "--ifile"):
            input_file = arg
            required_options.resolve("ifile")
        elif opt in ("-d", "--directory"):
            directory = arg
            required_options.resolve("directory")
        else:
            print_help()

    # Verify that all the required options have been specified
    if not required_options.options_resolved():
        print_help()
        logging.error(
            "The following required options were not specified:"
            + " ".join(required_options.required_options)
        )
        sys.exit(1)

    # check if file or directory exist
    if not os.path.exists(input_file) or not os.path.exists(directory):
        print_help()
        logging.error("Input file or download directory don't exist")
        sys.exit(1)

    with open(input_file, "r") as f:
        urls = f.read().splitlines()

    # start MAX_THREADS threads for every URL and proceed teh download
    try:
        session = requests.Session()
        with ThreadPoolExecutor(MAX_THREADS) as executor:
            futures = [executor.submit(download, url, session=session) for url in urls]
            for future in futures:
                future.add_done_callback(progress_indicator)
    except KeyboardInterrupt:
        sys.stdout.write("Stopping queued downloads!")
        # cancel_futures=True in python 3.9
        executor.shutdown(wait=False)


if __name__ == "__main__":
    main(sys.argv[1:])
