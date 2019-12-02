#import sys
#sys.path.append('../flagcomplex/')

from flask import Flask, render_template, request, jsonify
from flask_json import FlaskJSON #, JsonError, json_response, as_json
from flagcomplex import FlagComplex
from flagcomplex.EuklGeometryUtility import rotate_vectors
import numpy as np

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
    fcomplex = FlagComplex()

    # The input data from the post request contains information about the points "ps", the line they are on "ds",
    # as well as the projection plane "pplane".
    data = request.get_json()


    pplane = data["pplane"]
    old_pplane = data["oldpplane"]
    app.logger.info("Setting the projection plane to be " + str(pplane) + ".")
    fcomplex.set_projection_plane(np.array(pplane))
    # The number of flags
    n = len(data['ps'])
    # Adding all flags to the flag complex object
    app.logger.info("Adding " + str(n) + " flags to the python flag complex object.")
    if old_pplane == [0, 0, 1]:
        for i in range(n):
            p = data['ps'][i]
            # Note: We don't need this. Therefore, I commented it.
            # The webpage svg calculates coordinates on the scale of pixels,
            # which gives us very big numbers. We rescale them by a factor of 100.
            #p[:] = [x/100 for x in p]
            #p.append(1)
            p.append(100)
            direction = data['ds'][i]
            #direction[:] = [x/100 for x in direction]
            #direction.append(1)
            direction.append(100)
            fcomplex.add_flag(p, direction)
    else:
        for i in range(n):
            p = data['ps'][i]
            p.append(100)
            direction = data['ds'][i]
            direction.append(100)
            rotation_matrix = rotate_vectors(np.array([0, 0, 1]), np.array(old_pplane))
            p = np.matmul(rotation_matrix, p)
            direction = np.matmul(rotation_matrix, direction)

            fcomplex.add_flag(p, direction)

    # Checking the triple flow condition:
    if fcomplex.get_triple_ratio([0, 1, 2]) <= 0:
        app.logger.info("Flag complex not positive!")
        data['error'] = 1
    else:
        data['error'] = 0

        # Computing eruption flow data
        fcomplex.create_triangulation()
        triangle = fcomplex.triangles[0]

        app.logger.info("Computing eruption flow data.")
        fcomplex.erupt_triangle(t=-10.01, triangle=triangle, transformation_style="Q")
        for i in range(2001):
            t = -1000 + i
            fcomplex.erupt_triangle(t=0.01, triangle=triangle, transformation_style="Q")
            fcomplex.draw_complex()
            fc_drawus = fcomplex.get_projected_us(triangle)

            drawps= []
            drawqs= []
            drawus = []

            for k in range(n):
                x = fcomplex.drawps[k]
                if x is not None:
                    drawps.append((x*100).tolist())
                else:
                    drawps.append(None)
                x = fcomplex.drawqs[k]
                if x is not None:
                    drawqs.append((x * 100).tolist())
                else:
                    drawqs.append(None)
                x = fc_drawus[k]
                if x is not None:
                    drawus.append((x * 100).tolist())
                else:
                    drawus.append(None)
                data[t] = {"ps": drawps, "qs": drawqs, "us": drawus}
                app.logger.info("Data successfully computed!")
    return jsonify(data)

#@app.before_request
#def log_request_info():
#    #app.logger.debug('Headers: %s', request.headers)
#    app.logger.debug('Body: %s', request.get_data())
#    return


if __name__ == '__main__':
    app.run(debug=True)
