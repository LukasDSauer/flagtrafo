from flask import Flask, render_template, request, jsonify
from flask_json import FlaskJSON
from flagcomplex import FlagComplex, FlagTesselator
import copy
from services.flagcomplex_interface import init_flagcomplex_from_data,\
    compute_eruption_data, compute_shear_data, compute_bulge_data, compute_ellipse,\
    rescale_existing_points, compute_no_trafo_data, compute_eruption_data_minus_plus

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
    n = len(data['ps'])
    tesselation_steps = 3

    fcomplex = init_flagcomplex_from_data(n, data, pplane, old_pplane)
    app.logger.info("Initialized flag complex with " + str(n) + " flags and projection plane " + str(pplane) + ".")


    # Checking the triple flow condition:
    if not fcomplex.is_complex_positive():
        app.logger.info("Flag complex not positive!")
        data['error'] = 1
    else:
        data['error'] = 0
        # Computing eruption flow data
        fcomplex.create_triangulation()
        ftess = FlagTesselator(fcomplex, steps=tesselation_steps)
        if n == 3:
            triangle = fcomplex.triangles[0]
            data['erupt'] = compute_eruption_data(fcomplex, ftess)
            app.logger.info("Computed eruption flow data.")
        if n == 4:
        #     data['ellipse'] = compute_ellipse(fcomplex)
        #     app.logger.info("Computed ellipse.")
        #     fcomplex1 = copy.deepcopy(fcomplex)
        #     ftess1 = FlagTesselator(fcomplex1, steps=tesselation_steps)
        #     app.logger.info("Computing shear flow data...")
        #     data['shear'] = compute_shear_data(fcomplex1, ftess1)
        #     app.logger.info("Success!")
        #     fcomplex1 = copy.deepcopy(fcomplex)
        #     app.logger.info("Computing bulge flow data...")
        #     data['bulge'] = compute_bulge_data(fcomplex1, ftess1)
        #     app.logger.info("Success!")
            app.logger.info("Computing eruption flow data (-/+)...")
            data['eruptmp'] = compute_eruption_data_minus_plus(fcomplex, ftess)
            app.logger.info("Success!")
        if n > 4:
            data['no_trafo'] = compute_no_trafo_data(fcomplex, ftess)


        app.logger.info("All data successfully computed!")

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
