You should have docker installed on your system to contribute to and run Riki.

Before running, ensure you have a configuration file in the root directory, called .env
Base your .env file on the .env.template file provided by the repo.
In particular, edit line 1 to be whatever the secret key is that was communicated to you previously.
Other than that, no edits should be necessary.

LIST OF COMMANDS (from current directory):
To build docker image:
   docker-compose build

To run docker image:
   docker-compose up
   When running, you should see webapp logs.  To view in browser, visit:
   localhost:5001

To stop the docker image either:
   CTRL+C in the now blocking terminal window
    or
   docker-compose down
   in a new terminal window.

To run tests on the Riki system:
   docker-compose run riki test
   This should generate coverage reports in the reports/cov_html folder.

To generate documentation about the Riki system:
   docker-compose run riki docs
   this should generate documentation in the reports/docs/wiki folder.
   after running the docker image, you can access the documentation at:
   http://localhost:5001/static/docs/wiki/index.html

To run in debug mode:
   docker-compose run riki debug
   this will run the program with a debugger

To open a terminal in the running system:
   docker-compose run riki bash

In general, any bash command can be run on the Riki system with:
   docker-compose run riki <command>

NOTE: All predefined commands are in the Riki/entrypoint.sh file.
Examine that file for further information.