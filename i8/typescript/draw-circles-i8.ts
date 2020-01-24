const maxLevels = 5;
var radius = 100;
var size = maxLevels * 4;

var svg = (
    d3.select("body").append("svg")
      .attr("width", radius*size)
      .attr("height", radius*size)
);

// Recursively Add circles around middle circle ...
var circle = new Circle(radius*size/2, radius*size/2,radius*2/5.25);

var circles = (circle).surroundWithFlowersRecursively(maxLevels);
_.forEach(
    circles,
    c => {
        console.log("appending c", c);
        appendCircleWithMidpoint(<d3SVG>svg, c, maxLevels);
        // appendPolygon(<d3SVG>svg, c.hexagonWithinCircle());
    }
);

appendCircleWithMidpoint(<d3SVG>svg, circle);

// ---------------------- ---------------------- ---------------------- ----------------------

var svg2 = (
    d3.select("body").append("svg")
      .attr("width", radius*size)
      .attr("height", radius*size)
);

// Add middle circle
var central = new Circle(radius*size/2, radius*size/2, radius);
appendCircleWithMidpoint(<d3SVG>svg2, central, maxLevels);

var circles = _.concat(
    new Circle(radius*size/2, radius*size/2,radius*2/5.25).surroundingCircles(8, 2.625, Math.PI/2/2/2),
    new Circle(radius*size/2, radius*size/2,radius*2/5.25).surroundingCircles(8, 2.625),
);

// Append circles for midpoints only ...
_.forEach(
    circles,
    c => {
        console.log("appending c", c);
        appendCircleWithMidpoint(<d3SVG>svg2, c, maxLevels);
    }
);

_.forEach(
    circles,
    c => {
        var line = Circle.lineBetweenMidpoints(central, c).extendLine(radius*2);
        appendLine(<d3SVG>svg2, line);
    }
);

// ------------------------
var svg3 = (
    d3.select("body").append("svg")
      .attr("width", radius*size)
      .attr("height", radius*size)
);

var centralWithHex = new Circle(radius*size/2, radius*size/2, radius);
appendPolygon(<d3SVG>svg3, centralWithHex.hexagonWithinCircle());

_.forEach(
    centralWithHex.surroundingCircles(6, 0.5, 0),
    (c) => {
        appendPolygon(<d3SVG>svg3, c.hexagonWithinCircle());
    }
)


var svg4 = (
    d3.select("body").append("svg")
      .attr("width", radius*size)
      .attr("height", radius*size)
);

_.forEach(
    centralWithHex.surroundingCircles(6, 1, 0),
    (c) => {
        appendPolygon(<d3SVG>svg4, c.hexagonWithinCircle());
    }
)

_.forEach(
    centralWithHex.surroundingCircles(6, 1, 0),
    (c) => {
        appendPolygon(<d3SVG>svg4, c.hexagonWithinCircle(0));
    }
)