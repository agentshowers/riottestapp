To run the app:

1) In the Dockerfile, change the API_KEY environment variable to the apropriate value
2) Run "docker build -t appriot ." to build the app
3) Run "docker run -p 4555:80 appriot" to run the app
4) Access the app in browser via "http://localhost:4555"

To run tests:

1) python tests.py