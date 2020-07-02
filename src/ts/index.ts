import * as _ from "lodash";
import {Circle} from "./circles"
import {Hexagon, Nonagon, Polygon, PolygonWithSides} from "./polygons"
import {Point} from "./points"
import {Star, FivePointStar} from "./star"
import * as d3 from 'd3'
import {_map_even_odd} from "./helpers"
// import {isEven} from "./helpers"
import {appendText, appendPolygon, appendCircle, appendCircleWithMidpoint, d3SVG, d3CIRCLE} from "./canvas"
import {IO} from "./types"


export function appendSVGToDOM(id: string, width:number, height:number): d3SVG {
    return <d3SVG>(
        d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("id", id)
    );
}

// eslint-disable-next-line no-unused-vars
export function rotateOuterCircles(centralCircle:Circle, currentShift:number, outerCirclesSVGS:d3CIRCLE[]): [number, Circle[]] {
    const newShift = currentShift + 1;
    console.log("Current shfit", newShift);
    const newOuterCircles = centralCircle.surroundingCircles(6, 1, (newShift/10)*Math.PI*2/6);
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

export function surroundingHexagons(circle:Circle): Hexagon[] {
    return [
        // - [ ] How do I make this cleaner ...?
        // https://medium.com/@rossbulat/typescript-generics-explained-15c6493b510f
        Hexagon.withinCircle<Hexagon>(circle).northWest(),
        Hexagon.withinCircle<Hexagon>(circle).northEast(),
        Hexagon.withinCircle<Hexagon>(circle).above(),
        Hexagon.withinCircle<Hexagon>(circle).below(),
        Hexagon.withinCircle<Hexagon>(circle).southWest(),
        Hexagon.withinCircle<Hexagon>(circle).southEast(),
    ];
}

export function nonagonsThatFormA6PointStarCenteredAt(centralHexagon:Hexagon): Polygon[] {
    const centralCircle = centralHexagon.outerCircle;
    const outerCircles = centralCircle.surroundingCircles(6, 1);
    // appendPolygon(svg, new Hexagon(centralCircle.midpoint, centralCircle.r).lines);
    let surroundingPolygons = _.map(
        outerCircles,
        function (c) {
            return new Nonagon(c.midpoint, centralCircle.r * 0.75);
        }
    );
    // Rotate every other polygon ...
    surroundingPolygons = _map_even_odd(
        surroundingPolygons,
        function (nonagon) {
            return nonagon.rotate(Math.PI);
        }
    );
    return _.concat(
        // Nonagons
        surroundingPolygons,
        // Hexagons
        centralHexagon
    );
}

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------


// eslint-disable-next-line no-unused-vars
export function drawDifferentPolygons(drawingId:string, radius:number, size:number) : IO {
    let svg:d3SVG;
    _.forOwn(
        PolygonWithSides,
        (cls, num_sides) => {
            console.log(cls, num_sides);
            svg = appendSVGToDOM(drawingId, radius * size, radius * size);
            appendPolygon(svg, new cls(new Point(radius * size / 2, radius * size / 2), radius).lines);
            // appendCircleWithMidpoint(svg, star.outerCircle);
        }
    )
}

// eslint-disable-next-line no-unused-vars
export function drawStarGrid(drawingId:string, radius:number, size:number) : IO {
    const star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);
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
export function drawRotatedStar(drawingId:string, radius:number, size:number): IO {
    const star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);
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
export function drawDifferentStars(drawingId:string, radius:number, size:number): IO {
    let star:Star;
    let svg:d3SVG;
    _.forEach(
        _.range(6, 12, 1),
        points => {
            star = new Star(new Point(radius * size / 2, radius * size / 2), points, radius);
            svg = appendSVGToDOM(drawingId, radius * size, radius * size);
            appendPolygon(svg, star.lines);
            appendCircleWithMidpoint(svg, star.outerCircle);
        }
    )
}

// eslint-disable-next-line no-unused-vars
export function drawRotatingCircles(drawingId:string, radius:number, size:number): IO {
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);
    const centralCircle = new Circle(radius * size / 2, radius * size / 2, radius);
    // let centralSVGS = appendCircle(svg, centralCircle);
    let currentShift = 0;
    let outerCircles = centralCircle.surroundingCircles(6, 1, currentShift*Math.PI*2/6);
    const outerCirclesSVGS = <d3CIRCLE[]>(_.map(outerCircles, c => appendCircle(svg, c)));
    const outerCirclesL2 = _.flatMap(
        centralCircle.surroundingCircles(6, 1, currentShift*Math.PI*2/6),
        c => c.surroundingCircles(6, 1, currentShift*Math.PI*2/6)
    );
    _.map(outerCirclesL2, c => appendCircle(svg, c));

    // I wanted the central ring to completely rotate ... but the problem with the flowers ... is that they get drawn by other surrounding circles ...
    setInterval(function () {
        [currentShift, outerCircles] = rotateOuterCircles(centralCircle, currentShift, outerCirclesSVGS);
    }, 50);
}


