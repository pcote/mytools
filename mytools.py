"""
A collection of various tools that act for stuff
I find myself writing a lot.
"""

from importlib import reload
from bs4 import BeautifulSoup
from contextlib import contextmanager

def nudir(ob):
    """
    No underscore dir command.
    :param ob:
    :return:
    """
    return [att for att in dir(ob) if not att.startswith("_")]


def fdir(ob, search_term):
    """
    dir command with a find option in it.
    :param search_term:
    :param ob: The object to do a dir lookup on.
    :param search_term: The search term to lookup.
    :return: a list of attributes for the object which are found by the search term.
    """
    return [att for att in dir(ob) if search_term in att]


def varkey(ob):
    """
    Shortcut to vars(ob).keys()
    :param ob:
    :return:
    """
    return vars(ob).keys()


def randomsleep(func):
    """
    Intentionally delays return of a function for a random number of seconds.
    :param func:
    :return:
    """
    from functools import wraps
    from time import sleep

    @wraps(func)
    def wrapped_func(*args):
        result = func(*args)
        random = get_randomizer()
        MINTIME, MAXTIME = 3, 8
        sleep_time = random.randrange(MINTIME, MAXTIME)
        print("CALLED {0} WITH ARGS {1} SLEEPING {2} seconds".format(func.__name__, str(args), sleep_time))
        sleep(sleep_time)
        return result
    return wrapped_func


def download_html_files(list_of_links, target_folder):
    """
    Downloads the files associated with a list of links to
    a local folder.
    note: There is an intentional random delay between downloads so as not to do rapid fire hammering of the
    target server.
    :param list_of_links: URL addresses to the intended files.
    :param target_folder: The path to the local folder to save files to
    :return: Nothing.
    """
    import re

    def _setup_file_path(lnk):

        new_file_name = lnk.split("/")[-1]
        file_extension_match = r"\.\w+"
        if re.search(file_extension_match, lnk ):
            new_file_name = re.sub(file_extension_match, "", new_file_name)

        new_file_name += ".html"

        return "{0}/{1}".format(target_folder, new_file_name)


    @randomsleep
    def _download(lnk, target_path):
        import requests
        import os

        res = requests.get(lnk)
        raw_data = res.text
        file_mode = "wt" if os.path.exists(target_folder) else "xt"
        with open(target_path, file_mode, encoding="utf-8") as file_ob:
            file_ob.write(raw_data)


    for link in list_of_links:
        targ_path = _setup_file_path(link)
        _download(link, targ_path)


def make_empty_data_file(file_name):
    """
    Ensure that an empty file will exist for the data being stored or read.
    :param file_name: name of the file to make.  Should end in dat for a pickle or json for json.
    :return: Nothing.
    """
    import json
    import pickle
    if file_name.endswith(".json"):
        file_ob = open(file_name, "xt")
        json.dump([], file_ob)

    if file_name.endswith(".dat"):
        file_ob = open(file_name, "xb")
        pickle.dump([], file_ob)

    file_ob.flush()
    file_ob.close()


def saveobject(ob_to_save, file_name):
    """
    Saves structured data in either json or as pickle dump depending on the extension on the file name
    :param ob_to_save: The python object to save (presumedly serializable)
    :param file_name: The name of the file (including path) to save it to.
    :return: Nothing
    """
    import json
    import pickle
    import os

    dumper = json if file_name.endswith(".json") else pickle

    open_mode = "w" if os.path.exists(file_name) else "x"
    data_mode = "t" if file_name.endswith(".json") else "b"
    write_mode =  open_mode + data_mode

    with open(file_name, write_mode) as file_ob:
        dumper.dump(ob_to_save, file_ob)


def loadobject(file_name):
    """
    Load a structured data file into memory as a Python object.
    :param file_name: Name of the data file.  If not a json file, assumed to be a pickle file.
    :return: Object containing the file data.
    """
    import json
    import pickle

    if file_name.endswith(".json"):
        loader, data_read_mode = json, "rt"
    else:
        loader, data_read_mode = pickle, "rb"

    with open(file_name, data_read_mode) as file_ob:
        ob = loader.load(file_ob)
    return ob


