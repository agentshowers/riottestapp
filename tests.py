"""Unit tests for backend."""
import unittest
import json
import src.app
import src.LoL

VALID_REGION = "validRegion"
VALID_SUMMONER_NAME = "validSummoner"
VALID_SUMMONER_ID = 1
NO_GAMES_SUMMONER_NAME = "noGamesSummoner"
NO_GAMES_SUMMONER_ID = 2
INVALID_MATCH_SUMMONER_NAME = "invalidMatchSummoner"
INVALID_MATCH_SUMMONER_ID = 3
INVALID_MATCH_ID = 1
VALID_MATCH_ID = 3296743698L

def mock_is_valid_region(region):
    """Mocks LoL.is_valid_region"""
    if region == VALID_REGION:
        return True
    return False

def mock_get_account_id(region, summoner_name):
    """Mocks LoL.get_account_id"""
    if summoner_name == VALID_SUMMONER_NAME:
        return VALID_SUMMONER_ID
    elif summoner_name == NO_GAMES_SUMMONER_NAME:
        return NO_GAMES_SUMMONER_ID
    elif summoner_name == INVALID_MATCH_SUMMONER_NAME:
        return INVALID_MATCH_SUMMONER_ID
    raise src.LoL.SummonerNotFoundError("Summoner {summoner} does not exist."
                                        .format(summoner=summoner_name))

def mock_get_latest_match(region, account_id):
    """Mocks LoL.get_latest_match"""
    if account_id == VALID_SUMMONER_ID:
        return VALID_MATCH_ID
    if account_id == INVALID_MATCH_SUMMONER_ID:
        return INVALID_MATCH_ID
    raise src.LoL.NoMatchesError("Summoner does not have any matches recorded.")

def mock_get_match_data(region, match_id):
    """Mocks LoL.get_match_data"""
    if match_id == VALID_MATCH_ID:
        with open("mocks\\mockmatch.json", "r") as myfile:
            data = myfile.read()
            return json.loads(data)
    raise src.LoL.ApiError("Match does not exist")

def mock_get_champion_name(region, champion_id):
    """Mocks LoL.get_champion_name"""
    names = {"4" : "Twisted Fate", "78" : "Poppy", "120" : "Hecarim",
             "143" : "Zyra", "245" : "Ekko", "51" : "Caitlyn",
             "222" : "Jynx", "11" : "Master Yi", "53" : "Blitzcrank",
             "92" : "Riven"}
    return names[str(champion_id)]

def mock_get_champion_mastery(region, champion_id, summoner_id):
    """Mocks LoL.get_champion_mastery"""
    masteries = {"4" : 2, "78" : 3, "120" : 3, "143" : 3, "245" : 4,
                 "51" : 5, "222" : 5, "11" : 6, "53" : 6, "92" : 6}
    return masteries[str(champion_id)]

class APITests(unittest.TestCase):
    """Tests the exposed API."""

    def setUp(self):
        self.old_is_valid_region = src.LoL.is_valid_region
        src.LoL.is_valid_region = mock_is_valid_region
        self.old_get_account_id = src.LoL.get_account_id
        src.LoL.get_account_id = mock_get_account_id
        self.old_get_latest_match = src.LoL.get_latest_match
        src.LoL.get_latest_match = mock_get_latest_match
        self.old_get_match_data = src.LoL.get_match_data
        src.LoL.get_match_data = mock_get_match_data
        self.old_get_champion_mastery = src.LoL.get_champion_mastery
        src.LoL.get_champion_mastery = mock_get_champion_mastery
        self.old_get_champion_name = src.LoL.get_champion_name
        src.LoL.get_champion_name = mock_get_champion_name

    def tearDown(self):
        src.LoL.is_valid_region = self.old_is_valid_region
        src.LoL.get_account_id = self.old_get_account_id
        src.LoL.get_latest_match = self.old_get_latest_match
        src.LoL.get_match_data = self.old_get_match_data
        src.LoL.get_champion_mastery = self.old_get_champion_mastery
        src.LoL.get_champion_name = self.old_get_champion_name

    def test_empty_region(self):
        """Validates if no region returns an error"""
        with self.assertRaises(src.app.APIError) as raised:
            src.app.get_game_data("", "someSummoner")
        self.assertIn("Region parameter is mandatory", raised.exception.message)
        self.assertEqual(raised.exception.status_code, 400)

    def test_empty_summoner(self):
        """Validates if no summoner returns an error"""
        with self.assertRaises(src.app.APIError) as raised:
            src.app.get_game_data("someRegion", "")
        self.assertIn("Summoner parameter is mandatory", raised.exception.message)
        self.assertEqual(raised.exception.status_code, 400)

    def test_invalid_region(self):
        """Validates if invalid returns an error"""
        with self.assertRaises(src.app.APIError) as raised:
            src.app.get_game_data("invalidRegion", VALID_SUMMONER_NAME)
        self.assertIn("'invalidRegion' is not a valid region", raised.exception.message)
        self.assertEqual(raised.exception.status_code, 404)

    def test_invalid_summoner(self):
        """Validates if non existing summoner returns an error"""
        with self.assertRaises(src.app.APIError) as raised:
            src.app.get_game_data(VALID_REGION, "invalidSummoner")
        self.assertIn("Summoner invalidSummoner does not exist", raised.exception.message)
        self.assertEqual(raised.exception.status_code, 404)

    def test_player_with_no_matches(self):
        """Validates if player with no matches returns an error"""
        with self.assertRaises(src.app.APIError) as raised:
            src.app.get_game_data(VALID_REGION, NO_GAMES_SUMMONER_NAME)
        self.assertIn("Summoner does not have any matches recorded", raised.exception.message)
        self.assertEqual(raised.exception.status_code, 404)

    def test_player_with_invalid_match(self):
        """Validates if invalid match id returns an error"""
        with self.assertRaises(src.app.APIError) as raised:
            src.app.get_game_data(VALID_REGION, INVALID_MATCH_SUMMONER_NAME)
        self.assertIn("Match does not exist", raised.exception.message)
        self.assertEqual(raised.exception.status_code, 500)

    def test_valid_response(self):
        """Validates if good response is as expected (sorted and with correct values)"""
        with open("mocks\\mockresponse.json", "r") as myfile:
            expected_result = myfile.read()
            obtained_result = src.app.get_game_data(VALID_REGION, VALID_SUMMONER_NAME)
            self.assertEqual(expected_result, obtained_result)

