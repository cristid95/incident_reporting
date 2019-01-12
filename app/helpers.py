"""This module will encode and parse the query string params."""

from urlparse import parse_qs
import os


def parse_query_params(query_string):
    """
        Function to parse the query parameter string.
        """
    # Parse the query param string
    query_params = dict(parse_qs(query_string))
    # Get the value from the list
    query_params = {k: v[0] for k, v in query_params.items()}
    return query_params


def save_filestorage_object(fs, dirpath, filename):
	if not os.path.isdir(dirpath):
		os.makedirs(dirpath)
	try:
		fs.save(dirpath + filename)
		return True
	except:
		return False


def remove_file(filepath):
	os.remove(filepath)