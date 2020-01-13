const maxLevels = 1;
// const existantCircles = {};
var radius = 100;
var size = maxLevels * 4;

function inQuadrant1(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (x2 >= x1) && (y2 >= y1)
}

function inQuadrant2(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (x2 <= x1) && (y2 >= y1)
}

function inQuadrant3(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (x2 <= x1) && (y2 <= y1)
}

function inQuadrant4(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (x2 >= x1) && (y2 <= y1)
}


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

function extendLineRight(p1, p2, newDistance) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    var slope = (y2 - y1) / (x2 - x1);
    console.log("extending line right", slope);
    // horizontal
    if (y2 === y1 || Math.abs(slope) < (1.0/1000000.0) ) {
        return [x1+newDistance, y1];
    }

    var x = 0;
    var y = 0;
    var currentDistance = Math.sqrt(Math.pow(x2-x1, 2) + Math.pow(y2-y1, 2));

    if (slope > 0) {
        x = x1 + ((newDistance*Math.abs(x2-x1))/currentDistance);
        y = y1 + ((newDistance*Math.abs(y2-y1))/currentDistance);
    }
    else {
        x = x1 + ((newDistance*Math.abs(x2-x1))/currentDistance);
        y = y1 - ((newDistance*Math.abs(y2-y1))/currentDistance);
    }
    return [
        x,
        y
    ];
}

function extendLineLeft(p1, p2, newDistance) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    var slope = (y2 - y1) / (x2 - x1);
    console.log("extending line left", slope);
    // horizontal
    if (y2 === y1 || Math.abs(slope) < (1.0/1000000.0)) {
        return [x1-newDistance, y1];
    }

    var x = 0;
    var y = 0;
    // https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
    var currentDistance = Math.sqrt(Math.pow(x2-x1, 2) + Math.pow(y2-y1, 2));
    if (slope > 0) {
        x = x1 - ((newDistance*Math.abs(x2-x1))/currentDistance);
        y = y1 - ((newDistance*Math.abs(y2-y1))/currentDistance);
    }
    else {
        x = x1 - ((newDistance*Math.abs(x2-x1))/currentDistance);
        y = y1 + ((newDistance*Math.abs(y2-y1))/currentDistance);
    }
    return [
        x,
        y
    ];
}

function extendLine(p1, p2, newDistance=radius*3) {
    console.log("Extending line between", p1, p2);
    var [x1, y1] = p1;
    var [x2, y2] = p2;

    // y2 = x2 * slope
    // vertical
    var slope = (y2 - y1) / (x2 - x1);
    if (x1 === x2 || Math.abs(slope) > 1000000) {
        // y2 under y1 ...
        if (y2 < y1) {
            return [x2, y1-newDistance];
        }
        return [x2, y1+newDistance];
    }
    if (inQuadrant2(p1, p2) || inQuadrant3(p1, p2)) {
        return extendLineLeft(p1, p2, newDistance);
    }
    return extendLineRight(p1, p2, newDistance);
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
        var [x1, y1] = extendLine([central.x, central.y], [c.x, c.y]);
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
        var [x1, y1] = extendLine([central.x, central.y], [c.x, c.y]);
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
