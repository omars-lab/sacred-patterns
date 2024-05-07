import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import * as d3 from 'd3'
import { d3SVG, DrawingProps } from "./types"
import { Dropdown } from 'react-bootstrap';
import { useRef, useEffect } from 'react';
import {
    appendLinearGradientDef, drawChainedStars, drawDifferentPolygons,
    drawStarGrid,
    drawRotatedStar,
    drawDifferentStars,
    drawRotatingCircles, drawHexagonWithSurroundingNonagons, invertHex,
    drawCirclesRecursively
} from './draw';

/* The following line can be included in your src/index.js or App.js file */
import 'bootstrap/dist/css/bootstrap.min.css';

export function sytleSVG(svg: d3SVG, id: string, width: number, height: number): d3SVG {
    // https://www.freshconsulting.com/d3-js-gradients-the-easy-way/
    const svg_response = svg
        .attr("width", width)
        .attr("height", height)
        .attr("title", id)
        .attr("id", id);

    const defs = svg.append("defs");
    appendLinearGradientDef(defs, "svgGradient", "#28313B", "#485461");
    appendLinearGradientDef(defs, "invertedSvgGradient", `#${invertHex("28313B")}`, `#${invertHex("485461")}`);
    // appendLinearGradientDef(defs, "svgGradient", "#F2A65A", "#772F1A");
    return (svg_response) as d3SVG;
}

export function appendSVGToDOM(id: string, width: number, height: number): d3SVG {
    // https://www.freshconsulting.com/d3-js-gradients-the-easy-way/
    const svg = sytleSVG(
        d3.select("body").append("svg"),
        id, width, height
    );
    return svg;
}

export function drawArtwork(svg: d3SVG, props: DrawingProps) {
    // https://medium.com/@jeffbutsch/using-d3-in-react-with-hooks-4a6c61f1d102
    const { radius, index, size, maxLevels } = props;
    if (index == "0") {
        drawChainedStars(svg, radius * 7.5, 2);
    }
    else if (index == "1") {
        drawDifferentPolygons(svg, radius, size);
    }
    else if (index == "2") {
        drawStarGrid(svg, radius, size);
    }
    else if (index == "3") {
        drawRotatedStar(svg, radius, size);
    }
    else if (index == "4") {
        drawDifferentStars(svg, radius, size);
    }
    else if (index == "5") {
        drawRotatingCircles(svg, radius, size);
    }
    else if (index == "6") {
        // var svg: d3SVG;
        //  
        const background_theme = JSON.parse(document.getElementById("config")!.innerText).background_theme[0];
        const line_theme = JSON.parse(document.getElementById("config")!.innerText).line_theme[0];
        drawHexagonWithSurroundingNonagons(svg, radius, size, background_theme, line_theme);
        // Adding click handlers ...
        // http://bl.ocks.org/methodofaction/3831266
        // https://stackoverflow.com/questions/24079566/d3-js-download-graph-as-svg-image
        d3.select("#download").on("click", function () {
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
    else if (index == "7") {
        drawCirclesRecursively(svg, radius, size, maxLevels);
    }
}

// https://medium.com/@jeffbutsch/using-d3-in-react-with-hooks-4a6c61f1d102
function D3Artwork(props: { activeArtworkIndex: string }) {
    console.log(props.activeArtworkIndex);
    const d3Container = useRef(null);
    const drawingProps: DrawingProps = {
        radius: 100,
        maxLevels: 2,
        size: 2 * 3,
        index: props.activeArtworkIndex,
    };
    const height = drawingProps.radius * drawingProps.size;
    const width = drawingProps.radius * drawingProps.size;
    useEffect(
        () => {
            if (props.activeArtworkIndex && d3Container.current) {
                const svg = d3.select(d3Container.current);
                svg.selectAll("*").remove();
                const s = ((svg as unknown) as d3SVG);
                sytleSVG(s, `d3-svg-${props.activeArtworkIndex}`, width, height)
                drawArtwork(s, drawingProps);
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
            width={width}
            height={height}
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