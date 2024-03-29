/*
 * Functions handling interactive site elements.
 */

/**
 * This function is used to switch from one program mode to the next. It updates GUI elements accordingly,
 * removes superfluous elements from the svg...
 *
 * @param mode a string with the name of the mode to switch to. Reasonable values are "standard", "addFlags",
 * "addPoints" and "addLines".
 */
function switch_program_mode_to(mode) {
    if (mode === "standard") {
        program_mode = "standard";
        document.getElementById('button-addflag').value = "Add flags";
        show_editing_elements();
        if (Object.keys(ui_elements).includes(n.toString())) {
            // Numbers with special transformations get the following hint:
            document.getElementById('b-hinttype').style.display = "inline";
            document.getElementById('span-modeinfo').innerHTML =
                "Move slider to transform.";
        } else {
            document.getElementById('span-modeinfo').innerHTML =
                "";
        }
    }
    if (mode === "addFlags") {
        n_old = n;
        if (us_2dim != null) {
            for (let i = 0; i < us_2dim.length; i++) {
                svg.selectAll("#u_point" + i.toString()).remove();
                svg.selectAll("#u_line" + i.toString()).remove();
            }
        }
        for (let i = 0; i < n - 1; i++) {
            svg.selectAll("#p_line" + i.toString()).remove();
        }
        svg.selectAll("#p_point").remove();

        svg.selectAll("#helper_line").remove();
        svg.selectAll("#convex").remove();
        svg.selectAll("#ellipse").remove();

        hide_editing_elements();
        document.getElementById("button-addflag").style.display = "block";
        document.getElementById('button-addflag').value = "Finish";
        svg.on("mousemove", mouse_move_point_or_line)
            .on("click", mouse_click_point_or_line);
        switch_program_mode_to("addPoints");
    }
    if (mode === "addPoints") {
        program_mode = "addPoints";
        document.getElementById('span-modeinfo').innerHTML = "Click to add point. " +
            "Click 'finish' to finish adding more flags.";
    }
    if (mode === "addLines") {
        program_mode = "addLines";
        document.getElementById('span-modeinfo').innerHTML = "Click to add line. ";
    }

}

/**
 * Function handling the "Submit flags" button. If the site was in the "addPoints" or "addLines" mode,
 * it sends the new flags to the server using the submit_flags_to_server() function.
 *
 * If the site was in the "standard" mode before, it switches to "addPoints" modes and enables
 * the user to hover new points over the canvas.
 */
function submit_flags_button() {
    if (program_mode === "addPoints" || program_mode === "addLines") {
        // only submit if the user has added something and if the server has
        // an actual job to do.
        if (n > 2 && n > n_old) {
            submit_flags_to_server(false);
        } else {
            svg.selectAll("#newpoint").remove();
            svg.selectAll("#newline").remove();
            switch_program_mode_to("standard");
        }
    } else if (program_mode === "standard") {
        switch_program_mode_to("addFlags");
    }
}

/**
 * If the site is in the "addPoints" or "addLines" mode, a new point resp. line hovers over the canvas
 * whereever the mouse is.
 */
