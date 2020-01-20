const maxLevels = 5;
var radius = 100;
var size = maxLevels * 4;
var svg:d3SVG;
var star = null;


// eslint-disable-next-line no-unused-vars
function drawDifferentPolygons() {
    _.forOwn(
        PolygonWithSides,
        (cls, num_sides) => {
            console.log(cls, num_sides);
            svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
            appendPolygon(svg, new cls(new Point(radius * size / 2, radius * size / 2), radius).lines);
            // appendCircleWithMidpoint(svg, star.outerCircle);
        }
    )
}
// eslint-disable-next-line no-unused-vars
function drawStarGrid() {
    star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    svg = <d3SVG> (d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
    appendPolygon(svg, star.lines);
    appendPolygon(svg, star.rotate(Math.PI/2).lines);
    appendPolygon(svg, Hexagon.onCircle(star.outerCircle).lines);
    appendPolygon(svg, star.right().lines);
    appendPolygon(svg, star.right().rotate(Math.PI/2).lines);
    appendPolygon(svg, Hexagon.onCircle(star.right().outerCircle).lines);
    appendPolygon(svg, star.above().lines);
    appendPolygon(svg, star.above().rotate(Math.PI/2).lines);
    appendPolygon(svg, Hexagon.onCircle(star.above().outerCircle).lines);
    appendPolygon(svg, star.above().right().lines);
    appendPolygon(svg, star.above().right().rotate(Math.PI/2).lines);
    appendPolygon(svg, Hexagon.onCircle(star.above().right().outerCircle).lines);
}
// eslint-disable-next-line no-unused-vars
function drawRotatedStar() {
    star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
    appendPolygon(svg, star.rotate(Math.PI/4).lines);
    _.forEach(
        star.rotate(Math.PI/4).circles,
        c => {
            appendCircleWithMidpoint(svg, c);
            true;
        }
    );
}

// eslint-disable-next-line no-unused-vars
function drawDifferentStars() {
    _.forEach(
        _.range(6, 12, 1),
        points => {
            star = new Star(new Point(radius * size / 2, radius * size / 2), points, radius);
            svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
            appendPolygon(svg, star.lines);
            appendCircleWithMidpoint(svg, star.outerCircle);
        }
    )
}

// drawDifferentPolygons();
// drawStarGrid();
// drawRotatedStar();
// drawDifferentStars();
