To run the app:

* In the Dockerfile, change the API_KEY environment variable to the apropriate value
* Run "docker build -t appriot ." to build the app
* Run "docker run -p 4555:80 appriot" to run the app
* Access the app in browser via "http://localhost:4555"

To run tests:

* python tests.py

Regarding rate limits:

* Currently only mechanism implemented is caching the champions names (most frequent limitation)
* Cache could also be added to getAccountID and getMatchData
* To handle the rate limits properly (with time), the stategy I would follow is:
* * Define a max waiting time constant
* * When a request returns 429, check if 'Retry-After' is less than the max waiting time
* * If yes, wait and retry
* * If no, return a 500 error asking the user to try again later