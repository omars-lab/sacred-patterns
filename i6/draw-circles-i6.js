const maxLevels = 1;
// const existantCircles = {};
var radius = 100;
var size = maxLevels * 4;

function circlesAround(c, count, level, distance_modifier=1, shift_in_radians=0) {
    const {x, y, r} = c;
    var circles = _.map(
        _.range(0, 2 * Math.PI, 2 * Math.PI / count),
        radians => circle(
            x + (Math.cos(radians + shift_in_radians) * r * distance_modifier),
            y + (Math.sin(radians + shift_in_radians) * r * distance_modifier),
            r,
            level
        )
    );
    // console.log(c, circles);
    return circles;
}

var svg = (
    d3.select("body").append("svg")
      .attr("width", radius*size)
      .attr("height", radius*size)
);

// Add middle circle
central = _.values(circle(radius*size/2, radius*size/2, radius))[0];
appendCircleWithMidpoint(svg, central);

// Recursively Add circles around middle circle ...
var circles = _.merge(
    {},
    ...circlesAround({x:radius*size/2, y:radius*size/2, r:radius*2/5.25}, 8, maxLevels, 2.625, Math.PI/2/2/2)
);

_.forEach(
    _.values(circles),
    c => {
        console.log("appending c", c);
        appendCircleWithMidpoint(svg, c);
    }
);

_.forEach(
    _.values(circles),
    c => {
        var [x1, y1] = extendLine([central.x, central.y], [c.x, c.y], radius*3);
        console.log("Drawing Line From", [central.x, central.y], " to ", [x1, y1]);
        svg.append("line")
           .attr("x1", central.x)
           .attr("y1", central.y)
           .attr("x2", x1)
           .attr("y2", y1)
           .attr("class","line")
           .style("stroke", "black");
    }
);


// Append circles for midpoints only ...
circles = _.merge(
   {},
   ...circlesAround({x:radius*size/2, y:radius*size/2, r:radius*2/5.25}, 8, undefined, 2.625)
);

console.log(circles, _.values(circles));

_.forEach(
   _.values(circles),
   c => {
       console.log("appending c", c);
       appendCircleWithMidpoint(svg, c);
   }
);

_.forEach(
    _.values(circles),
    c => {
        var [x1, y1] = extendLine([central.x, central.y], [c.x, c.y], radius*3);
        console.log("Drawing Line From", [central.x, central.y], [x1, y1]);
        svg.append("line")
           .attr("x1", central.x)
           .attr("y1", central.y)
           .attr("x2", x1)
           .attr("y2", y1)
           .attr("class","line")
           .style("stroke", "black");
    }
);

// Make circle methods ...
// polar_slices()
// virticle slices ...
// horizontal slices ...


// Additional changes needed ... simplify all the different operations that can be done ...
// Circle ... get Id ... connect midpoints of two different circles ...
// - [ ] Make 3 layers of circles in each other ...


// Add verticle bars to circle ...