def make_soup(fname):
    """
    Create a simple beautiful soup object out of the filename
    """
    with open(fname, "rt", encoding="utf-8") as file_ob:
        soup = BeautifulSoup(file_ob)
        return soup


def soup_line(dir_name, *exclusions):
    """
    Make pairs of soups and the names of the files they came from.
    :param dir_name: The name of the directory that has the html files needed.
    :param exclusions: Any exclusions that should NOT be considered within that directory.
    :return: A tuple containing the soup object and the name of the file used to create it.
    """
    import os

    from collections import namedtuple
    SoupFilePair = namedtuple("SoupFileName", ["soup", "file_name"])
    is_valid_file = lambda fpath: os.path.isfile(fpath) and fpath.endswith(".html") and fpath not in exclusions

    for fname in os.listdir(dir_name):
        file_path = "{0}/{1}".format(dir_name, fname)
        if is_valid_file(file_path):
            file_ob = open(file_path, "rt", encoding="utf-8")
            soup = BeautifulSoup(file_ob.read().strip())
            yield SoupFilePair(soup, fname)


def rest_call(base_url, api_call, *args):
    """
    Simple utility for calling REST-based services.
    Very crude and limited to the following assumptions....
    1.  The api call is GET based.
    2.  The data returned is JSON.
    :param base_url: The base url for the service in question.
    :param api_call: The api call.
    :param args: Any optional arguments - If used, it assume that the api_call argument is set up
    for Python string parameters.
    :return: A JSON object containing the response to the call.
    """
    import requests
    import json
    api_call = api_call.format(*args)
    full_url = base_url + "/" + api_call
    return json.loads(requests.get(full_url).text)


def simple_send(gen):
    """
    Convenience function to get a no argument send() function out of a generator object
    example usage:
    send = simple_send(mygenerator)
    send() # returns next item in that generator by invoking mygenerator.send(None)

    A convenience function intended for usage within a repl.
    :param gen: A generator object
    :return: A send function that can be invoked directly without args.
    """
    from functools import partial
    send = partial(gen.send, None)
    return send


def get_randomizer():
    """
    Create a simple standard randomizer object seeded by current time.
    :return: a randomizer object.
    """
    import time
    import random
    rand = random.Random()
    rand.seed(time.time())
    return rand


def extension_finder(directory_name, file_extension):
    """
    Utility to recursively search a directory, find files an extension, and return full paths
    to that file.
    :param directory_name: the file to find.
    :param file_extension: extension to look for
    :return: a generator for all files of that extension complete with path to it.
    """
    import os
    for directory, child_directories, files in os.walk(directory_name):
        for file_name in files:
            if file_name.endswith(file_extension):
                yield "{0}\\{1}".format(directory, file_name)


def convert_to_package(dir_name):
    """
    Take a directory and it's subfolders and add empty __init__.py files if none were there before.
    """
    import os
    for dir_path, _, file_names in os.walk(dir_name):
        if "__init__.py" not in file_names:
            new_file_path = "{}/__init__.py".format(dir_path)
            with open(new_file_path, "xt", encoding="utf-8"):
                pass # Just need to create the file.  That is all.


@contextmanager
def get_db_context():
    """
    Context manager for connecting to a mysql database using credentials set up.
    Takes care of connection and disconnection to the db on the user's behalf.
    Configuration is done with an ini file called creds.ini which sits in a config folder.
    :return: A cursor object.
    """
    import pymysql
    import configparser
    parser = configparser.ConfigParser()
    parser.read("config/creds.ini")
    parser = parser["mysql"]
    conn = pymysql.connect(user=parser["user"], passwd=parser["pw"], database=parser["db"], host=parser["host"])
    conn.set_charset("utf8")
    csr = conn.cursor()

    yield csr

    conn.commit()
    csr.close()
    conn.close()