"""Methods to fetch data from the LoL API."""
import requests
import config
import cache

BASE_URL = "https://{queryRegion}.api.riotgames.com/lol"
REGIONS = {"BR" : "br1", "EUNE" : "eun1", "EUW" : "euw1", "JP" : "jp1",
           "KR" : "kr1", "LAN" : "la1", "LAS" : "la2", "NA" : "na1",
           "OCE": "oc1", "TR" : "tr1", "RU" : "ru", "PBE" : "pbe1"}

def get_account_id(region, summoner_name):
    """Gets the account ID for a given summoner Name."""
    #TODO add cache to method like get_champion_name
    summoner_url = "/summoner/v3/summoners/by-name/{summonername}"
    query = api_key_query()
    url = get_base_url(region) + summoner_url.format(summonername=summoner_name)
    req = request_get(url, params=query)

    if req.status_code == 200: #All OK
        return response_payload(req)["accountId"]

    if req.status_code == 404: #Summoner not found
        raise SummonerNotFoundError("Summoner {summoner} does not exist."
                                    .format(summoner=summoner_name))

    if req.status_code < 500: #Error in the request
        raise RequestError(response_payload(req)["status"]["message"])

    raise ApiError(response_payload(req)["status"]["message"]) #Server error

def get_latest_match(region, account_id):
    """Gets the latest match ID for a given accountID."""
    matches_url = "/match/v3/matchlists/by-account/{accountid}"
    query = api_key_query()
    url = get_base_url(region) + matches_url.format(accountid=account_id)
    req = request_get(url, params=query)

    if req.status_code == 200: #All OK
        return response_payload(req)["matches"][0]["gameId"]

    if req.status_code == 422: #No matches recorded
        raise NoMatchesError("Summoner does not have any matches recorded.")

    if req.status_code < 500: #Error in the request
        raise RequestError(response_payload(req)["status"]["message"])

    raise ApiError(response_payload(req)["status"]["message"]) #Server error

def get_match_data(region, match_id):
    """Gets the match data based on the ID."""
    #TODO add cache to method like get_champion_name
    match_url = "/match/v3/matches/{matchid}"
    query = api_key_query()
    url = get_base_url(region) + match_url.format(matchid=match_id)
    req = request_get(url, params=query)

    if req.status_code == 200:
        return response_payload(req)

    if req.status_code < 500: #Error in the request
        raise RequestError(response_payload(req)["status"]["message"])

    raise ApiError(response_payload(req)["status"]["message"]) #Server error

def get_champion_name(region, champion_id):
    """Gets champion name based on ID."""
    name_from_cache = cache.get_champion_name(champion_id)
    if name_from_cache != "":
        return name_from_cache

    champions_url = "/static-data/v3/champions/{id}"
    query = api_key_query()
    url = get_base_url(region) + champions_url.format(id=champion_id)
    req = request_get(url, params=query)

    if req.status_code == 200: #All OK
        name = response_payload(req)["name"]
        cache.add_champion_name(champion_id, name)
        return name

    if req.status_code < 500: #Error in the request
        raise RequestError(response_payload(req)["status"]["message"])

    raise ApiError(response_payload(req)["status"]["message"]) #Server error

def get_champion_mastery(region, champion_id, summoner_id):
    """Gets the Champion Mastery for a given summoner and champion."""
    mastery_url = "/champion-mastery/v3/champion-masteries/" \
                  "by-summoner/{summonerid}/by-champion/{championid}"
    query = api_key_query()
    url = get_base_url(region) + mastery_url.format(summonerid=summoner_id, championid=champion_id)
    req = request_get(url, params=query)

    if req.status_code == 200: #All OK
        return response_payload(req)["championLevel"]

    if req.status_code < 500: #Error in the request
        raise RequestError(response_payload(req)["status"]["message"])

    raise ApiError(response_payload(req)["status"]["message"]) #Server error

def request_get(url, params):
    """Gets request to the url with given params (separate for mocking purposes)"""
    return requests.get(url, params)

def response_payload(req):
    """Gets the request payload (separate for mocking purposes)"""
    return req.json()

def is_valid_region(region):
    """Identifies if a given region is valid."""
    return region in REGIONS

def get_region_list():
    """Returns the list of regions."""
    return REGIONS.keys()

def get_base_url(region):
    """Forms the base API URL."""
    return BASE_URL.format(queryRegion=REGIONS[region])

def api_key_query():
    """Forms the API Key Query."""
    conf = config.load_from_env()
    return {"api_key" : conf["API_KEY"]}

class SummonerNotFoundError(ValueError):
    """Raise this when the summoner name doesn't exist."""

class NoMatchesError(ValueError):
    """Raise this when the summoner has no ranked matches."""

class ApiError(ValueError):
    """Raise this when an error occurs in the server (500+)."""

class RequestError(ValueError):
    """Raise this when an error occurs in the request (400-499)."""
