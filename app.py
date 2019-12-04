from flask import Flask, render_template, request, jsonify
from flask_json import FlaskJSON
from flagcomplex import FlagComplex
import copy
from services.flagcomplex_interface import init_flagcomplex_from_data,\
    compute_eruption_data, compute_shear_data, compute_bulge_data

app = Flask(__name__)
app.config['DEBUG'] = True

FlaskJSON(app)

"""
Error codes:

0 = No error.
1 = The tuple of flags is not positive.
"""


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
    # The input data from the post request contains information about the points "ps", the line they are on "ds",
    # as well as the projection plane "pplane".
    data = request.get_json()
    pplane = data["pplane"]
    old_pplane = data["oldpplane"]
    width = data["width"]
    height = data["height"]
    n = len(data['ps'])

    fcomplex = init_flagcomplex_from_data(n, data, pplane, old_pplane)
    app.logger.info("Initialized flag complex with " + str(n) + " flags and projection plane " + str(pplane) + ".")


    # Checking the triple flow condition:
    if fcomplex.get_triple_ratio([0, 1, 2]) <= 0:
        app.logger.info("Flag complex not positive!")
        data['error'] = 1
    else:
        data['error'] = 0
        # Computing eruption flow data
        fcomplex.create_triangulation()
        if n == 3:
            triangle = fcomplex.triangles[0]
            data['erupt'] = compute_eruption_data(fcomplex, triangle,  width, height)
            app.logger.info("Computed eruption flow data.")
        if n == 4:
            quad = [0, 1, 2, 3]
            fcomplex1 = copy.deepcopy(fcomplex)
            data['shear'] = compute_shear_data(fcomplex1, quad, width, height)
            app.logger.info("Computed shear flow data.")
            data['bulge'] = compute_bulge_data(fcomplex, quad,  width, height)
            app.logger.info("Computed bulge flow data.")

        app.logger.info("All data successfully computed!")

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
