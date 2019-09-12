from flask import Flask, render_template, request, jsonify
from flask_json import FlaskJSON, JsonError, json_response, as_json
from services.flagcomplex.FlagComplex import FlagComplex
#import json
import numpy as np

app = Flask(__name__)
app.config['DEBUG'] = True

FlaskJSON(app)

fcomplex = None


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/graphics')
def graphics():
    global fcomplex
    fcomplex = FlagComplex()
    fcomplex.set_projection_plane(np.array([0,0,1]))
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
    pplane = request.get_json()["pplane"]
    app.logger.info("Setting the projection plane to be " + str(pplane) + ".")
    fcomplex.set_projection_plane(np.array(pplane))
    # The number of flags
    n = len(data['ps'])
    # Adding all flags to the flag complex object
    app.logger.info("Adding " + str(n) + " flags to the python flag complex object.")
    for i in range(n):
        p = flags['ps'][str(i)]
        p.append(100.0)
        direction = flags['ds'][str(i)]
        direction.append(100.0)
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
    return jsonify(data)



@app.route("/flagcomplex/add_flags", methods=['POST'])
def add_flag():
    global fcomplex
    flags = request.get_json()
    n = len(flags['ps'])
    app.logger.info("Adding " + str(n) + " flags to the python flag complex object.")
    for i in range(n):
        p = flags['ps'][str(i)]
        p.append(100.0)
        direction = flags['ds'][str(i)]
        direction.append(100.0)
        fcomplex.add_flag(p, direction)
    return "done"

@app.route("/flagcomplex/get_eruption_flow", methods=['POST'])
def get_eruption_flow():
    global fcomplex

    data = dict()
    fcomplex.create_triangulation()
    triangle = fcomplex.triangles[0]

    fcomplex.erupt_triangle(t=-10.01, triangle=triangle, transformation_style="Q")
    for i in range(2001):
        t = -1000+i
        fcomplex.erupt_triangle(t=0.01, triangle=triangle, transformation_style="Q")
        fcomplex.draw_complex()
        drawps = [(x * 100).tolist() for x in fcomplex.drawps]
        drawqs = [(x * 100).tolist() for x in fcomplex.drawqs]
        us = fcomplex.get_inner_triangle(triangle)
        drawus = [(fcomplex.get_two_dimensional_point(x) * 100).tolist() for x in us]
        data[t] = {"ps": drawps, "qs": drawqs, "us": drawus}
    print(data)
    return jsonify(data)




@app.route("/flagcomplex/set_projection_plane", methods=['POST'])
def set_projection_plane():
    global fcomplex
    pplane = request.get_json()["pp"]
    app.logger.info("Setting the projection plane to be " + str(pplane) + ".")
    fcomplex.set_projection_plane(np.array(pplane))
    fcomplex.draw_complex()

    # TODO: Multiply with 100 here.

    drawps = [(x*100).tolist() for x in fcomplex.drawps]
    drawqs = [(x*100).tolist() for x in fcomplex.drawqs]

    data = {"ps": drawps, "ls": drawqs}
    return jsonify(data)

#@app.before_request
#def log_request_info():
#    #app.logger.debug('Headers: %s', request.headers)
#    app.logger.debug('Body: %s', request.get_data())
#    return


if __name__ == '__main__':
    app.run()
