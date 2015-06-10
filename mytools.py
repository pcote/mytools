"""
A collection of various tools that act for stuff
I find myself writing a lot.
"""

from importlib import reload
from bs4 import BeautifulSoup
from contextlib import contextmanager
import requests


def nudir(ob):
    """
    No underscore dir command.
    :param ob: The target object for which to do a dir search on.
    :return: a list of dir results sans underscore members
    """
    return [att for att in dir(ob) if not att.startswith("_")]


def fdir(ob, search_term):
    """
    dir command with a find option in it.
    :param search_term:
    :param ob: The object to do a dir lookup on.
    :param search_term: The search term to lookup.
    :return: a list of attrs for object found by search term.
    """
    return [att for att in dir(ob) if search_term in att]


def varkey(ob):
    """
    Shortcut to vars(ob).keys()
    :param ob:
    :return:
    """
    return vars(ob).keys()


def make_empty_data_file(file_name):
    """
    Ensure that an empty file will exist for the data being stored or read.
    :param file_name: name of the file to make.  (.dat is pickle .json is json)
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
    Saves structured data in either json or as pickle dump
    depending on the extension on the file name
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
    write_mode = open_mode + data_mode

    with open(file_name, write_mode) as file_ob:
        dumper.dump(ob_to_save, file_ob)


def loadobject(file_name):
    """
    Load a structured data file into memory as a Python object.
    :param file_name: Name of data file.  If not json , assumed to be pickle.
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


def rest_call(base_url, api_call, *args):
    """
    Simple utility for calling REST-based services.
    Very crude and limited to the following assumptions....
    1.  The api call is GET based.
    2.  The data returned is JSON.
    :param base_url: The base url for the service in question.
    :param api_call: The api call.
    :param args: Any optional args - If used, it assumes api_call arg set up
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
    Convenience function to get a no argument send() function
    out of a generator object
    example usage:
    send = simple_send(mygenerator)
    send() # return next item in that gene by invoking mygen.send(None)

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
    Utility to recursively search a directory,
    find files an extension, and return full paths
    to that file.
    :param directory_name: the file to find.
    :param file_extension: extension to look for
    :return: a gen for files w/ that path. includes path
    """
    import os
    for directory, child_directories, files in os.walk(directory_name):
        for file_name in files:
            if file_name.endswith(file_extension):
                yield "{0}\\{1}".format(directory, file_name)


def convert_to_package(dir_name):
    """
    Take a directory and it's subfolders and add empty __init__.py files
    if none were there before.
    """
    import os
    for dir_path, _, file_names in os.walk(dir_name):
        if "__init__.py" not in file_names:
            new_file_path = "{}/__init__.py".format(dir_path)
            with open(new_file_path, "xt", encoding="utf-8"):
                pass  # Just need to create the file.  That is all.


def dump_dataset(data_set):
    """
    Just take a list of records and dump them out.
    """
    for rec in data_set:
        for col in rec:
            print(col)
        print()


def dump_dict(dct, order=None):
    iter = dct.items()

    if order == "key":
        iter = sorted(iter, key=lambda x: tuple(x)[0])
    if order == "value":
        iter = sorted(iter, key=lambda x: tuple(x)[1])

    for key, val in iter:
        print("{} -> {}".format(key, val))

@contextmanager
def get_db_context():
    """
    Context manager to connect a mysql db using credentials set up.
    Takes care of connection and disconnection to the db on the user's behalf.
    Configuration is done with an ini file called creds.ini which
    sits in a config folder.
    :return: A cursor object.
    """
    import pymysql
    import configparser
    parser = configparser.ConfigParser()
    parser.read("config/creds.ini")
    parser = parser["mysql"]
    conn = pymysql.connect(user=parser["user"], passwd=parser["pw"],
                           database=parser["db"], host=parser["host"])
    conn.set_charset("utf8")
    csr = conn.cursor()

    yield csr

    conn.commit()
    csr.close()
    conn.close()
