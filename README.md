```markdown
# Riki

*Note: Docker should be installed on your system to contribute to and run Riki.*

## Setup Instructions

Before running, ensure you have a configuration file in the root directory, `.env`.
Base your `.env` file on the `.env.template` file provided by the repo.
In particular, edit line 1 to include your secret

## List of Commands

**From the current directory:**

- **Build Docker image:**
   ```shell
   docker-compose build
   ```
- **Run Docker image:**
   ```shell
   docker-compose up
   ```
   While running, you should see webapp logs. To view in browser, visit: `localhost:5001`

- **Stop the Docker image:**
   - Press `CTRL+C` in the terminal window
   - Or run `docker-compose down` in a new terminal window.

- **Run tests on the Riki system:**
   ```shell
   docker-compose run riki test
   ```
   This should generate coverage reports in the `reports/cov_html` folder.

- **Generate documentation about the Riki system:**
   ```shell
   docker-compose run riki docs
   ```
   This should generate documentation in the `reports/docs/wiki` folder.
   After running the Docker image, you can access the documentation at: `http://localhost:5001/static/docs/wiki/index.html`

- **Run in debug mode:**
   ```shell
   docker-compose run riki debug
   ```
   This will run the program with a debugger.

- **Open a terminal in the running system:**
   ```shell
   docker-compose run riki bash
   ```
   
In general, any bash command can be run on the Riki system with:
```shell
docker-compose run riki <command>
```

**Note:** All predefined commands are in the `Riki/entrypoint.sh` file. Examine that file for further information.
```
