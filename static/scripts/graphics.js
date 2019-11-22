/*
 * Functions handling interactive site elements.
 */
/**
 * Function handling the "Submit flags" button. If the site was in the "addPoints" or "addLines" mode,
 * it sends the new flags to the server using the submit_flags_to_server() function.
 *
 * If the site was in the "standard" mode before, it switches to "addPoints" modes and enables
 * the user to hover new points over the canvas.
 */
function switch_program_mode_to(mode) {
    if (mode === "standard") {
        program_mode = "standard";
        document.getElementById('add_flag_buttonb').value = "Add flags";
        show_editing_elements();
        if (Object.keys(ui_elements).includes(n.toString())) {
            // Numbers with special transformations get the following hint:
            document.getElementById('hint-type').style.display = "inline";
            document.getElementById('mode-description').innerHTML =
                "Move slider to transform.";
        }
    }
    if (mode === "addFlags") {
        svg.selectAll("#u_point").remove();
        svg.selectAll("#u_line").remove();
        svg.selectAll("#p_point").remove();
        svg.selectAll("#p_line").remove();
        svg.selectAll("#helper_line").remove();
        hide_editing_elements();
        document.getElementById("add_flag_buttonb").style.display = "block";
        document.getElementById('add_flag_buttonb').value = "Finish";
        switch_program_mode_to("addPoints");
    }
    if (mode === "addPoints") {
        program_mode = "addPoints";
        document.getElementById('mode-description').innerHTML = "Click to add point. " +
            "Click 'finish' to finish adding more flags.";
    }
    if (mode === "addLines") {
        program_mode = "addLines";
        document.getElementById('mode-description').innerHTML = "Click to add line. ";
    }

}

function submit_flags_button() {
    if (program_mode === "addPoints" || program_mode === "addLines") {
        if (n_submit.includes(n)) {
            submit_flags_to_server(false);
        } else {
            svg.selectAll("#newpoint").remove();
            svg.selectAll("#newline").remove();
            switch_program_mode_to("standard");
        }
    } else if (program_mode == "standard") {
        switch_program_mode_to("addFlags");
        svg.on("mousemove", mouse_move_point_or_line)
            .on("click", mouse_click_point_or_line);
    }
}

/**
 * If the site is in the "addPoints" or "addLines" mode, a new point resp. line hovers over the canvas
 * whereever the mouse is.
 */
function mouse_move_point_or_line() {
    liveCoordinates = d3.mouse(this);

    if (program_mode == "addPoints") {
        //TODO: Change this to drawPoints, we don't need the extra function.
        draw_points([liveCoordinates], "newpoint", NEW_HIGHLIGHT_COLOR, flag_layer);
    } else if (program_mode == "addLines") {
        draw_infinite_lines([fixedCoordinates], [liveCoordinates], "newline", NEW_HIGHLIGHT_COLOR, flag_layer);
    }
}

/**
 * If the site is in the "addPoints" or "addLines" mode, the hovering point resp. line will be fixed
 * in place whenever the user clicks.
 *
 * Furthermore, it switches mode to "addLines" resp. "addPoints" to enable adding further objects.
 */
function mouse_click_point_or_line() {
    if (program_mode == "addPoints") {
        switch_program_mode_to("addLines");
    } else if (program_mode == "addLines") {
        if (n <= n_max) {
            svg.selectAll("#newline")
            .style('stroke', '#393939')
            .attr("id", "line");

            svg.selectAll("#newpoint")
                .style('stroke', '#393939')
                .style('fill', '#393939')
                .attr("id", "point");

            ps_2dim[n] = fixedCoordinates;
            ds_2dim[n] = liveCoordinates;
            n++;
            switch_program_mode_to("addPoints");
        } else {
            svg.selectAll("#newpoint").remove();
            svg.selectAll("#newline").remove();
            submit_flags_button();
            alert("You can not add more than " + n_max.toString() + " flags!");
        }
    }
    fixedCoordinates = d3.mouse(this);
}

/**
 * Function handling the "Submit projection plane" button. It reads the entered values from the
 * projection plane form. It then sends the flags and the new projection plane value to the server
 * using the submit_flags_to_server() function.
 */
function submit_projection_plane_button() {
    var x = parseFloat($("#ppx").val());
    var y = parseFloat($("#ppy").val());
    var z = parseFloat($("#ppz").val());

    // Verifying whether the inputs are actual numbers.
    if (isNaN(x) || isNaN(y) || isNaN(z)) {
        alert("One of the projection plane inputs is not a proper number!")
    } else {
        old_proj_plane = proj_plane;
        proj_plane = [x, y, z];
        submit_flags_to_server(true);
        document.getElementById("pplane-value").innerHTML = "(" + proj_plane[0] + ", " + proj_plane[1] + ", " + proj_plane[2] + ")";
    }
}

