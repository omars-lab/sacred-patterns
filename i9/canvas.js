"use strict";
// https://www.typescriptlang.org/docs/handbook/advanced-types.html
// https://www.logicbig.com/tutorials/misc/typescript/ts-config-json.html
// Introspecting types ...
// var x = d3.select("body");
// var x = d3.select("body").append("line");
// var x = d3.select("body").append("circle");
function colorForLevel(level, maxLevels) {
    console.log(level, maxLevels);
    // The higher the level ... the more clear ...
    if (_.isUndefined(level) || _.isUndefined(maxLevels)) {
        return 'red';
    }
    else {
        var color = 200 / ((200 / (maxLevels + 1)) * (level + 1));
        return "rgba(" + color + "," + color + "," + color + "," + Math.min(1, (level + 1) / (maxLevels + 1)) + ")";
    }
}
/* eslint-disable-next-line no-unused-vars, no-redeclare */
function appendCircleWithMidpoint(onto, c, maxLevels) {
    console.log("HIIIII", c, c.metadata, maxLevels);
    // Append Circle
    onto.append('circle')
        .attr('cx', c.x)
        .attr('cy', c.y)
        .attr('r', c.r)
        .attr('stroke', colorForLevel(c.metadata.level, maxLevels))
        // .attr('stroke', 'black')
        .attr('fill', 'none');
    // Append Midpoint
    onto.append('circle')
        .attr('cx', c.x)
        .attr('cy', c.y)
        .attr('r', 1)
        .attr('stroke', colorForLevel(c.metadata.level, maxLevels))
        // .attr('stroke', 'black');
        .attr('fill', colorForLevel(c.metadata.level, maxLevels));
}
// function applyStylesTo(to, styleParams, defaultStyleParams) {
//
// }
/* eslint-disable-next-line no-unused-vars, no-redeclare */
function appendCircle(onto, c, maxLevels) {
    console.log("HIIIII", c, c.metadata, maxLevels);
    // Append Circle
    return (onto.append('circle')
        .attr('cx', c.x)
        .attr('cy', c.y)
        .attr('r', c.r)
        .attr('stroke', _.get(c.metadata, "stroke", colorForLevel(c.metadata.level, maxLevels)))
        .attr('fill', _.get(c.metadata, "fill", 'none')));
}
/* eslint-disable-next-line no-unused-vars, no-redeclare */
function appendLine(onto, l, color) {
    if (color === void 0) { color = "black"; }
    console.log("Drawing Line From", l.p1, " to ", l.p2);
    onto.append("line")
        .attr("x1", l.p1.x)
        .attr("y1", l.p1.y)
        .attr("x2", l.p2.x)
        .attr("y2", l.p2.y)
        .attr("class", "line")
        .style("stroke", color);
}
/* eslint-disable-next-line no-unused-vars, no-redeclare */
function appendPolygon(onto, lines, metadata) {
    if (metadata === void 0) { metadata = {}; }
    // Assumes lines are in connected order ...
    if (_.isEmpty(lines)) {
        return;
    }
    var last_line = _.last(lines);
    var last_point = [last_line.p2.x, last_line.p2.y];
    // Skip over the ending points of the line ... except for the last line ...
    var points = _.concat(_.map(lines, function (l) { return [l.p1.x, l.p1.y]; }), [last_point]);
    var poly_points = _.join(_.map(points, function (p) { return _.join(p, ","); }), ", ");
    onto.append("polyline")
        .style('stroke', _.get(metadata, "stroke", "black"))
        .style('stroke-width', _.get(metadata, "stroke-width", "1"))
        .style('fill', _.get(metadata, "fill", 'none'))
        .attr("points", poly_points);
}
