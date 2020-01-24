"use strict";
var maxLevels = 5;
var radius = 100;
var size = maxLevels * 4;
var svg;
var star = null;
// eslint-disable-next-line no-unused-vars
function drawDifferentPolygons() {
    _.forOwn(PolygonWithSides, function (cls, num_sides) {
        console.log(cls, num_sides);
        svg = (d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
        appendPolygon(svg, new cls(new Point(radius * size / 2, radius * size / 2), radius).lines);
        // appendCircleWithMidpoint(svg, star.outerCircle);
    });
}
// eslint-disable-next-line no-unused-vars
function drawStarGrid() {
    star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    svg = (d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
    appendPolygon(svg, star.lines);
    appendPolygon(svg, star.rotate(Math.PI / 2).lines);
    appendPolygon(svg, Hexagon.onCircle(star.outerCircle).lines);
    appendPolygon(svg, star.right().lines);
    appendPolygon(svg, star.right().rotate(Math.PI / 2).lines);
    appendPolygon(svg, Hexagon.onCircle(star.right().outerCircle).lines);
    appendPolygon(svg, star.above().lines);
    appendPolygon(svg, star.above().rotate(Math.PI / 2).lines);
    appendPolygon(svg, Hexagon.onCircle(star.above().outerCircle).lines);
    appendPolygon(svg, star.above().right().lines);
    appendPolygon(svg, star.above().right().rotate(Math.PI / 2).lines);
    appendPolygon(svg, Hexagon.onCircle(star.above().right().outerCircle).lines);
}
// eslint-disable-next-line no-unused-vars
function drawRotatedStar() {
    star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    svg = (d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
    appendPolygon(svg, star.rotate(Math.PI / 4).lines);
    _.forEach(star.rotate(Math.PI / 4).circles, function (c) {
        appendCircleWithMidpoint(svg, c);
        true;
    });
}
// eslint-disable-next-line no-unused-vars
function drawDifferentStars() {
    _.forEach(_.range(6, 12, 1), function (points) {
        star = new Star(new Point(radius * size / 2, radius * size / 2), points, radius);
        svg = (d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
        appendPolygon(svg, star.lines);
        appendCircleWithMidpoint(svg, star.outerCircle);
    });
}
var svg = (d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
var centralCircle = new Circle(radius * size / 2, radius * size / 2, radius);
var centralSVGS = appendCircle(svg, centralCircle);
var currentShift = 0;
var outerCircles = centralCircle.surroundingCircles(6, 1, currentShift * Math.PI * 2 / 6);
var outerCirclesSVGS = (_.map(outerCircles, function (c) { return appendCircle(svg, c); }));
var outerCirclesL2 = _.flatMap(centralCircle.surroundingCircles(6, 1, currentShift * Math.PI * 2 / 6), function (c) { return c.surroundingCircles(6, 1, currentShift * Math.PI * 2 / 6); });
var outerCirclesSVGSL2 = (_.map(outerCirclesL2, function (c) { return appendCircle(svg, c); }));
// eslint-disable-next-line no-unused-vars
function drawCircles() {
    _.forEach(_.range(6, 12, 1), function (points) {
        star = new Star(new Point(radius * size / 2, radius * size / 2), points, radius);
        svg = (d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
        appendPolygon(svg, star.lines);
        appendCircleWithMidpoint(svg, star.outerCircle);
    });
}
function rotateOuterCircles() {
    currentShift = currentShift + 1;
    console.log("Current shfit", currentShift);
    var newOuterCircles = centralCircle.surroundingCircles(6, 1, (currentShift / 10) * Math.PI * 2 / 6);
    _.forEach(_.zip(newOuterCircles, outerCirclesSVGS), function (_a) {
        var newCircle = _a[0], circleToTransition = _a[1];
        circleToTransition
            .transition()
            .ease(d3.easeLinear)
            .duration(50)
            .attr('cx', newCircle.x)
            .attr('cy', newCircle.y)
            .attr('r', newCircle.r);
    });
    outerCircles = newOuterCircles;
}
// I wanted the central ring to completely rotate ... but the problem with the flowers ... is that they get drawn by other surrounding circles ...
setInterval(rotateOuterCircles, 50);
// drawDifferentPolygons();
// drawStarGrid();
// drawRotatedStar();
// drawDifferentStars();
