from flask import Flask, render_template, request, jsonify
from flask_json import FlaskJSON
from flask_navigation import Navigation
from flagcomplex import FlagComplex, FlagTesselator
import copy
from services.flagcomplex_interface import init_flagcomplex_from_data, \
    compute_eruption_data, compute_shear_data, compute_bulge_data, compute_ellipse, \
    rescale_existing_points, compute_no_trafo_data, compute_eruption_data_minus_plus, compute_eruption_data_plus_plus

app = Flask(__name__)
app.config['DEBUG'] = True

n_max = 10


FlaskJSON(app)
nav = Navigation(app)

nav.Bar('top', [
    nav.Item('Home', 'home'),
    nav.Item('Application', 'graphics'),
    nav.Item('Tips and tricks', 'tricks'),
    nav.Item('Mathematical Background', 'math_background'),
    nav.Item('About', 'about')
])

"""
Error codes:

0 = No error.
1 = The tuple of flags is not positive.
2 = Too many flags.
"""

# The home page
@app.route('/')
def home():
    return render_template("home.html")

# The page with all the interactive parts of the app.
@app.route('/graphics')
def graphics():
    return render_template("graphics.html", n_max=n_max)

# Some mathematical explanations
@app.route('/math-background')
def math_background():
    return render_template("math_background.html")

# Tips and tricks for the app
@app.route('/tricks')
def tricks():
    return render_template("tricks.html")


@app.route("/about")
def about():
    return render_template("about.html")

# Server request for calculating the transformation data. This is called by
# the graphics page.
@app.route("/flagcomplex/get_transformation_data", methods=['POST'])
def get_transformation_data():
    # The input data from the post request contains information about the points "ps", the line they are on "ds",
    # as well as the projection plane "pplane".
    data = request.get_json()
    pplane = data["pplane"]
    old_pplane = data["oldpplane"]
    # The number of flags
    n = len(data['ps'])

    # Cancel computation if there are too many flags
    if n > 10:
        app.logger.info("Too many flags. Cancelling computation!")
        data['error'] = 2
        return jsonify(data)

    # Set up for the transformation and tesselation computations
    tesselation_steps = 3
    t_step = 0.1
    trafo_range = {"erupt": {"trafo_range": 100, "t_step": t_step},
                   "shear": {"trafo_range": 80, "t_step": t_step},
                   "bulge": {"trafo_range": 80, "t_step": t_step},
                   "eruptmp": {"trafo_range": 50, "t_step": t_step},
                   "eruptpp": {"trafo_range": 50, "t_step": t_step},
                   "no_trafo": {"trafo_range": 0, "t_step": 0}}

    # Flag complex object to perform transformations on
    fcomplex = init_flagcomplex_from_data(n, data, pplane, old_pplane)
    app.logger.info("Initialized flag complex with " + str(n) + " flags and projection plane " + str(pplane) + ".")

    # Checking the triple flow condition:
    if not fcomplex.is_complex_positive():
        app.logger.info("Flag complex not positive!")
        data['error'] = 1
    # If there is no problem, calculate the transformation data according to the number of flags.
    else:
        data['error'] = 0
        # Computing eruption flow data
        fcomplex.create_triangulation()
        ftess = FlagTesselator(fcomplex, steps=tesselation_steps)
        if n == 3:
            triangle = fcomplex.triangles[0]
            data['erupt'] = compute_eruption_data(fcomplex, ftess, **trafo_range["erupt"])
            app.logger.info("Computed eruption flow data.")
        if n == 4:
            fcomplex.refresh_setup()
            data['ellipse'] = compute_ellipse(fcomplex)
            app.logger.info("Computed ellipse.")
            fcomplex1 = copy.deepcopy(fcomplex)
            ftess1 = FlagTesselator(fcomplex1, steps=tesselation_steps)
            app.logger.info("Computing shear flow data...")
            data['shear'] = compute_shear_data(fcomplex1, ftess1, **trafo_range["shear"])
            app.logger.info("Success!")
            fcomplex1 = copy.deepcopy(fcomplex)
            ftess1 = FlagTesselator(fcomplex1, steps=tesselation_steps)
            app.logger.info("Computing bulge flow data...")
            data['bulge'] = compute_bulge_data(fcomplex1, ftess1, **trafo_range["bulge"])
            app.logger.info("Success!")
            app.logger.info("Computing eruption flow data (-/+)...")
            fcomplex1 = copy.deepcopy(fcomplex)
            ftess1 = FlagTesselator(fcomplex1, steps=tesselation_steps)
            data['eruptmp'] = compute_eruption_data_minus_plus(fcomplex1, ftess1, **trafo_range["eruptmp"])
            app.logger.info("Success!")
            app.logger.info("Computing eruption flow data (+/+)...")
            fcomplex1 = copy.deepcopy(fcomplex)
            ftess1 = FlagTesselator(fcomplex1, steps=tesselation_steps)
            data['eruptpp'] = compute_eruption_data_plus_plus(fcomplex1, ftess1, **trafo_range["eruptpp"])
            app.logger.info("Success!")
        if n > 4:
            data['no_trafo'] = compute_no_trafo_data(fcomplex, ftess)

        data['trafo_range'] = trafo_range

        app.logger.info("All data successfully computed!")

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