/*
 * Functions for interaction with the server.
 */
/**
 * This function submits all the flag data to the server and receives transformation data (as well
 * as updated points, if the projection plane was changed) from the server.
 *
 * During the calculation time of the server, all interactive elements of the site are hidden, in
 * order to prevent changes from the user.
 */
function submit_flags_to_server(with_refresh) {
    t = 0;
    t_str = "0";

    hide_editing_elements();
    show_loader();

    svg.selectAll("#newpoint").remove();
    svg.selectAll("#newline").remove();

    var data = {
        "ps": ps_2dim,
        "ds": ds_2dim,
        "pplane": proj_plane,
        "oldpplane": old_proj_plane
    };
    data = JSON.stringify(data);
    console.log(data);

    $.ajax({
        type: "POST",
        url: '/flagcomplex/get_transformation_data',
        data: data,
        dataType: "json",
        contentType: "application/json; charset=utf-8"
    })
        .done(function (data) {
            console.info("All the transformation data received!")
            trafo_data = data;
            ps_2dim = trafo_data[t_str]["ps"];
            qs_2dim = trafo_data[t_str]["qs"];
            // From now on, we can use the qs for the ds, as they simply are another point on the line,
            // and this is all that we need.
            ds_2dim = trafo_data[t_str]["qs"];
            us_2dim = trafo_data[t_str]["us"];

            hide_loader();
            switch_program_mode_to("standard");

            if (with_refresh) {
                refresh_svg();
            }
        });
}

/*
 * Functions for interaction with the SVG object.
 */

/**
 * This functions updates all the SVG elements coordinates, e.g. after a transformation has been applied.
 */
function refresh_svg() {
    update_points(ps_2dim, "point");
    update_points(us_2dim, "u_point");
    update_points(ps_2dim, "p_point");
    update_triangle(us_2dim, "u_line");
    update_triangle(ps_2dim, "p_line");
    update_helper_lines(ps_2dim, qs_2dim, "helper_line");
    update_infinite_lines(ps_2dim, ds_2dim, "line");
}

/**
 * Draws infinite lines through points data0[i] and data1[i] for all i. An infinite line not only
 * connects the two points, but stretches over the whole canvas.
 *
 * @param data0: an array of 2-dim arrays (point coordinates)
 * @param data1: another array of 2-dim arrays (point coordinates)
 * @param id: an id string for identifying the lines later
 * @param color: a color string specifying the object's color
 */
function draw_infinite_lines(data0, data1, id, color, layer) {
    // We will not draw the line between point0 and point1
    // as it will not appear infinitely long. Instead, we will calculate the line's
    // intersection points with the boundary of the canvas. Then, the line will appear "infinitely" long.
    data = [];
    for (var i = 0; i < data0.length; i++) {
        data.push(get_intersection_with_frame(data0[i], data1[i]));
    }

    var line = layer.selectAll("#" + id)
        .data(data);

    line.exit().remove();

    line.enter().append("line")
        .attr("id", id)
        .merge(line)
        .style('stroke', color)
        .attr("x1", function (d) {
            return d[0][0];
        })
        .attr("y1", function (d) {
            return d[0][1];
        })
        .attr("x2", function (d) {
            return d[1][0];
        })
        .attr("y2", function (d) {
            return d[1][1];
        });

    d3.event.preventDefault();
}

/**
 * draws little circles at all the points specified in data
 *
 * @param data: an array of 2-dim arrays
 * @param id: an id string for identifying the points later
 * @param color: a color string specifying the object's color
 */
function draw_points(data, id, color, layer) {
    var circle = layer.selectAll("#" + id)
        .data(data);
    circle.exit().remove();

    circle.enter().append("circle")
        .attr("id", id)
        .attr("r", 2.5)
        .merge(circle)
        .style('stroke', color)
        .style('fill', color)
        .attr("cx", function (d) {
            return d[0];
        })
        .attr("cy", function (d) {
            return d[1];
        });
}

/**
 * draws lines connecting the three corners of the triangle specified in data
 *
 * @param data: a 3-dim array of 2-dim arrays
 * @param id: an id string for identifying the triangle's lines later
 * @param color: a color string specifying the object's color
 */
function draw_triangle(data, id, color, layer) {
    for (var i = 0; data.length - 1; i++) {
        layer.append("line")
            .attr("id", id)
            .style('stroke', color)
            .attr("x1", data[i][0])
            .attr("y1", data[i][1])
            .attr("x2", data[(i + 1) % 3][0])
            .attr("y2", data[(i + 1) % 3][1]);
    }
}

/**
 * draws helper lines between the points in the middle triangle and in the outer triangle
 *
 * @param data: a 3-dim array of 2-dim arrays
 * @param id: an id string for identifying the lines later
 * @param color: a color string specifying the object's color
 */
