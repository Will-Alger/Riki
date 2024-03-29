import os

from wiki import create_app

directory = os.getcwd()
app = create_app(directory)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)
