# flag-transformator web application

The `flag-transformator` project is a web application with an interactive user interface for playing with different
transformations of flag complexes in the real projective plane. It provides transformations such as the bulge flow, the
shear flow and the eruption flow.

`flag-transformator` can be viewed in your web browser. The geometric backend on the server side is the Python package `projflag-lib/flagcomplex`.

## Setup instructions

### Setup using pip (private use)

1. Download the `flag-transformator` source files and unpack them.
2. Open a command prompt of your choice and navigate to the flag transformator folder.
3. Execute `pip install -r requirements.txt`.
4. Start the application server with `python3 src/setup.py`. Open the address shown in the command prompt in your browser, e.g. `http://172.18.108.70:80/`.

### Setup using Docker (production use)

1. Install `docker` from www.docker.com. (On Windows: Start the Docker desktop client after the installation.)
2. Download the `flag-transformator` source files and unpack them.
3. Open a command prompt of your choice and navigate to the flag transformator folder.
4. Execute `docker build -t flagtransformator-image .` in order to create a Docker image from the container.
5. Start the application server with `docker run -d -p 80:80 flagtransformator-image`. Open the address `http://localhost/` in your browser in order to see the app.