function draw_helper_lines(data_middle, data_outer, id, color, layer) {
    for (var i = 0; data_middle.length - 1; i++) {
        layer.append("line")
            .attr("id", id)
            .style('stroke', color)
            .attr("x1", data_middle[i][0])
            .attr("y1", data_middle[i][1])
            .attr("x2", data_outer[(i + 2) % 3][0])
            .attr("y2", data_outer[(i + 2) % 3][1]);
    }
}

/**
 * updates the objects coordinates
 * @param data0
 * @param data1
 * @param id
 */
function update_infinite_lines(data0, data1, id) {
    data = [];
    for (var i = 0; i < data0.length; i++) {
        data.push(get_intersection_with_frame(data0[i], data1[i]));
    }

    svg.selectAll("#" + id)
        .data(data)
        .attr("x1", function (d) {
            return d[0][0];
        })
        .attr("y1", function (d) {
            return d[0][1];
        })
        .attr("x2", function (d) {
            return d[1][0];
        })
        .attr("y2", function (d) {
            return d[1][1];
        });
}

/**
 * updates the objects coordinates
 * @param data
 * @param id
 */
function update_triangle(data, id) {
    var index = [0, 1, 2];
    svg.selectAll("#" + id)
        .data(index)
        .attr("x1", function (i) {
            return data[i][0];
        })
        .attr("y1", function (i) {
            return data[i][1];
        })
        .attr("x2", function (i) {
            return data[(i + 1) % 3][0];
        })
        .attr("y2", function (i) {
            return data[(i + 1) % 3][1];
        });
}

/**
 * updates the objects coordinates
 * @param data
 * @param id
 */
function update_points(data, id) {
    svg.selectAll("#" + id)
        .data(data)
        .attr("cx", function (d) {
            return d[0];
        })
        .attr("cy", function (d) {
            return d[1];
        });
}

/**
 * updates the objects coordinates
 * @param middle_data
 * @param outer_data
 * @param id
 */
function update_helper_lines(middle_data, outer_data, id) {
    var index = [0, 1, 2];
    svg.selectAll("#" + id)
        .data(index)
        .attr("x1", function (i) {
            return middle_data[i][0];
        })
        .attr("y1", function (i) {
            return middle_data[i][1];
        })
        .attr("x2", function (i) {
            return outer_data[(i + 2) % 3][0];
        })
        .attr("y2", function (i) {
            return outer_data[(i + 2) % 3][1];
        });
}

/*
 * Functions for altering the user interface.
 */
/**
 * hides interactive sliders and buttons
 */
function hide_editing_elements() {
    ui_elements["all_elements"].forEach(function (item, index) {
        document.getElementById(item).style.display = "none";
    });
}

/**
 * hides the little loading circle
 */
function hide_loader() {
    document.getElementById('loader:flags').style.display = "none";
}

/**
 * displays interactive sliders and buttons
 */
function show_editing_elements() {
    // UI elements that are only displayed for this particular number of flags n.
    console.log(Object.keys(ui_elements));

    if (Object.keys(ui_elements).includes(n.toString())) {
        ui_elements[n.toString()].forEach(function (item, index) {
            document.getElementById(item).style.display = "block";
        });
    }
    // UI elements that are displayed for all numbers of flags.
    ui_elements["show_for_all_n"].forEach(function (item, index) {
        document.getElementById(item).style.display = "block";
    });
}

/**
 * displays the loading circle (during loading data from the server)
 */
function show_loader() {
    document.getElementById('hint-type').style.display = "none";
    document.getElementById('mode-description').innerHTML = "Loading transformation data.";
    document.getElementById('loader:flags').style.display = "block";
}

/*
 * Geometric helper functions.
 */
/**
 * For a line passing through the points point0 and point1, this functions calculates its intersection
 * points with the frame of the canvas.
 *
 * @param point0: a 2-dim array
 * @param point1: a 2-dim array
 * @returns {[]}: an array of two 2-dim arrays
 */
function get_intersection_with_frame(point0, point1) {
    var output = [];

    if (point0[0] - point1[0] !== Infinity) {
        var a = (point0[1] - point1[1]) / (point0[0] - point1[0]);
        var b = point0[1] - a * point0[0];
        // The following points are the possible intersection
        // points of the line a*x+b with the image frame lines.
        var intersection_points = [];
        intersection_points.push([0, b]);
        intersection_points.push([width, a * width + b]);
        intersection_points.push([-b / a, 0]);
        intersection_points.push([(height - b) / a, height]);
        // Now we need to check whether the points are also inside the frame.
        var x;
        for (x in intersection_points) {
            if (intersection_points[x][0] >= 0 && intersection_points[x][0] <= width && intersection_points[x][1] >= 0 && intersection_points[x][1] <= height) {
                output.push(intersection_points[x]);
            }
        }
    } else {
        console.info('Handling exception Infinity!');
    }
    return output;
}






