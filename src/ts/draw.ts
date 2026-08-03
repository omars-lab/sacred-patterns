/* eslint-disable-next-line no-unused-vars */
import * as _ from "lodash";
import { Circle } from "./circles"
import { Hexagon, Nonagon, Polygon, PolygonWithSides } from "./polygons"
import { Point } from "./points"
import { Star, ElongatedFivePointStar, FivePointStar } from "./star"
import * as d3 from 'd3'
import { _map_even_odd } from "./helpers"
import { IO, d3SVG, d3SVGDef, d3CIRCLE } from "./types"
import { appendText, appendPolygon, appendCircle, appendCircleWithMidpoint, colorForLevel } from "./canvas"
import { Decagon } from "./polygons"

/* The following line can be included in your src/index.js or App.js file */
import 'bootstrap/dist/css/bootstrap.min.css';

// https://stackoverflow.com/questions/35969656/how-can-i-generate-the-opposite-color-according-to-current-color
export function invertHex(hex: string): string {
    const invertedHexResponse = (Number(`0x1${hex}`) ^ 0xFFFFFF).toString(16).substr(1).toUpperCase();
    console.log(invertHex);
    return invertedHexResponse
}

export function appendLinearGradientDef(svgDefs: d3SVGDef, id: string, color1: string, color2: string) {
    const gradient = svgDefs.append("linearGradient")
        .attr("id", id)
        .attr("x1", "0%")
        .attr("x2", "100%")
        .attr("y1", "0%")
        .attr("y2", "100%");

    gradient.append("stop")
        .attr('class', 'start')
        .attr("offset", "0%")
        .attr("stop-color", color1)
        .attr("stop-opacity", 1);

    gradient.append("stop")
        .attr('class', 'end')
        .attr("offset", "100%")
        .attr("stop-color", color2)
        .attr("stop-opacity", 1);
}

// eslint-disable-next-line no-unused-vars
export function rotateOuterCircles(centralCircle: Circle, currentShift: number, outerCirclesSVGS: d3CIRCLE[]): [number, Circle[]] {
    const newShift = currentShift + 1;
    console.log("Current shfit", newShift);
    const newOuterCircles = centralCircle.surroundingCircles(6, { shift_in_radians: (newShift / 10) * Math.PI * 2 / 6 });
    _.forEach(
        _.zip(newOuterCircles, outerCirclesSVGS),
        ([newCircle, circleToTransition]) => {
            (circleToTransition as d3CIRCLE)
                .transition()
                .ease(d3.easeLinear)
                .duration(50)
                .attr('cx', (newCircle as Circle).x)
                .attr('cy', (newCircle as Circle).y)
                .attr('r', (newCircle as Circle).r);
        }
    )
    return [newShift, newOuterCircles] as [number, Circle[]];
}