// eslint-disable-next-line no-unused-vars
export function drawHexagonWithSurroundingNonagons(drawingId:string, radius:number, size:number, background_theme:unknown, lines_theme:unknown): IO {
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);

    _.forOwn(background_theme, (v, k) => {
        console.log(k, v);
        svg.style(k, v);
    })

    const circle = new Circle(radius * size / 2, radius * size / 2, radius);
    const hexagons = _.concat(
        _.flatMap(
            _.map(surroundingHexagons(circle), 'outerCircle'),
            surroundingHexagons
        ),
        Hexagon.withinCircle<Hexagon>(circle),
    );
    _.forEach(
        _.flatMap(
            hexagons,
            nonagonsThatFormA6PointStarCenteredAt
        ),
        function (p) {
            appendPolygon(svg, p.lines, lines_theme);
        }
    );
}

// eslint-disable-next-line no-unused-vars
export function drawCirclesRecursively(drawingId:string, radius:number, size:number, maxLevels:number): IO {
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);
    // Recursively Add circles around middle circle ...
    const circle = new Circle(radius*size/2, radius*size/2,radius*2/5.25);
    const circles = (circle).surroundWithFlowersRecursively(maxLevels);
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

// eslint-disable-next-line no-unused-vars
export function drawChainedStars(drawingId:string, radius:number, size:number): IO {
    const numbereOfStars = 12;
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);
    // Recursively Add circles around middle circle ...
    const circle = new Circle(radius*size/2, radius*size/2, radius*2/4);
    const points = (circle).pointsOnCircumference(numbereOfStars, Math.PI/12);
    const rotations : Record<number, number> = {
         0:2*Math.PI - (0  * (2*Math.PI/12)) +     (0*Math.PI/12/12),
         1:2*Math.PI - (1  * (2*Math.PI/12)) +  (-2.5*Math.PI/12/12) - (1 * (Math.PI/12)),
         2:2*Math.PI - (2  * (2*Math.PI/12)) +  (-7.5*Math.PI/12/12) - (1 * (Math.PI/12)),
         3:2*Math.PI - (3  * (2*Math.PI/12)) +     (0*Math.PI/12/12) + (2 * (Math.PI/12)),
         4:2*Math.PI - (4  * (2*Math.PI/12)) +    (-5*Math.PI/12/12) + (2 * (Math.PI/12)),
         5:2*Math.PI - (5  * (2*Math.PI/12)) +     (5*Math.PI/12/12),
         6:2*Math.PI - (6  * (2*Math.PI/12)) +     (0*Math.PI/12/12),
         7:2*Math.PI - (7  * (2*Math.PI/12)) +  (-2.5*Math.PI/12/12) - (1 * (Math.PI/12)),
         8:2*Math.PI - (8  * (2*Math.PI/12)) +     (5*Math.PI/12/12) - (2 * (Math.PI/12)),
         9:2*Math.PI - (9  * (2*Math.PI/12)) +     (0*Math.PI/12/12) + (2 * (Math.PI/12)),
        10:2*Math.PI - (10 * (2*Math.PI/12)) +   (7.5*Math.PI/12/12) + (1 * (Math.PI/12)),
        11:2*Math.PI - (11 * (2*Math.PI/12)) +     (5*Math.PI/12/12),
    }
    _.forEach(
        points,
        (p, i) => {
            // https://stackoverflow.com/questions/19461521/how-to-center-an-element-horizontally-and-vertically#:~:text=For%20vertical%20alignment%2C%20set%20the,any%20other%20inline%20children%20elements.
            // let finalRotation = (numbereOfStars-i)*2*Math.PI/numbereOfStars;
            // finalRotation = isEven(i) ? (finalRotation) : finalRotation + (4*Math.PI/12/12);
            // // finalRotation = isEven(i) ? (finalRotation + Math.PI/12) : (finalRotation + Math.PI/12);
            // finalRotation = isEven(i) ? (finalRotation) : (finalRotation);
            const finalRotation = rotations[i];
            const s = FivePointStar(p, radius/numbereOfStars/1.35).rotate(finalRotation);
            appendPolygon(<d3SVG>svg, s.lines);
            appendText(<d3SVG>svg, `${i}: ${Math.round(180*finalRotation/Math.PI)}`, p, {
                "font-size": `${radius/50}px`,
                "text-anchor": "middle",
                "vertical-align": "middle",
            });
        }
    );
    appendPolygon(<d3SVG>svg, FivePointStar(circle.midpoint, radius/numbereOfStars/1.5).lines);
    // appendPolygon(<d3SVG>svg, (new Star(circle.midpoint, 5, radius/numbereOfStars/1.5)).lines);
    // appendCircleWithMidpoint(<d3SVG>svg, circle);
}

// // eslint-disable-next-line no-unused-vars
// function drawHexagonWithSurroundingNonagons() {
//     // let svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size));
//     let svg = <d3SVG>(d3.select("body").append("svg").attr("width", radius * size).attr("height", radius * size).style("background", "RGBA(118,215,196,0.9)"));
//     let centralCircle = new Circle(radius * size / 2, radius * size / 2, radius);
//     let outerCircles = centralCircle.surroundingCircles(6, 1);
//     // appendPolygon(svg, new Hexagon(centralCircle.midpoint, centralCircle.r).lines);
//     let surroundingPolygons = _.map(outerCircles, c => new Nonagon(c.midpoint, centralCircle.r * 0.75));
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
