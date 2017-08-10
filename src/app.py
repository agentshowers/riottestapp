"""The main module for the API."""
import json
from flask import Flask, request, render_template
import LoL
import config

APP = Flask(__name__)

@APP.route("/")
def home():
    """Index for front-end."""
    return render_template('index.html')

@APP.route("/gamedata")
def gamedata():
    """Endpoint that returns the gamedata for a given summoner and region."""
    region = request.args.get("region", "")
    summoner = request.args.get("summoner", "")
    return get_game_data(region, summoner)

class APIError(Exception):
    """Custom exception handling API errors."""
    status_code = 500

    def __init__(self, message, status_code=None):
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
        return json.dumps(match_data)

    #Handle API Errors
    except LoL.SummonerNotFoundError as summ_error:
        raise APIError(summ_error.message, 404)

    except LoL.NoMatchesError as matches_error:
        raise APIError(matches_error.message, 404)

    except LoL.ApiError as api_error:
        raise APIError(api_error.message)

    except LoL.RequestError as request_error:
        raise APIError(request_error.message)

    except Exception as ex:
        raise APIError(ex.message)

def error_response(message, status_code):
    """Generates a generic error response."""
    return json.dumps({"status" : {"message" : message, "status_code" : status_code}})

if __name__ == "__main__":
    CONFIG = config.load_from_env()
    APP.run(host=CONFIG["HOST"], port=CONFIG["PORT"])
    