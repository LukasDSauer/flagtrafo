function refreshCanvas() {
    updatePoints(ps_2dim, "#point");
    updatePoints(us_2dim, "#u_point");
    updatePoints(ps_2dim, "#p_point")
    updateTriangle(us_2dim, "#u_line");
    updateTriangle(ps_2dim, "#p_line");
    updateHelperLines(ps_2dim, qs_2dim, "#helper_line")

    var line_data = [];

    for (var i = 0; i < n; i++) {
        var intersectionPoints = getIntersectionWithFrame(ps_2dim[i], ds_2dim[i]);
        line_data.push({
            "x1": intersectionPoints[0][0], "y1": intersectionPoints[0][1],
            "x2": intersectionPoints[1][0], "y2": intersectionPoints[1][1]
        });

    }

    svg.selectAll("#line")
        .data(line_data)
        .attr("x1", function (d) {return d["x1"];})
        .attr("y1", function (d) {return d["y1"];})
        .attr("x2", function (d) {return d["x2"];})
        .attr("y2", function (d) {return d["y2"];})
}

function hideEditingElements(){
    document.getElementById('add_flag_buttonb').style.display = "none";
    document.getElementById('checkboxes-triangle').style.display = "none";
    document.getElementById('transformator').style.display = "none";
    document.getElementById('proj-plane-form').style.display = "none";
}
function hideLoader(){
    document.getElementById('loader-flags').style.display = "none";
}

function showEditingElements() {
    document.getElementById('add_flag_buttonb').style.display = "block";
    document.getElementById('checkboxes-triangle').style.display = "block";
    document.getElementById('transformator').style.display = "block";
    document.getElementById('proj-plane-form').style.display = "inline";
}
function showLoader(){
    document.getElementById('loader-flags').style.display = "block";
}

function submitFlagsToServer(){
    console.info("Sending flags to server!");

        hideEditingElements();
        showLoader();
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
                //console.log(data);
                trafo_data = data;
                ps_2dim = trafo_data[t_str]["ps"];
                qs_2dim = trafo_data[t_str]["qs"];
                // From now on, we can use the qs for the ds, as they simply are another point on the line,
                // and this is all that we need.
                ds_2dim = trafo_data[t_str]["qs"];
                us_2dim = trafo_data[t_str]["us"];
                hideLoader();
                showEditingElements();
                document.getElementById('hint-type').style.display = "inline";
                document.getElementById('mode-description').innerHTML =
            "Move slider to transform.";
            });
}

function submitFlagsButton() {
    if (program_mode == "addPoints" || program_mode == "addLines") {
        submitFlagsToServer();
    }
    else if (program_mode== "standard"){
        console.info("Add flag mode!")
        program_mode = "addPoints";
        hideEditingElements();
        document.getElementById('add_flag_buttonb').value = "Finish";
        svg.on("mousemove", mouseMovePointOrLine)
            .on("click", mouseClickPointOrLine);
    }
}

function getIntersectionWithFrame(point1, point2) {
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

function mouseMovePointOrLine(){
    liveCoordinates = d3.mouse(this);

            if (program_mode == "addPoints") {
                addPoint(liveCoordinates);
            } else if (program_mode == "addLines") {
                addLine(fixedCoordinates, liveCoordinates);
            }
}

function mouseClickPointOrLine(){
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


function addPoint(coordinates) {
    var x = coordinates[0];
    var y = coordinates[1];

    data = [{"x": x, "y": y}];

    var circle = svg.selectAll("#newpoint")
        .data(data);

    circle.exit().remove();

    circle.enter().append("circle")
        .attr("id", "newpoint")
        .attr("r", 2.5)
        .merge(circle)
        .style('stroke', '#007979')
        .style('fill', '#006969')
        .attr("cx", function (d) {
            return d.x;
        })
        .attr("cy", function (d) {
            return d.y;
        });

    d3.event.preventDefault();
}

function addLine(fixedCoordinates, liveCoordinates) {
    var intersectionPoints = getIntersectionWithFrame(fixedCoordinates, liveCoordinates);
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

function submitProjectionPlane() {
            proj_plane = [parseFloat($("#ppx").val()),
                parseFloat($("#ppy").val()),
                parseFloat($("#ppz").val())];
            submitFlagsToServer();
            refreshCanvas();
            document.getElementById("pplane-value").innerHTML = "("+proj_plane[0]+", "+proj_plane[1]+", "+proj_plane[2]+")";
}

function drawPoints(data, id, color){
    var circle = svg.selectAll(id)
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

function drawTriangle(data, id, color){
    for (var i=0; data.length-1; i++){
        svg.append("line")
        .attr("id", id)
        .style('stroke', color)
        .attr("x1", data[i][0])
        .attr("y1", data[i][1])
        .attr("x2", data[(i+1)%3][0])
        .attr("y2", data[(i+1)%3][1]);
    }
}

function drawHelperLines(data_middle, data_outer, id, color){
    for (var i=0; data_middle.length-1; i++){
        svg.append("line")
        .attr("id", id)
        .style('stroke', color)
        .attr("x1", data_middle[i][0])
        .attr("y1", data_middle[i][1])
        .attr("x2", data_outer[(i+2)%3][0])
        .attr("y2", data_outer[(i+2)%3][1]);
    }
}

function updateTriangle(data, id){
    var index = [0, 1, 2];
    svg.selectAll(id)
        .data(index)
        .attr("x1", function(i){ return data[i][0];})
        .attr("y1", function(i){ return data[i][1];})
        .attr("x2", function(i){ return data[(i+1)%3][0];})
        .attr("y2", function(i){ return data[(i+1)%3][1];});
}

function updatePoints(data, id){
    svg.selectAll(id)
        .data(data)
        .attr("cx", function (d) {
            return d[0];
        })
        .attr("cy", function (d) {
            return d[1];
        });
}

function updateHelperLines(middle_data, outer_data, id) {
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


