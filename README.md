# flagtrafo - The Flag Transformation Web Application

The `flagtrafo` project is a web application with an interactive user interface for playing with different
transformations of flag complexes in the real projective plane. It provides transformations such as the bulge flow, the
shear flow and the eruption flow.

`flagtrafo` can be viewed in your web browser. The geometric backend on the server side is the Python package `projflag-lib/flagcomplex`.

## Setup instructions

### Setup using pip (private use)

1. Download the `flagtrafo` source files and unpack them.
2. Open a command prompt of your choice and navigate to the flagtrafo folder. (Optionally [activate a virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment).)
3. Execute `pip install -r requirements.txt`.
4. Start the application server with `python3 src/app.py`. Open the address shown in the command prompt in your browser, e.g. `http://172.18.108.70:80/`.

Hint for developers: You may want to activate the debug mode, which causes the server to update whenever you change the
code. This can be achieved by uncommenting the line `# app.config['DEBUG'] = True` in the file `src/app.py` or by running
`$env:FLASK_ENV = "development"` in your Windows PowerShell, or by running `export FLASK_DEBUG` in your Linux shell.

### Setup using Docker (production use)

1. Install `docker` from www.docker.com. (On Windows: Start the Docker desktop client after the installation.)
2. Download the `flagtrafo` source files and unpack them.
3. Open a command prompt of your choice and navigate to the flagtrafo folder.
4. Execute `docker build -t flagtrafo-image .` in order to create a Docker image from the container.
5. Start the application server with `docker run --name flagtrafo-container -d -p 80:80 flagtrafo-image`. Open the address `http://localhost/` in your browser in order to see the app.
