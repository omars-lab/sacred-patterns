import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import * as _ from "lodash";
import {Circle} from "./circles"
import {Hexagon, Nonagon, Polygon, PolygonWithSides} from "./polygons"
import {Point} from "./points"
import {Star, ElongatedFivePointStar, FivePointStar} from "./star"
import * as d3 from 'd3'
import {_map_even_odd} from "./helpers"
// import {isEven} from "./helpers"
import {IO, d3SVG, d3SVGDef, d3CIRCLE } from "./types"
import {appendText, appendPolygon, appendCircle, appendCircleWithMidpoint } from "./canvas"
import {Decagon} from "./polygons"
import { Dropdown } from 'react-bootstrap';
import React, { useRef, useEffect } from 'react';


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

export function appendSVGToDOM(id: string, width:number, height:number): d3SVG {
    // https://www.freshconsulting.com/d3-js-gradients-the-easy-way/
    const svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("title", id)
        .attr("id", id);

    const defs = svg.append("defs");
    appendLinearGradientDef(defs, "svgGradient", "#28313B", "#485461");
    appendLinearGradientDef(defs, "invertedSvgGradient", `#${invertHex("28313B")}`, `#${invertHex("485461")}`);
    // appendLinearGradientDef(defs, "svgGradient", "#F2A65A", "#772F1A");
    return (svg) as d3SVG;
}

