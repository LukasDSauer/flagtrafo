/**
 * Listeners for buttons and sliders.
 */
function set_listeners()
{
    // The "Add flag" button
    $("#button-addflag").click(function () {
        submit_flags_button();
    });

    // The "Submit projection plane" button
    $("#button-pplane").click(function () {
        submit_projection_plane_button();
    });

    // The "Reset transformation" button
    $("#button-traforeset").click(function () {
        reset_slider();
        transform_coordinates();
    });

    // The "Save Svg" button
    $("#button-savesvg").click(function () {
        bottom_layer.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", width)
            .attr("height", height)
            .attr("id", "background")
            .attr("fill", "#DDDDDD");
        saveSvg(document.getElementById("svg"), "flag-transformator-img.svg");
        svg.selectAll("#background").remove();
    });

    // The slider for transformation
    slider.oninput = function () {
        t = this.value;
        transform_coordinates();
    };

    // The dropdown menu for transformation type
    select_trafo.onchange = function () {
        switch_trafo_type_to(select_trafo.options[select_trafo.selectedIndex].value);
        refresh_coordinates();
        refresh_svg(false);
    };

    // Checkbox for the inner triangle. Check for showing inner triangle, uncheck for removing.
    $('input[name=withInner]').change(function () {
        if ($(this).is(':checked')) {
            for (let i = 0; i < us_2dim.length; i++) {
                draw_points(us_2dim[i], "u_point" + i.toString(), FLAVOR_COLOR_1, triangle_layer);
                draw_triangle(us_2dim[i], "u_line" + i.toString(), FLAVOR_COLOR_1, triangle_layer);
            }
        } else {
            for (let i = 0; i < us_2dim.length; i++) {
                svg.selectAll("#u_point" + i.toString()).remove();
                svg.selectAll("#u_line" + i.toString()).remove();
            }
        }
    });

    // Checkbox for the middle triangle. Check for showing middle triangle, uncheck for removing.
    $('input[name=withMiddle]').change(function () {
        if ($(this).is(':checked')) {
            console.log(ps_2dim);
            console.log(n);
            for (let i = 1; i < n - 1; i++) {
                var points = [ps_2dim[0], ps_2dim[i], ps_2dim[i + 1]];
                draw_triangle(points, "p_line" + (i - 1).toString(), FLAVOR_COLOR_2, triangle_layer);
            }
            draw_points(ps_2dim, "p_point", FLAVOR_COLOR_2, triangle_layer);
        } else {
            svg.selectAll("#p_point").remove();
            for (let i = 1; i < n - 1; i++) {
                svg.selectAll("#p_line" + (i - 1).toString()).remove();
            }
        }
    });

    // Checkbox for the helper lines. Check for showing, uncheck for removing.
    $('input[name=withHelper]').change(function () {
        if ($(this).is(':checked')) {
            draw_helper_lines(ps_2dim, qs_2dim, "helper_line", FLAVOR_COLOR_3, background_layer);
        } else {
            svg.selectAll("#helper_line").remove();
        }
    });

    // Checkbox for the ellipse. Check for showing, uncheck for removing.
    $('input[name=withEllipse]').change(function () {
        if ($(this).is(':checked')) {
            draw_triangle(ellipse, "ellipse", FLAVOR_COLOR_3, background_layer);
        } else {
            svg.selectAll("#ellipse").remove();
        }
    });

    // Checkbox for the convex set. Check for showing, uncheck for removing.
    $('input[name=withConvex]').change(function () {
        if ($(this).is(':checked')) {
            draw_polygon(convex, "convex", FLAVOR_COLOR_4, background_layer);
        } else {
            svg.selectAll("#convex").remove();
        }
    });
}

/**
 * Resets the transformation slider to 0, and all its implied values.
 */
function reset_slider()
{
    t = 0;
    slider.value = 0;
    document.getElementById("trafovalue").innerHTML = "0"; // Display the default slider value   
}