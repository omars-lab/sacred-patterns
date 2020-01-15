const maxLevels = 2;
// const existantCircles = {};
var radius = 100;
var size = maxLevels * 4;

var svg = (
    d3.select("body").append("svg")
      .attr("width", radius*size)
      .attr("height", radius*size)
);

// Recursively Add circles around middle circle ...
var circles = (new Circle(radius*size/2, radius*size/2,radius*2/5.25, {})).surroundWithFlowersRecursively(maxLevels);
_.forEach(
    circles,
    c => {
        console.log("appending c", c);
        appendCircleWithMidpoint(svg, c);
    }
);

// ---------------------- ---------------------- ---------------------- ----------------------

var svg2 = (
    d3.select("body").append("svg")
      .attr("width", radius*size)
      .attr("height", radius*size)
);

// Add middle circle
central = new Circle(radius*size/2, radius*size/2, radius);
appendCircleWithMidpoint(svg2, central);

var circles = new Circle(radius*size/2, radius*size/2,radius*2/5.25).surroundingCircles(8, 2.625, Math.PI/2/2/2);

// Append circles for midpoints only ...
_.forEach(
    circles,
    c => {
        console.log("appending c", c);
        appendCircleWithMidpoint(svg2, c);
    }
);

_.forEach(
    circles,
    c => {
        var line = Circle.lineBetweenMidpoints(central, c).extendLine(radius*2);
        appendLine(svg2, line);
    }
);

// Append circles for midpoints only ...
circles = new Circle(radius*size/2, radius*size/2,radius*2/5.25).surroundingCircles(8, 2.625);

_.forEach(circles,
   c => {
       console.log("appending c", c);
       appendCircleWithMidpoint(svg2, c);
   }
);

_.forEach(circles,
    c => {
        var line = Circle.lineBetweenMidpoints(central, c).extendLine(radius*2);
        appendLine(svg2, line);
    }
);
