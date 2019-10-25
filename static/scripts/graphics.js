/*
 * Fixed variables
 */
var new_object_color = '#007979';

/*
 * Functions handling interactive site elements.
 */
function submit_flags_button() {
    if (program_mode == "addPoints" || program_mode == "addLines") {
        console.info("Submitting flags to server!")
        submit_flags_to_server();
    } else if (program_mode == "standard") {
        console.info("Switching to the 'Add flag' mode!");
        program_mode = "addPoints";
        hide_editing_elements();
        document.getElementById('add_flag_buttonb').value = "Finish";
        svg.on("mousemove", mouse_move_point_or_line)
            .on("click", mouse_click_point_or_line);
    }
}

function mouse_move_point_or_line() {
    liveCoordinates = d3.mouse(this);

    if (program_mode == "addPoints") {
        //TODO: Change this to drawPoints, we don't need the extra function.
        draw_points([liveCoordinates], "newpoint", new_object_color);
    } else if (program_mode == "addLines") {
        draw_infinite_line(fixedCoordinates, liveCoordinates);
    }
}

function mouse_click_point_or_line() {
    if (program_mode == "addPoints") {
        program_mode = "addLines";
        document.getElementById('mode-description').innerHTML = "Click to add line. ";
    } else if (program_mode == "addLines") {
        program_mode = "addPoints";
        document.getElementById('mode-description').innerHTML = "Click to add point. " +
            "Click 'finish' to finish adding more flags.";
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

    }
    fixedCoordinates = d3.mouse(this);
}

function submit_projection_plane_button() {
    proj_plane = [parseFloat($("#ppx").val()),
        parseFloat($("#ppy").val()),
        parseFloat($("#ppz").val())];
    submit_flags_to_server();
    refresh_svg();
    document.getElementById("pplane-value").innerHTML = "(" + proj_plane[0] + ", " + proj_plane[1] + ", " + proj_plane[2] + ")";
}

/*
 * Functions for interaction with the server.
 */

function submit_flags_to_server() {
    hide_editing_elements();
    show_loader();
    document.getElementById('hint-type').style.display = "none";
    document.getElementById('mode-description').innerHTML = "Loading transformation data.";

    svg.selectAll("#newpoint").remove();
    svg.selectAll("#newline").remove();
    document.getElementById('add_flag_buttonb').value = "Add flags";
    program_mode = "standard";
    var data = {
        "ps": ps_2dim,
        "ds": ds_2dim,
        "pplane": proj_plane
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
            console.log(data);
            trafo_data = data;
            ps_2dim = trafo_data[t_str]["ps"];
            qs_2dim = trafo_data[t_str]["qs"];
            // From now on, we can use the qs for the ds, as they simply are another point on the line,
            // and this is all that we need.
            ds_2dim = trafo_data[t_str]["qs"];
            us_2dim = trafo_data[t_str]["us"];
            hide_loader();
            show_editing_elements();
            document.getElementById('hint-type').style.display = "inline";
            document.getElementById('mode-description').innerHTML =
                "Move slider to transform.";
        });
}

/*
 * Functions for interaction with the SVG object.
 */

function refresh_svg() {
    update_points(ps_2dim, "#point");
    update_points(us_2dim, "#u_point");
    update_points(ps_2dim, "#p_point")
    update_triangle(us_2dim, "#u_line");
    update_triangle(ps_2dim, "#p_line");
    update_helper_lines(ps_2dim, qs_2dim, "#helper_line")

    var line_data = [];

    for (var i = 0; i < n; i++) {
        var intersectionPoints = get_intersection_with_frame(ps_2dim[i], ds_2dim[i]);
        line_data.push({
            "x1": intersectionPoints[0][0], "y1": intersectionPoints[0][1],
            "x2": intersectionPoints[1][0], "y2": intersectionPoints[1][1]
        });

    }

    svg.selectAll("#line")
        .data(line_data)
        .attr("x1", function (d) {
            return d["x1"];
        })
        .attr("y1", function (d) {
            return d["y1"];
        })
        .attr("x2", function (d) {
            return d["x2"];
        })
        .attr("y2", function (d) {
            return d["y2"];
        })
}

function draw_infinite_line(fixedCoordinates, liveCoordinates) {
    var intersectionPoints = get_intersection_with_frame(fixedCoordinates, liveCoordinates);
    data = [{
        "x1": intersectionPoints[0][0], "y1": intersectionPoints[0][1],
        "x2": intersectionPoints[1][0], "y2": intersectionPoints[1][1]
    }];

    var line = svg.selectAll("#newline")
        .data(data);

    line.exit().remove();

    line.enter().append("line")
        .attr("id", "newline")
        .merge(line)
        .style('stroke', '#007979')
        .attr("x1", function (d) {
            return d.x1;
        })
        .attr("y1", function (d) {
            return d.y1;
        })
        .attr("x2", function (d) {
            return d.x2;
        })
        .attr("y2", function (d) {
            return d.y2;
        });


    d3.event.preventDefault();
}

function draw_points(data, id, color) {
    var circle = svg.selectAll("#"+id)
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

function draw_triangle(data, id, color) {
    for (var i = 0; data.length - 1; i++) {
        svg.append("line")
            .attr("id", id)
            .style('stroke', color)
            .attr("x1", data[i][0])
            .attr("y1", data[i][1])
            .attr("x2", data[(i + 1) % 3][0])
            .attr("y2", data[(i + 1) % 3][1]);
    }
}

function draw_helper_lines(data_middle, data_outer, id, color) {
    for (var i = 0; data_middle.length - 1; i++) {
        svg.append("line")
            .attr("id", id)
            .style('stroke', color)
            .attr("x1", data_middle[i][0])
            .attr("y1", data_middle[i][1])
            .attr("x2", data_outer[(i + 2) % 3][0])
            .attr("y2", data_outer[(i + 2) % 3][1]);
    }
}

function update_triangle(data, id) {
    var index = [0, 1, 2];
    svg.selectAll(id)
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

function update_points(data, id) {
    svg.selectAll(id)
        .data(data)
        .attr("cx", function (d) {
            return d[0];
        })
        .attr("cy", function (d) {
            return d[1];
        });
}

function update_helper_lines(middle_data, outer_data, id) {
    var index = [0, 1, 2];
    svg.selectAll(id)
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

function hide_editing_elements() {
    document.getElementById('add_flag_buttonb').style.display = "none";
    document.getElementById('checkboxes-triangle').style.display = "none";
    document.getElementById('transformator').style.display = "none";
    document.getElementById('proj-plane-form').style.display = "none";
}

function hide_loader() {
    document.getElementById('loader-flags').style.display = "none";
}

function show_editing_elements() {
    document.getElementById('add_flag_buttonb').style.display = "block";
    document.getElementById('checkboxes-triangle').style.display = "block";
    document.getElementById('transformator').style.display = "block";
    document.getElementById('proj-plane-form').style.display = "inline";
}

function show_loader() {
    document.getElementById('loader-flags').style.display = "block";
}

/*
 * Geometric helper functions.
 */
function get_intersection_with_frame(point1, point2) {
    var output = [];

    if (point1[0] - point2[0] != Infinity) {
        var a = (point1[1] - point2[1]) / (point1[0] - point2[0]);
        var b = point1[1] - a * point1[0];
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




