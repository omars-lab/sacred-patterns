"use strict";
var maxLevels = 2;
var radius = 100;
var size = maxLevels * 4;
var svg = (d3.select("body").append("svg")
    .attr("width", radius * size)
    .attr("height", radius * size));
// Recursively Add circles around middle circle ...
var circles = (new Circle(radius * size / 2, radius * size / 2, radius * 2 / 5.25)).surroundWithFlowersRecursively(maxLevels);
_.forEach(circles, function (c) {
    console.log("appending c", c);
    appendCircleWithMidpoint(svg, c, maxLevels);
});
// ---------------------- ---------------------- ---------------------- ----------------------
var svg2 = (d3.select("body").append("svg")
    .attr("width", radius * size)
    .attr("height", radius * size));
// Add middle circle
var central = new Circle(radius * size / 2, radius * size / 2, radius);
appendCircleWithMidpoint(svg2, central, maxLevels);
var circles = _.concat(new Circle(radius * size / 2, radius * size / 2, radius * 2 / 5.25).surroundingCircles(8, 2.625, Math.PI / 2 / 2 / 2), new Circle(radius * size / 2, radius * size / 2, radius * 2 / 5.25).surroundingCircles(8, 2.625));
// Append circles for midpoints only ...
_.forEach(circles, function (c) {
    console.log("appending c", c);
    appendCircleWithMidpoint(svg2, c, maxLevels);
});
_.forEach(circles, function (c) {
    var line = Circle.lineBetweenMidpoints(central, c).extendLine(radius * 2);
    appendLine(svg2, line);
});
// ------------------------
var svg3 = (d3.select("body").append("svg")
    .attr("width", radius * size)
    .attr("height", radius * size));
var centralWithHex = new Circle(radius * size / 2, radius * size / 2, radius);
appendPolygon(svg3, centralWithHex.hexagonWithinCircle());
_.forEach(centralWithHex.surroundingCircles(6, 0.5, 0), function (c) {
    appendPolygon(svg3, c.hexagonWithinCircle());
});
var svg4 = (d3.select("body").append("svg")
    .attr("width", radius * size)
    .attr("height", radius * size));
_.forEach(centralWithHex.surroundingCircles(6, 1, 0), function (c) {
    appendPolygon(svg4, c.hexagonWithinCircle());
});
_.forEach(centralWithHex.surroundingCircles(6, 1, 0), function (c) {
    appendPolygon(svg4, c.hexagonWithinCircle(0));
});
