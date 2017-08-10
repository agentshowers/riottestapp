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

class APITests(unittest.TestCase):
    """Tests the exposed API."""

    def setUp(self):
        src.LoL.is_valid_region = mock_is_valid_region
        src.LoL.get_account_id = mock_get_account_id
        src.LoL.get_latest_match = mock_get_latest_match
        src.LoL.get_match_data = mock_get_match_data

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

if __name__ == '__main__':
    API_SUITE = unittest.TestLoader().loadTestsFromTestCase(APITests)
    unittest.TextTestRunner(verbosity=2).run(API_SUITE)

#TODO Mock the requests.get method and test LoL module methods
