"""The main module for the API."""
import json
from flask import Flask, request, current_app, Response
import LoL
import config

APP = Flask(__name__)

@APP.route("/")
def home():
    """Index for front-end."""
    return current_app.send_static_file('index.html')

@APP.route("/gamedata")
def gamedata():
    """Endpoint that returns the gamedata for a given summoner and region."""
    region = request.args.get("region", "")
    summoner = request.args.get("summoner", "")
    payload = get_game_data(region, summoner)
    resp = Response(response=payload,
                    status=200,
                    mimetype="application/json")
    return resp

class APIError(Exception):
    """Custom exception handling API errors."""
    def __init__(self, message, status_code):
        Exception.__init__(self)
        if status_code is not None:
            self.status_code = status_code
        self.message = error_response(message, status_code)

@APP.errorhandler(APIError)
def handle_api_error(error):
    """Handles API errors."""
    return error.message, error.status_code

def get_game_data(region, summoner):
    """Gets the game data."""

    #Handle invalid parameters
    if region == "":
        raise APIError("Region parameter is mandatory", 400)

    if summoner == "":
        raise APIError("Summoner parameter is mandatory", 400)

    if not LoL.is_valid_region(region):
        message = "Region '{inRegion}' is not a valid region. " \
                  "Please select one from the following list: {list}"
        raise APIError(message.format(inRegion=region, list=LoL.get_region_list()), 404)

    try:
        account_id = LoL.get_account_id(region, summoner)
        latest_match = LoL.get_latest_match(region, account_id)
        match_data = LoL.get_match_data(region, latest_match)
        return json.dumps(parse_match_data(region, match_data))

    #Handle API Errors
    except LoL.SummonerNotFoundError as summ_error:
        raise APIError(summ_error.message, 404)

    except LoL.NoMatchesError as matches_error:
        raise APIError(matches_error.message, 404)

    except LoL.ApiError as api_error:
        raise APIError(api_error.message, 500)

    except LoL.RequestError as request_error:
        raise APIError(request_error.message, 500)

    except Exception as ex:
        raise APIError(ex.message, 500)

def parse_match_data(region, match_info):
    """Gets match data from response JSON object"""
    participant_list = []

    for player in match_info["participantIdentities"]:
        p_id = player["participantId"]
        summoner_name = player["player"]["summonerName"]
        summoner_id = player["player"]["summonerId"]
        p_data = [p for p in match_info["participants"] if p["participantId"] == p_id][0]
        team_id = p_data["teamId"]
        champion_id = p_data["championId"]
        champion_name = LoL.get_champion_name(region, champion_id)
        champion_mastery = LoL.get_champion_mastery(region, champion_id, summoner_id)
        participant = {"summonerId" : summoner_id, "summonerName" : summoner_name,
                       "teamId" : team_id, "championId" : champion_id,
                       "championName" : champion_name, "championMastery" : champion_mastery}
        participant_list.append(participant)

    return {"gameId" : match_info["gameId"],
            "participants" : sorted(participant_list,
                                    key=lambda part: (part["championMastery"], part["championId"]))}


def error_response(message, status_code):
    """Generates a generic error response."""
    return json.dumps({"status" : {"message" : message, "status_code" : status_code}})

if __name__ == "__main__":
    CONFIG = config.load_from_env()
    APP.run(host=CONFIG["HOST"], port=CONFIG["PORT"])
    