// eslint-disable-next-line no-unused-vars
export function rotateOuterCircles(centralCircle:Circle, currentShift:number, outerCirclesSVGS:d3CIRCLE[]): [number, Circle[]] {
    const newShift = currentShift + 1;
    console.log("Current shfit", newShift);
    const newOuterCircles = centralCircle.surroundingCircles(6, 1, (newShift/10)*Math.PI*2/6);
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
    return [newShift, newOuterCircles] as [number,Circle[]];
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
export function drawDifferentPolygons(drawingId:string, radius:number, size:number) : IO {
    let svg;
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
        (points) => {
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
    const outerCirclesSVGS = (_.map(outerCircles, c => appendCircle(svg, c))) as d3CIRCLE[];
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
export function drawHexagonWithSurroundingNonagons(drawingId: string, radius: number, size: number, background_theme: unknown, lines_theme: unknown): d3SVG {
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
    return (svg as d3SVG);
}

// eslint-disable-next-line no-unused-vars
export function drawCirclesRecursively(drawingId:string, radius:number, size:number, maxLevels:number): IO {
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);
    // Recursively Add circles around middle circle ...
    const circle = new Circle(radius*size/2, radius*size/2,radius*2/5.25);
    const circles = (circle).surroundWithFlowersRecursively(maxLevels);
    _.forEach(
        circles,
        (c: Circle) => {
            console.log("appending c", c);
            appendCircleWithMidpoint(svg as d3SVG, c, maxLevels);
            appendPolygon(svg as d3SVG, Hexagon.withinCircle(c).lines);
        }
    );
    // appendCircleWithMidpoint(<d3SVG>svg, circle);
}

// eslint-disable-next-line no-unused-vars
export function drawChainedStars(drawingId:string, radius:number, size:number): IO {
    const numbereOfStars = 10;
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);
    // Recursively Add circles around middle circle ...
    const circle = new Circle(radius*size/2, radius*size/2, radius*2/5);
    const points = (circle).pointsOnCircumference(numbereOfStars, Math.PI/numbereOfStars);

    _.forEach(
        points,
        (p, i) => {
            const finalRotation = 2*Math.PI - (i * (2*Math.PI/numbereOfStars));
            const elongationFactor : Record<number, number> = {};
            elongationFactor[(3+(i*2)) % 10] = 1.5;
            const s = new ElongatedFivePointStar(
                FivePointStar(p, radius/numbereOfStars/1.35).rotate(finalRotation),
                elongationFactor
            );
            appendPolygon(svg as d3SVG, s.lines);
            appendText(svg as d3SVG, `${i}: ${Math.round(180*finalRotation/Math.PI)}`, p, {
                "font-size": `${radius/50}px`,
                "text-anchor": "middle",
                "vertical-align": "middle",
            });
        }
    );
    appendPolygon(svg as d3SVG, FivePointStar(circle.midpoint, radius/numbereOfStars/1.5).lines);
    appendPolygon(svg as d3SVG, (new Decagon(circle.midpoint, radius*2/5.25)).lines);
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

  
export function drawArtwork(index: string) {    
    // https://medium.com/@jeffbutsch/using-d3-in-react-with-hooks-4a6c61f1d102
    const radius = 100;
    const maxLevels = 2;
    const size = maxLevels * 3;
    
    if ( index == "0" ) {
        drawChainedStars("d0", radius*7.5, 2);
    }
    else if ( index == "1" ) {
        drawDifferentPolygons("d1", radius,  size);
    }
    else if ( index == "2" ) {
        drawStarGrid("d2", radius, size);
    }
    else if ( index == "3" ) {
        drawRotatedStar("d3", radius, size);
    }
    else if ( index == "4" ) {
        drawDifferentStars("d4", radius, size);
    }
    else if ( index == "5" ) {
        drawRotatingCircles("d5", radius, size);
    }
    else if ( index == "6" ) {
        // var svg: d3SVG;
        //  
        const background_theme = JSON.parse(document.getElementById("config")!.innerText).background_theme[0];
        const line_theme = JSON.parse(document.getElementById("config")!.innerText).line_theme[0];
        const svg = drawHexagonWithSurroundingNonagons("d6", radius, size, background_theme, line_theme);
        // Adding click handlers ...
        // http://bl.ocks.org/methodofaction/3831266
        // https://stackoverflow.com/questions/24079566/d3-js-download-graph-as-svg-image
        d3.select("#download").on("click", function() {
            const htmldata = svg
                .attr("version", 1.1)
                .attr("xmlns", "http://www.w3.org/2000/svg")
                .node()!.outerHTML;  
            d3.select(this)
                .attr("href-lang", "image/svg+xml")
                .attr("href", "data:image/svg+xml;base64,\n" + window.btoa(htmldata))
                .attr("download", "viz.svg") 
        });
        // d3.select("#regenerate").on("click", function(){
        //     document.getElementById('d6')!.remove();
        //     background_theme = JSON.parse(document.getElementById("config")!.innerText).background_theme[0];
        //     line_theme = JSON.parse(document.getElementById("config")!.innerText).line_theme[0];
        //     svg = drawHexagonWithSurroundingNonagons("d6", radius, size, background_theme, line_theme);
        // });
    }
    else if ( index == "7" ) {
        drawCirclesRecursively("d7", radius, size, maxLevels);
    }
}

// https://medium.com/@jeffbutsch/using-d3-in-react-with-hooks-4a6c61f1d102
function D3Artwork(props: { activeArtworkIndex: string }) {
    console.log(props.activeArtworkIndex);
    const d3Container = useRef(null);
    useEffect(
        () => {
            if (props.activeArtworkIndex && d3Container.current) {
                const svg = d3.select(d3Container.current);

                // Bind D3 data
                const update = svg
                    .append('g')
                    .selectAll('text')
                    .data([props.activeArtworkIndex, props.activeArtworkIndex, props.activeArtworkIndex]);

                // Enter new D3 elements
                update.enter()
                    .append('text')
                    .attr('x', (_, i) => i * 25)
                    .attr('y', 40)
                    .style('font-size', 24)
                    .text((d) => d);

                // Update existing D3 elements
                update
                    .attr('x', (_, i) => i * 40)
                    .text((d) => d);

                // Remove old D3 elements
                update.exit()
                    .remove();

                drawArtwork(props.activeArtworkIndex);
            }
        },

        /*
            useEffect has a dependency array (below). It's a list of dependency
            variables for this useEffect block. The block will run after mount
            and whenever any of these variables change. We still have to check
            if the variables are valid, but we do not have to compare old props
            to next props to decide whether to rerender.
        */
        [props.activeArtworkIndex, d3Container.current])

    return (
        <svg
            className="d3-component"
            width={400}
            height={200}
            ref={d3Container}
        />
    );
}

function ArtworkDropdown() {

  const [activeArtworkIndex, setActiveArtworkIndex] = useState("0")
  // https://stackoverflow.com/questions/31509965/how-can-i-capture-the-value-of-a-react-bootstrap-dropdown-list

  return (
    <>
        <Dropdown onSelect={
            (eventKey, evt) => {
                setActiveArtworkIndex(eventKey!);
                console.log(eventKey);
                console.log(evt);
            }
        }>
            <Dropdown.Toggle variant="success" id="dropdown-basic">
                Select Artwork
            </Dropdown.Toggle>
            <Dropdown.Menu>
                <Dropdown.Item eventKey={"0"}>Image 0</Dropdown.Item>
                <Dropdown.Item eventKey={"1"}>Image 1</Dropdown.Item>
                <Dropdown.Item eventKey={"2"}>Image 2</Dropdown.Item>
                <Dropdown.Item eventKey={"3"}>Image 3</Dropdown.Item>
                <Dropdown.Item eventKey={"4"}>Image 4</Dropdown.Item>
                <Dropdown.Item eventKey={"5"}>Image 5</Dropdown.Item>
                <Dropdown.Item eventKey={"6"}>Image 6</Dropdown.Item>
                <Dropdown.Item eventKey={"7"}>Image 7</Dropdown.Item>
            </Dropdown.Menu>
        </Dropdown>
        <D3Artwork activeArtworkIndex={activeArtworkIndex}></D3Artwork>
    </>
  );
}

function NavigationBar() {
  // TODO: Actually implement a navigation bar
  return <>
        <h1>Hello from React!</h1>
        <ArtworkDropdown></ArtworkDropdown>
    </>;
    
}

/* eslint-disable-next-line no-unused-vars */
export function main() {
    const domNode = document.getElementById('root')!;
    const root = createRoot(domNode);
    root.render(<NavigationBar />);
}

// https://react.dev/reference/react/useState
// https://stackoverflow.com/questions/34424845/adding-script-tag-to-react-jsx
// https://react.dev/reference/react/Component#alternatives