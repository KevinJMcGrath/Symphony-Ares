# http://skipperkongen.dk/2016/09/09/easy-parallel-http-requests-with-python-and-asyncio/
import asyncio
import concurrent.futures
import requests
from urllib.parse import quote

import modules.botlog as log

search_index: int = 0


def QuerkSearch(searchTerm: str, searchTerm_dash: str = None, searchTerm_underscore: str = None):
    global search_index
    search_index = 0

    encoded_search_terms = []
    st_enc = quote(searchTerm)
    encoded_search_terms.append(st_enc)

    if searchTerm_dash is not None:
        st_d_enc = quote(searchTerm_dash)
        encoded_search_terms.append(st_d_enc)

    if searchTerm_underscore is not None:
        st_u_enc = quote(searchTerm_underscore)
        encoded_search_terms.append(st_u_enc)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(BuildSearchRequests(encoded_search_terms))


def BuildSearchRequests(searchTerms):
    taskList = []

    for term in searchTerms:
        taskList.append(asyncio.Task(SearchWikipedia(term)))

    # The * operator in this context is for "unpacking". It turns the list
    # into a tuple of discrete elements
    yield from asyncio.gather(*taskList)


def LogSearchStart(engine: str, search: str):
    global search_index
    search_index += 1

    log.LogConsoleInfo("(" + str(search_index) + ") Searching " + engine + " for " + search)

    return search_index


def LogSearchEnd(s_index: int):
    log.LogConsoleInfo("(" + str(s_index) + ") Search Complete.")


async def SearchWikipedia(search: str):
    current_search_index = LogSearchStart("Wikipedia", search)

    # searchep =

    LogSearchEnd(current_search_index)


