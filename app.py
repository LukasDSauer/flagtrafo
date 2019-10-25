import sys
sys.path.append('services/flagcomplex/')

from flask import Flask, render_template, request, jsonify
from flask_json import FlaskJSON, JsonError, json_response, as_json
from FlagComplex import FlagComplex
from EuklGeometryUtility import rotate_vectors
import numpy as np

app = Flask(__name__)
app.config['DEBUG'] = True

FlaskJSON(app)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/graphics')
def graphics():
    return render_template("graphics.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/flagcomplex/get_transformation_data", methods=['POST'])
def get_transformation_data():
    fcomplex = FlagComplex()

    # The input data from the post request contains information about the points "ps", the line they are on "ds",
    # as well as the projection plane "pplane".
    data = request.get_json()
    #print("ALL THE DATA!")
    #print(data)
    pplane = request.get_json()["pplane"]
    app.logger.info("Setting the projection plane to be " + str(pplane) + ".")
    fcomplex.set_projection_plane(np.array(pplane))
    # The number of flags
    n = len(data['ps'])
    # Adding all flags to the flag complex object
    app.logger.info("Adding " + str(n) + " flags to the python flag complex object.")
    if pplane == [0, 0, 1]:
        for i in range(n):
            p = data['ps'][i]
            p.append(100.0)
            direction = data['ds'][i]
            direction.append(100.0)
            fcomplex.add_flag(p, direction)
    else:
        for i in range(n):
            p = data['ps'][i]
            p.append(100.0)
            direction = data['ds'][i]
            direction.append(100.0)
            rotation_matrix = rotate_vectors(np.array(pplane), np.array([0, 0, 1]))
            p = np.matmul(rotation_matrix, p)
            direction = np.matmul(rotation_matrix, direction)

            fcomplex.add_flag(p, direction)


    # Computing eruption flow data
    fcomplex.create_triangulation()
    triangle = fcomplex.triangles[0]

    app.logger.info("Computing eruption flow data.")
    fcomplex.erupt_triangle(t=-10.01, triangle=triangle, transformation_style="Q")
    for i in range(2001):
        t = -1000 + i
        fcomplex.erupt_triangle(t=0.01, triangle=triangle, transformation_style="Q")
        fcomplex.draw_complex()
        drawps = [(x * 100).tolist() for x in fcomplex.drawps]
        drawqs = [(x * 100).tolist() for x in fcomplex.drawqs]
        us = fcomplex.get_inner_triangle(triangle)
        drawus = [(fcomplex.get_two_dimensional_point(x) * 100).tolist() for x in us]
        data[t] = {"ps": drawps, "qs": drawqs, "us": drawus}
    app.logger.info("Data successfully computed!")
    app.logger.info(data)
    return jsonify(data)

#@app.before_request
#def log_request_info():
#    #app.logger.debug('Headers: %s', request.headers)
#    app.logger.debug('Body: %s', request.get_data())
#    return


if __name__ == '__main__':
    app.run()
