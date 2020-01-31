const maxLevels = 2;
var radius = 100;
var size = maxLevels * 4;


// eslint-disable-next-line no-unused-vars
function drawDifferentPolygons() {
    var svg:d3SVG;
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
    var star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    var svg = <d3SVG> (d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
    appendPolygon(svg, star.lines);
    appendPolygon(svg, star.rotate(Math.PI/2).lines);
    appendPolygon(svg, Hexagon.withinCircle(star.outerCircle).lines);
    appendPolygon(svg, star.right().lines);
    appendPolygon(svg, star.right().rotate(Math.PI/2).lines);
    appendPolygon(svg, Hexagon.withinCircle(star.right().outerCircle).lines);
    appendPolygon(svg, star.above().lines);
    appendPolygon(svg, star.above().rotate(Math.PI/2).lines);
    appendPolygon(svg, Hexagon.withinCircle(star.above().outerCircle).lines);
    appendPolygon(svg, star.above().right().lines);
    appendPolygon(svg, star.above().right().rotate(Math.PI/2).lines);
    appendPolygon(svg, Hexagon.withinCircle(star.above().right().outerCircle).lines);
}
// eslint-disable-next-line no-unused-vars
function drawRotatedStar() {
    var star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    var svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
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
    var star:Star;
    var svg:d3SVG;
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

// eslint-disable-next-line no-unused-vars
function rotateOuterCircles(centralCircle:Circle, currentShift:number, outerCirclesSVGS:d3CIRCLE[]) {
    var newShift = currentShift + 1;
    console.log("Current shfit", newShift);
    var newOuterCircles = centralCircle.surroundingCircles(6, 1, (newShift/10)*Math.PI*2/6);
    _.forEach(
        _.zip(newOuterCircles, outerCirclesSVGS),
        ([newCircle, circleToTransition]) => {
            (<d3CIRCLE>circleToTransition)
                .transition()
                .ease(d3.easeLinear)
                .duration(50)
                .attr('cx', (<Circle>newCircle).x)
                .attr('cy', (<Circle>newCircle).y)
                .attr('r', (<Circle>newCircle).r);
        }
    )
    return <[number,Circle[]]>[newShift, newOuterCircles];
}

// eslint-disable-next-line no-unused-vars
function drawRotatingCircles() {
    var svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
    var centralCircle = new Circle(radius * size / 2, radius * size / 2, radius);
    // var centralSVGS = appendCircle(svg, centralCircle);
    var currentShift = 0;
    var outerCircles = centralCircle.surroundingCircles(6, 1, currentShift*Math.PI*2/6);
    var outerCirclesSVGS = <d3CIRCLE[]>(_.map(outerCircles, c => appendCircle(svg, c)));
    var outerCirclesL2 = _.flatMap(
        centralCircle.surroundingCircles(6, 1, currentShift*Math.PI*2/6),
        c => c.surroundingCircles(6, 1, currentShift*Math.PI*2/6)
    );
    _.map(outerCirclesL2, c => appendCircle(svg, c));

    // I wanted the central ring to completely rotate ... but the problem with the flowers ... is that they get drawn by other surrounding circles ...
    setInterval(function () {
        [currentShift, outerCircles] = rotateOuterCircles(centralCircle, currentShift, outerCirclesSVGS);
    }, 50);
}

// // eslint-disable-next-line no-unused-vars
// function drawHexagonWithSurroundingNonagons() {
//     // var svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
//     var svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size).style("background", "RGBA(118,215,196,0.9)"));
//     var centralCircle = new Circle(radius * size / 2, radius * size / 2, radius);
//     var outerCircles = centralCircle.surroundingCircles(6, 1);
//     // appendPolygon(svg, new Hexagon(centralCircle.midpoint, centralCircle.r).lines);
//     var surroundingPolygons = _.map(outerCircles, c => new Nonagon(c.midpoint, centralCircle.r * 0.75));
//     // Rotate every other polygon ...
//     surroundingPolygons = _map_even_odd(
//         surroundingPolygons,
//         nonagon => (<Nonagon>nonagon).rotate(Math.PI),
//     );
//     _.forEach(surroundingPolygons, p => {
//         appendPolygon(svg, p.lines, {
//             // "fill": "RGBA(118,215,196,0.5)",
//             // "fill": "RGBA(118,215,196,0.75)",
//             "stroke": "RGB(244,208,63)",
//             "stroke-width": "5",
//         });
//     });
// }


function nonagonsThatFormA6PointStarCenteredAt(centralHexagon:Hexagon) {
    var centralCircle = centralHexagon.outerCircle;
    var outerCircles = centralCircle.surroundingCircles(6, 1);
    // appendPolygon(svg, new Hexagon(centralCircle.midpoint, centralCircle.r).lines);
    var surroundingPolygons = _.map(outerCircles, function (c) { return new Nonagon(c.midpoint, centralCircle.r * 0.75); });
    // Rotate every other polygon ...
    surroundingPolygons = _map_even_odd(surroundingPolygons, function (nonagon) { return nonagon.rotate(Math.PI); });
    return _.concat(
        // Nonagons
        surroundingPolygons,
        // Hexagons
        centralHexagon
    );
}

// eslint-disable-next-line no-unused-vars
function drawHexagonWithSurroundingNonagons() {
    // var svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
    var svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size).style("background", "RGBA(118,215,196,0.9)"));
    var circle = new Circle(radius * size / 2, radius * size / 2, radius);
    var circles = [
        // - [ ] How do I make this cleaner ...?
        // https://medium.com/@rossbulat/typescript-generics-explained-15c6493b510f
        Hexagon.withinCircle<Hexagon>(circle).northWest(),
        Hexagon.withinCircle<Hexagon>(circle).northEast(),
        Hexagon.withinCircle<Hexagon>(circle).above(),
        Hexagon.withinCircle<Hexagon>(circle),
        Hexagon.withinCircle<Hexagon>(circle).below(),
        Hexagon.withinCircle<Hexagon>(circle).southWest(),
        Hexagon.withinCircle<Hexagon>(circle).southEast(),


        // circle.southEast().above(),
        // circle.southEast().below(),
        // circle.southEast().southEast(),
        // circle.southEast().southEast().above(),
        // circle.above().southEast(),
        // circle.left(),
    ];
    _.forEach(
        _.flatMap(
            circles,
            nonagonsThatFormA6PointStarCenteredAt
        ),
        function (p) {
            appendPolygon(svg, p.lines, {
                // "fill": "RGBA(118,215,196,0.5)",
                // "fill": "RGBA(118,215,196,0.75)",
                "stroke": "RGB(244,208,63)",
                "stroke-width": "5",
            });
        }
    );
}


// eslint-disable-next-line no-unused-vars
function drawCirclesRecursively() {
    var svg = <d3SVG>(
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
            appendPolygon(<d3SVG>svg, Hexagon.withinCircle(c).lines);
        }
    );
    // appendCircleWithMidpoint(<d3SVG>svg, circle);
}


// do drawHexagonWithSurroundingNonagons but in a grid ...
// do the whole draw outer ring so I can roteate inner ring!

// drawCirclesRecursively();
drawHexagonWithSurroundingNonagons();
// drawRotatingCircles();
// drawDifferentPolygons();
// drawStarGrid();
// drawRotatedStar();
// drawDifferentStars();
