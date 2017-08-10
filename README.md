To run the app:

1) In the Dockerfile, change the API_KEY environment variable to the apropriate value
2) Run "docker build -t appriot ." to build the app
3) Run "docker run -p 4555:80 appriot" to run the app (if you changed the HOST variable in Dockerfile, adjust the command to the new value)
4) Access the app in browser via "http://localhost:4555"