CHAMPION_ID_FRESH = 11111
CHAMPION_ID_NONCACHE = 22222
CHAMPION_NAME_FRESH = "Fresh"
CHAMPION_NAME_FRESH_NO_CACHE = "SomethingsWrong"
CHAMPION_NAME_NONCACHE = "NonCache"
CHAMPION_NAME_INVALID = "Invalid"

def mock_cache_get_champion_name(champion_id):
    """Mocks cache.get_champion_name"""
    if champion_id == CHAMPION_ID_FRESH:
        return CHAMPION_NAME_FRESH
    return CHAMPION_NAME_NONCACHE

def mock_cache_add_champion_name(champion_id, champion_name):
    """Mocks cache.add_champion_name"""
    #Should do nothing

def mock_api_key_query():
    """Mocks LoL.api_key_query"""
    return {"api_key" : "LoremIpsum"}

def mock_get_base_url(region):
    """Mocks LoL.get_base_url"""
    return region + ".com"

def mock_requests_get(url, params):
    """Mocks requests.get"""
    if CHAMPION_ID_FRESH in url:
        payload = CHAMPION_NAME_FRESH_NO_CACHE
    elif CHAMPION_ID_NONCACHE in url:
        payload = CHAMPION_NAME_NONCACHE
    else:
        payload = CHAMPION_NAME_INVALID
    return {"status_code" : 200, "payload" : payload}

def mock_response_payload(req):
    """Mocks LoL.response_payload"""
    return req["payload"]

class CacheTests(unittest.TestCase):
    """Tests the cache of champions for rate limit"""

    def setUp(self):
        self.old_get_champion_name = src.cache.get_champion_name
        src.cache.get_champion_name = mock_cache_get_champion_name
        self.old_add_champion_name = src.cache.add_champion_name
        src.cache.add_champion_name = mock_cache_add_champion_name
        self.old_api_key_query = src.LoL.api_key_query
        src.LoL.api_key_query = mock_api_key_query
        self.old_get_base_url = src.LoL.get_base_url
        src.LoL.get_base_url = mock_get_base_url
        self.old_request_get = src.LoL.request_get
        src.LoL.request_get = mock_requests_get
        self.old_response_payload = src.LoL.response_payload
        src.LoL.response_payload = mock_response_payload

    def tearDown(self):
        src.cache.get_champion_name = self.old_get_champion_name
        src.cache.add_champion_name = self.old_add_champion_name
        src.LoL.api_key_query = self.old_api_key_query
        src.LoL.get_base_url = self.old_get_base_url
        src.LoL.request_get = self.old_request_get
        src.LoL.response_payload = self.old_response_payload

    def test_champion_in_cache(self):
        """Tests that champion name in cache doesn't trigger request"""
        name = src.LoL.get_champion_name("", CHAMPION_ID_FRESH)
        self.assertEqual(CHAMPION_NAME_FRESH, name)

    def test_champion_not_in_cache(self):
        """Tests that champion name not in cache triggers request"""
        name = src.LoL.get_champion_name("", CHAMPION_ID_NONCACHE)
        self.assertEqual(CHAMPION_NAME_NONCACHE, name)

if __name__ == '__main__':
    API_SUITE = unittest.TestLoader().loadTestsFromTestCase(APITests)
    unittest.TextTestRunner(verbosity=2).run(API_SUITE)
    CACHE_SUITE = unittest.TestLoader().loadTestsFromTestCase(CacheTests)
    unittest.TextTestRunner(verbosity=2).run(CACHE_SUITE)

#TODO Mock all possible responses from the LoL API and test all LoL.py methods
#TODO Test responses with rate limits
#TODO Test methods in cache.py