export function surroundingHexagons(circle: Circle): Hexagon[] {
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

export function nonagonsThatFormA6PointStarCenteredAt(centralHexagon: Hexagon): Polygon[] {
    const centralCircle = centralHexagon.outerCircle;
    const outerCircles = centralCircle.surroundingCircles(6, {});
    // appendPolygon(svg, new Hexagon(centralCircle.midpoint, centralCircle.r).lines);
    let surroundingPolygons = _.map(
        outerCircles,
        function (c: Circle) {
            return new Nonagon(c.midpoint, centralCircle.r * 0.75);
        }
    );
    // Rotate every other polygon ...
    surroundingPolygons = _map_even_odd(
        surroundingPolygons,
        function (nonagon: Nonagon) {
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
export function drawDifferentPolygons(svg: d3SVG, radius: number, size: number): IO {
    // let svg;
    _.forOwn(
        PolygonWithSides,
        (cls, num_sides) => {
            console.log(cls, num_sides);
            // We were creating svg per polygon type ...
            // svg = appendSVGToDOM(drawingId, radius * size, radius * size);
            appendPolygon(svg, new cls(new Point(radius * size / 2, radius * size / 2), radius).lines);
            // appendCircleWithMidpoint(svg, star.outerCircle);
        }
    )
}

// eslint-disable-next-line no-unused-vars
export function drawStarGrid(svg: d3SVG, radius: number, size: number): IO {
    const star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    appendPolygon(svg, star.lines);
    appendPolygon(svg, star.rotate(Math.PI / 2).lines);
    appendPolygon(svg, Hexagon.withinCircle(star.outerCircle).lines);
    appendPolygon(svg, star.right().lines);
    appendPolygon(svg, star.right().rotate(Math.PI / 2).lines);
    appendPolygon(svg, Hexagon.withinCircle(star.right().outerCircle).lines);
    appendPolygon(svg, star.above().lines);
    appendPolygon(svg, star.above().rotate(Math.PI / 2).lines);
    appendPolygon(svg, Hexagon.withinCircle(star.above().outerCircle).lines);
    appendPolygon(svg, star.above().right().lines);
    appendPolygon(svg, star.above().right().rotate(Math.PI / 2).lines);
    appendPolygon(svg, Hexagon.withinCircle(star.above().right().outerCircle).lines);
}

// eslint-disable-next-line no-unused-vars
export function drawRotatedStar(svg: d3SVG, radius: number, size: number): IO {
    const star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    appendPolygon(svg, star.rotate(Math.PI / 4).lines);
    _.forEach(
        star.rotate(Math.PI / 4).circles,
        c => {
            appendCircleWithMidpoint(svg, c);
            true;
        }
    );
}

// eslint-disable-next-line no-unused-vars
export function drawDifferentStars(svg: d3SVG, radius: number, size: number): IO {
    let star: Star;
    // let svg:d3SVG;
    _.forEach(
        _.range(6, 12, 1),
        (points) => {
            star = new Star(new Point(radius * size / 2, radius * size / 2), points, radius);
            // We used to append an svg for every pointed star ... revisit this if needed 
            // svg = appendSVGToDOM(drawingId, radius * size, radius * size);
            appendPolygon(svg, star.lines);
            appendCircleWithMidpoint(svg, star.outerCircle);
        }
    )
}

// eslint-disable-next-line no-unused-vars
export function drawRotatingCircles(svg: d3SVG, radius: number, size: number): IO {
    const centralCircle = new Circle(radius * size / 2, radius * size / 2, radius);
    // let centralSVGS = appendCircle(svg, centralCircle);
    let currentShift = 0;
    let outerCircles = centralCircle.surroundingCircles(6, { shift_in_radians: currentShift * Math.PI * 2 / 6 });
    const outerCirclesSVGS = (_.map(outerCircles, c => appendCircle(svg, c))) as d3CIRCLE[];
    const outerCirclesL2 = _.flatMap(
        centralCircle.surroundingCircles(6, { shift_in_radians: currentShift * Math.PI * 2 / 6 }),
        c => c.surroundingCircles(6, { shift_in_radians: currentShift * Math.PI * 2 / 6 })
    );
    _.map(outerCirclesL2, c => appendCircle(svg, c));

    // I wanted the central ring to completely rotate ... but the problem with the flowers ... is that they get drawn by other surrounding circles ...
    setInterval(function () {
        [currentShift, outerCircles] = rotateOuterCircles(centralCircle, currentShift, outerCirclesSVGS);
    }, 50);
}


// eslint-disable-next-line no-unused-vars
export function drawHexagonWithSurroundingNonagons(svg: d3SVG, radius: number, size: number, background_theme: unknown, lines_theme: unknown): d3SVG {
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
    return (svg as d3SVG);
}

// eslint-disable-next-line no-unused-vars
export function drawCirclesRecursively(svg: d3SVG, radius: number, size: number, maxLevels: number): IO {
    // Recursively Add circles around middle circle ...
    const circle = new Circle(radius * size / 2, radius * size / 2, radius * 2 / 5.25);
    const circles = (circle).surroundWithFlowersRecursively(maxLevels);
    _.forEach(
        circles,
        (c: Circle) => {
            console.log("appending c", c);
            appendCircleWithMidpoint(svg as d3SVG, c, colorForLevel(c.metadata.level, maxLevels));
            appendPolygon(svg as d3SVG, Hexagon.withinCircle(c).lines);
        }
    );
    // appendCircleWithMidpoint(<d3SVG>svg, circle);
}

function collectiveMidpoint(points: Point[]): Point {
    const xs = _.map(points, p => p.x);
    const ys = _.map(points, p => p.y);
    return new Point(_.sum(xs) / points.length, _.sum(ys) / points.length,)
}

function distanceBetweenPoints(x1: Point, x2:Point): number {
    return Math.sqrt(
        Math.pow(x1.x-x2.x, 2) + 
        Math.pow(x1.y-x2.y, 2) 
    );

}

// Appends Stuff to SVG and returns next layer ...
function processLotfallahDomeCircleLayer(svg: d3SVG, currentCirclesLayer: Circle[], centralCircle: Circle, layerNum: number, debugFn=((layer:number) => layer >= 0)): Circle[] {
    const nextCircleLayer = [] as Circle[];
    _.each(
        currentCirclesLayer,
        (c: Circle, i: number) => {
            console.log("appending c", c);
            // appendCircle(svg as d3SVG, c, "grey");
            if (debugFn(layerNum)) {
                appendCircle(svg as d3SVG, c, "grey");
            }
            // if (debugFn(layerNum)) {
            //     appendText(svg as d3SVG, `${i}ML${layerNum}`, c.midpoint, {stroke: "blue", "font-size": 4});
            // }
            // Top mapper - top for current index is top of one indexes before ...
            const topIndexMapper = (i: number) => (i - 1) < 0 ? (currentCirclesLayer.length + i - 1) : i - 1;
            // Right mapper - right for current index is right of two indexes before ...
            const rightIndexMapper = (i: number) => (i - 2) < 0 ? (currentCirclesLayer.length + i - 2) : i - 2;
            // Left mapper - left for current index is left of one indexes before ... smae as top
            const leftIndexMapper = topIndexMapper;
            // Bottom mapper - mottom for current index is bottom of twp indexes before ... smae as right
            const bottomIndexMapper = rightIndexMapper;
            // const [ topIndexMapper, rightIndexMapper, leftIndexMapper, bottomIndexMapper] = [((x:number) => x), ((x:number) => x), ((x:number) => x), ((x:number) => x)]

            const topPoint = currentCirclesLayer[topIndexMapper(i)].pointOnCircumferenceAtRadian(-1 * (topIndexMapper(i) + 2) * 2 * Math.PI / currentCirclesLayer.length - (layerNum * Math.PI/4))
            const leftPoint = currentCirclesLayer[leftIndexMapper(i)].pointOnCircumferenceAtRadian(-1 * (leftIndexMapper(i) + 3) * 2 * Math.PI / currentCirclesLayer.length - (layerNum * Math.PI/4))
            const rightPoint = currentCirclesLayer[rightIndexMapper(i)].pointOnCircumferenceAtRadian(-1 * (rightIndexMapper(i) + 3) * 2 * Math.PI / currentCirclesLayer.length - (layerNum * Math.PI/4));
            const bottomPoint = currentCirclesLayer[bottomIndexMapper(i)].pointOnCircumferenceAtRadian(-1 * (bottomIndexMapper(i) + 4 + layerNum) * 2 * Math.PI / currentCirclesLayer.length - (layerNum * Math.PI/4));
            const centralPoint = collectiveMidpoint([bottomPoint, topPoint, leftPoint, rightPoint]);
            

            if (debugFn(layerNum)) {
                // Top Dot
                appendText(svg as d3SVG, `${i}L${layerNum}`, topPoint,{stroke: "green", "font-size": 4});
            }
            if (debugFn(layerNum)) {
                // left Dot (also right dot ...)
                appendText(svg as d3SVG,  `${i}L${layerNum}`, leftPoint, {stroke: "orange", "font-size": 4});
            }
            if (debugFn(layerNum)) {
                // right Dot (also right dot ...)
                appendText(svg as d3SVG, `${i}L${layerNum}`, rightPoint, {stroke: "orange", "font-size": 4});
            }
            if (debugFn(layerNum)) {
                // Bottom Dot - also same as the midpoint ...
                appendText(svg as d3SVG, `${i}L${layerNum}`, bottomPoint, {stroke: "red", "font-size": 4});
            }

            if (debugFn(layerNum)) {
                appendText(svg as d3SVG, `${layerNum}.${i}`, centralPoint, {stroke: "purple", "font-size": 4});
            }

            // Add circle for the next layer ...
            // Next layer need to connect to origin / midpoint ...
            // const nextLayerPoint = c.pointOnCircumferenceAtRadian(-1 * (bottomIndexMapper(i) + 3) * 2 * Math.PI / currentCirclesLayer.length - (layerNum * Math.PI/4));
            // const nextLayerPoint = currentCirclesLayer[bottomIndexMapper(i)].pointOnCircumferenceAtRadian(-1 * (bottomIndexMapper(i) + 3) * 2 * Math.PI / currentCirclesLayer.length - (layerNum * Math.PI/4));
            const nextLayerPoint = c.pointOnCircumferenceAtRadian(-1 * (i + 3) * 2 * Math.PI / currentCirclesLayer.length - (layerNum * Math.PI/4));
            

            const newRadius = distanceBetweenPoints(nextLayerPoint, centralCircle.midpoint);
            const nextLayerCircle = new Circle(nextLayerPoint.x, nextLayerPoint.y, newRadius)
            nextCircleLayer.push(nextLayerCircle);

            // Inner circle radius
            // const previousLayerPoint = currentCirclesLayer[topIndexMapper(i)].pointOnCircumferenceAtRadian(-1 * (topIndexMapper(i) + 3) * 2 * Math.PI / currentCirclesLayer.length - (layerNum * Math.PI/4));
            // if (debugFn(layerNum)) {
            //     // Bottom Dot - also same as the midpoint ...
            //     appendText(svg as d3SVG, `${i}L${layerNum}`, previousLayerPoint, {stroke: "gold", "font-size": 4});
            // }
            // https://www.quora.com/How-does-one-calculate-the-straight-line-distance-between-two-points-on-a-circle-if-the-radius-and-arc-length-are-known
            // const innerCircleRaduis = (Math.PI/(4/3)) * newRadius/currentCirclesLayer.length;
            // const innerCircleRaduis = c.r / currentCirclesLayer.length;
            // const innerCircleRaduis = ((nextLayerCircle.r * Math.PI * 2) / currentCirclesLayer.length) / 2;
            // const innerCircleRaduis = distanceBetweenPoints(nextLayerPoint, previousLayerPoint) / 2;
            // const innerCircleRaduis = (2 * c.r * Math.sin(c.r*(2*Math.PI/currentCirclesLayer.length) / (2* c.r))) / 2;
            const innerCircleRaduis = .95 * ( Math.PI * distanceBetweenPoints(centralPoint, centralCircle.midpoint) ) / currentCirclesLayer.length;
            // const innerCircleRaduis = .99 * ( Math.PI * distanceBetweenPoints(centralPoint, centralCircle.midpoint) ) / currentCirclesLayer.length;
            appendCircle(svg as d3SVG, new Circle(centralPoint.x, centralPoint.y, innerCircleRaduis), "grey");
        }
    ).length;
    return nextCircleLayer;
}

// eslint-disable-next-line no-unused-vars
export function drawLotfallahDome(svg: d3SVG, radius: number, size: number, maxLevels: number): IO {
    console.log(maxLevels);
    // https://design.tutsplus.com/tutorials/geometric-design-the-lotfallah-mosque-dome--cms-24859
    // Add Circle in the center of the grid
    const circle = new Circle(radius * size / 2, radius * size / 2, radius * 2 / 5.25);
    appendCircleWithMidpoint(svg as d3SVG, circle);
    // Add 6 circles around middle circle ...
    // Interleave arrays so they are sequential ...
    console.log("circles");
    const flattenedCircles = _.flatten(_.zip(
        circle.surroundingCircles(6, {clockwise: false}), 
        circle.surroundingCircles(6, { shift_in_radians: Math.PI/6, clockwise: false })
    ));
    
    console.log(flattenedCircles);
    // const circles = (_.remove(flattenedCircles, _.isNil) as unknown) as Circle[];
    // const circles = _.remove(
    //     flattenedCircles, 
    //     x => { console.log(x); return _.isNil(x); } 
    // ) as Circle[];
    const l0Circles = flattenedCircles.filter((c) => !_.isNil(c)) as Circle[]
    // l0Circles.forEach((c) => appendCircle(svg as d3SVG, c, "grey"));
    console.log(processLotfallahDomeCircleLayer);
    // console.log(l0Circles);
    const l1Circles = processLotfallahDomeCircleLayer(svg as d3SVG, l0Circles, circle, 0, l => l == -1);
    // console.log(l1Circles);
    const l2Circles = processLotfallahDomeCircleLayer(svg as d3SVG, l1Circles, circle, 1, l => l == -1);
    // console.log(l2Circles);
    const l3Circles = processLotfallahDomeCircleLayer(svg as d3SVG, l2Circles, circle, 2, l => l == -1);
    // console.log(l3Circles);
    const l4Circles = processLotfallahDomeCircleLayer(svg as d3SVG, l3Circles, circle, 3, l => l == -1);
    // console.log(l4Circles);
    const l5Circles = processLotfallahDomeCircleLayer(svg as d3SVG, l4Circles, circle, 4, l => l == -1);
    // console.log(l5Circles);
    const l6Circles = processLotfallahDomeCircleLayer(svg as d3SVG, l5Circles, circle, 5, l => l == -1);
    // console.log(l6Circles);
    const l7Circles = processLotfallahDomeCircleLayer(svg as d3SVG, l6Circles, circle, 6, l => l == -1);
    console.log(l7Circles);
}

// eslint-disable-next-line no-unused-vars
export function drawChainedStars(svg: d3SVG, radius: number, size: number): IO {
    const numbereOfStars = 10;
    // Recursively Add circles around middle circle ...
    const circle = new Circle(radius * size / 2, radius * size / 2, radius * 2 / 5);
    const points = (circle).pointsOnCircumference(numbereOfStars, { shift_in_radians: Math.PI / numbereOfStars });

    _.forEach(
        points,
        (p, i) => {
            const finalRotation = 2 * Math.PI - (i * (2 * Math.PI / numbereOfStars));
            const elongationFactor: Record<number, number> = {};
            elongationFactor[(3 + (i * 2)) % 10] = 1.5;
            const s = new ElongatedFivePointStar(
                FivePointStar(p, radius / numbereOfStars / 1.35).rotate(finalRotation),
                elongationFactor
            );
            appendPolygon(svg as d3SVG, s.lines);
            appendText(svg as d3SVG, `${i}: ${Math.round(180 * finalRotation / Math.PI)}`, p, {
                "font-size": `${radius / 50}px`,
                "text-anchor": "middle",
                "vertical-align": "middle",
            });
        }
    );
    appendPolygon(svg as d3SVG, FivePointStar(circle.midpoint, radius / numbereOfStars / 1.5).lines);
    appendPolygon(svg as d3SVG, (new Decagon(circle.midpoint, radius * 2 / 5.25)).lines);
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