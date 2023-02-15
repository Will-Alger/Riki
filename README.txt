Directory structure should be:
Dockerfile
README.txt (this file)
Riki
- <riki source code>
To build docker image:
docker build -t riki .
To run docker image:
docker run -p 5001:5001 riki
When running, you should see webapp logs.  To view in browser, visit:
localhost:5001