function mouse_move_point_or_line() {
    liveCoordinates = d3.mouse(this);

    if (program_mode === "addPoints") {
        draw_points([liveCoordinates], "newpoint", NEW_HIGHLIGHT_COLOR, flag_layer);
    } else if (program_mode === "addLines") {
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
    if (program_mode === "addPoints") {
        switch_program_mode_to("addLines");
    } else if (program_mode === "addLines") {
        if (n <= n_max) {
            svg.selectAll("#newline")
                .style('stroke', '#393939')
                .attr("id", "line");

            svg.selectAll("#newpoint")
                .style('stroke', '#393939')
                .style('fill', '#393939')
                .attr("id", "point");

            ps_2dim.push(fixedCoordinates);
            ds_2dim.push(liveCoordinates);
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
    var x = parseFloat($("#input-ppx").val());
    var y = parseFloat($("#input-ppy").val());
    var z = parseFloat($("#input-ppz").val());

    // Verifying whether the inputs are actual numbers.
    if (isNaN(x) || isNaN(y) || isNaN(z)) {
        alert("One of the projection plane inputs is not a proper number!")
    } else {
        old_proj_plane = proj_plane;
        proj_plane = [x, y, z];
        submit_flags_to_server(true);
        document.getElementById("span-pplane").innerHTML = "(" + proj_plane[0] + ", " + proj_plane[1] + ", " + proj_plane[2] + ")";
    }
}

/**
 * Switches the transformation type.
 *
 * @param type a string that specifies the type to switch to.
 * "erupt" for n=3
 * "shear", "bulge", "eruptmp", "eruptpp" for n=4
 * "no_trafo" for other n.
 */
function switch_trafo_type_to(type) {
    trafo_type = type;
    select_trafo.value = type;

    // The range of the slider may be different for different trafo types.
    document.getElementById("range-trafo").max = trafo_range[trafo_type]["trafo_range"];
    document.getElementById("range-trafo").min = -trafo_range[trafo_type]["trafo_range"];

    // The shear flow has a unique GUI element.
    if (trafo_type === 'shear') {
        document.getElementById('input-withellipse').style.display = "block";
    } else {
        document.getElementById('input-withellipse').style.display = "none";
        svg.selectAll("#ellipse").remove();
    }
}

/**
 * Updates the coordinates with respect to the new value t.
 */
function transform_coordinates() {
    t_str = t.toString();
    // Basically we want t*t_step, but this sometimes gives us long floating points numbers, so we
    // perform some rounding magic.
    document.getElementById("trafovalue").innerHTML = (Math.round(10*t * trafo_range[trafo_type]["t_step"]+0.00001)/10).toString();
    // Update the current coordinates of the ps, qs and us.
    refresh_coordinates();
    refresh_svg(false);
}

/**
 * Refreshes coordinates. Usually called when trafo_type, the parameter t, or the data itself has been changed.
 */
function refresh_coordinates() {
    ps_2dim = trafo_data[trafo_type][t_str]["ps"];
    qs_2dim = trafo_data[trafo_type][t_str]["qs"];// From now on, we can use the qs for the ds, as they simply are another point on the line,
    // and this is all that we need.
    ds_2dim = qs_2dim;
    us_2dim = trafo_data[trafo_type][t_str]["us"];
    convex = trafo_data[trafo_type][t_str]["convex"];
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
    /*if (trafo_type !== "no_trafo") {
        t = 0;
        t_str = "0";
        refresh_coordinates();
    }*/
    hide_editing_elements();
    // Switch off mouse events during loading.
    svg.on("mousemove", null);
    svg.on("click", null);
    show_loader();

    svg.selectAll("#newpoint").remove();
    svg.selectAll("#newline").remove();


    var data = {
        "ps": ps_2dim,
        "ds": ds_2dim,
        "pplane": proj_plane,
        "oldpplane": old_proj_plane,
    };
    data = JSON.stringify(data);

    $.ajax({
        type: "POST",
        url: '/flagcomplex/get_transformation_data',
        data: data,
        dataType: "json",
        contentType: "application/json; charset=utf-8"
    })
        .done(function (data) {
            if (data["error"] !== 0) {
                alert(error_codes[data["error"]]);
                svg.selectAll("#point").remove();
                svg.selectAll("#line").remove();
                n = 0;
                hide_loader();
                switch_program_mode_to("addFlags");
            } else {
                trafo_range = data["trafo_range"];

                if (n === 3) {
                    switch_trafo_type_to("erupt");
                    trafo_data[trafo_type] = data["erupt"];
                }
                if (n === 4) {
                    switch_trafo_type_to("shear");
                    trafo_data["shear"] = data["shear"];
                    trafo_data["bulge"] = data["bulge"];
                    trafo_data["eruptmp"] = data["eruptmp"];
                    trafo_data["eruptpp"] = data["eruptpp"];
                    ellipse = data["ellipse"];
                }

                if (n > 4) {
                    t = 0;
                    t_str = "0";
                    switch_trafo_type_to("no_trafo");
                    trafo_data["no_trafo"] = data["no_trafo"];
                }


                refresh_coordinates();
                if (with_refresh) {
                    refresh_svg();
                }
                hide_loader();
                switch_program_mode_to("standard");
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
    update_points(ps_2dim, "p_point");
    for (let i = 0; i < us_2dim.length; i++) {
        update_points(us_2dim[i], "u_point" + i.toString());
        update_triangle(us_2dim[i], "u_line" + i.toString());
    }
    for (let i = 1; i < n - 1; i++) {
        var points = [ps_2dim[0], ps_2dim[i], ps_2dim[i + 1]];
        update_triangle(points, "p_line" + (i - 1).toString());
    }
    update_helper_lines(ps_2dim, qs_2dim, "helper_line");
    update_infinite_lines(ps_2dim, ds_2dim, "line");

    update_polygon(convex, "convex");
}

/**
 * Draws infinite lines through points data0[i] and data1[i] for all i. An infinite line not only
 * connects the two points, but stretches over the whole canvas.
 *
 * @param data0: an array of 2-dim arrays (point coordinates)
 * @param data1: another array of 2-dim arrays (point coordinates)
 * @param id: an id string for identifying the lines later
 * @param color: a color string specifying the object's color
 * @param layer: the layer to which the lines will be saved (i.e. a group of the svg element)
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
 * @param layer: the layer to which the points will be saved (i.e. a group of the svg element)
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
 * or more generally also draws a polygon.
 *
 * @param data: a 3-dim array of 2-dim arrays
 * @param id: an id string for identifying the triangle's lines later
 * @param color: a color string specifying the object's color
 * @param layer: the layer to which the lines will be saved (i.e. a group of the svg element)
 */
function draw_triangle(data, id, color, layer) {
    for (let i = 0; i < data.length; i++) {
        layer.append("line")
            .attr("id", id)
            .style('stroke', color)
            .attr("x1", data[i][0])
            .attr("y1", data[i][1])
            .attr("x2", data[(i + 1) % data.length][0])
            .attr("y2", data[(i + 1) % data.length][1]);
    }
}

/**
 * draws helper lines between the points in the middle triangle and in the outer triangle
 *
 * @param data_middle: a 3-dim array of 2-dim arrays (the middle triangle)
 * @param data_outer: a 3-dim array of 2-dim arrays (the outer triangle)
 * @param id: an id string for identifying the lines later
 * @param color: a color string specifying the object's color
 * @param layer: the layer to which the lines will be saved (i.e. a group of the svg element)
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
 * draws a filled polygon along the points specified in data
 *
 * @param data: an array of 3-dim arrays
 * @param id: an id string for identifying the polygon later
 * @param color: a color string specifying the object's color
 * @param layer: the layer to which the polygon will be saved (i.e. a group of the svg element)
 */
function draw_polygon(data, id, color, layer) {
    layer.selectAll(id)
        .data([data])
        .enter().append("polygon")
        .attr("id", id)
        .attr("points", function (d) {
            return d.map(function (d) {
                return [d[0], d[1]].join(",");
            }).join(" ");
        })
        .attr("stroke", color)
        .attr("stroke-width", 1)
        .attr("fill", color)
        .attr("fill-opacity", 0.1);

}

/**
 * updates the objects coordinates
 *
 * @param data
 * @param id
 */
function update_polygon(data, id) {
    svg.selectAll("#" + id)
        .data([data])
        .attr("points", function (d) {
            return d.map(function (d) {
                return [d[0], d[1]].join(",");
            }).join(" ");
        });
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
    let l = data.length;
    let index = [];
    for (let i = 0; i < l; i++) {
        index.push(i);
    }
    svg.selectAll("#" + id)
        .data(index)
        .attr("x1", function (i) {
            return data[i][0];
        })
        .attr("y1", function (i) {
            return data[i][1];
        })
        .attr("x2", function (i) {
            return data[(i + 1) % l][0];
        })
        .attr("y2", function (i) {
            return data[(i + 1) % l][1];
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
    // Reset transformation slider to zero
    reset_slider();
    // Uncheck all checkboxes
    $("input:checkbox").attr('checked', false);
    // Hide all edigitng elements
    ui_elements["all_elements"].forEach(function (item, index) {
        document.getElementById(item).style.display = "none";
    });  
}

/**
 * hides the little loading circle
 */
function hide_loader() {
    document.getElementById('loader-flags').style.display = "none";
}

/**
 * displays interactive sliders and buttons
 */
function show_editing_elements() {
    // UI elements that are only displayed for this particular number of flags n.
    if (Object.keys(ui_elements).includes(n.toString())) {
        ui_elements[n.toString()].forEach(function (item, index) {
            document.getElementById(item).style.display = "block";
        });
    }
    // UI elements that are displayed for all numbers of flags.
    ui_elements["show_for_all_n"].forEach(function (item, index) {
        document.getElementById(item).style.display = "block";
    });
    if (n === 3) {
        select_trafo.options[select_trafo.selectedIndex].value = "erupt";
    }
    if (n === 4) {
        select_trafo.options[select_trafo.selectedIndex].value = "shear";
        document.getElementById('input-withellipse').style.display = "block";
    }
}

/**
 * displays the loading circle (during loading data from the server)
 */
function show_loader() {
    document.getElementById('b-hinttype').style.display = "none";
    document.getElementById('span-modeinfo').innerHTML = "Loading transformation data. May take up to 25s.";
    document.getElementById('loader-flags').style.display = "block";
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
    /*
     * In fact, for our purpose it is not important that the intersection points
     * really lie exactly on the canvas. They just need to lie outside the canvas.
     * Therefore, we consider the vectors t*(point1-point0)+ point0 for all t.
     * They describe the line passing to point1 and point0. Now we only need to
     * choose t big (and small) enough in order to get out of the canvas.
     *
     * This simplification reduces rounding errors in comparison to the calculation
     * of the precise intersection points.
     */
    var diff = [point1[0] - point0[0], point1[1] - point0[1]];

    var t = 0;

    if (diff[0] !== 0 && diff[1] !== 0) {
        t = Math.max(Math.abs((width + point0[0]) / diff[0]), Math.abs((height + point0[1]) / diff[1]));
    } else if (diff[0] !== 0) {
        t = Math.abs((width + point0[0]) / diff[0]);
    } else if (diff[1] !== 0) {
        t = Math.abs((height + point0[1]) / diff[1]);
    } else {
        return [point0, point1]
    }

    t = order_of_magnitude(t)*5;
    return [[t * diff[0] + point0[0], t * diff[1] + point0[1]], [-t * diff[0] + point0[0], -t * diff[1] + point0[1]]];
}

/**
 * Returns the order of magnitude for a float n, e.g. for n = 104634, we get 100000.
 * @param n
 * @returns {number}
 */
function order_of_magnitude(n) {
    var order = Math.floor(Math.log(n) / Math.LN10
        + 0.000000001); // because float math sucks like that
    return Math.pow(10, order);
}


/**
 * Saves the svg object to an svg file
 *
 * @param svgEl: the d3.js svg object
 * @param name: the file name
 */
function saveSvg(svgEl, name) {
    svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    var svgData = svgEl.outerHTML;
    console.log(svgData);
    var preface = '<?xml version="1.0" standalone="no"?>\r\n';
    var svgBlob = new Blob([preface, svgData], {type: "image/svg+xml;charset=utf-8"});
    var svgUrl = URL.createObjectURL(svgBlob);
    var downloadLink = document.createElement("a");
    downloadLink.href = svgUrl;
    downloadLink.download = name;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}






