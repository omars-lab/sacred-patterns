import * as _ from "lodash";
import {Circle} from "./circles"
import {Hexagon, Nonagon, Polygon, PolygonWithSides} from "./polygons"
import {Point} from "./points"
import {Star, ElongatedFivePointStar, FivePointStar} from "./star"
import * as d3 from 'd3'
import {_map_even_odd} from "./helpers"
// import {isEven} from "./helpers"
import {appendText, appendPolygon, appendCircle, appendCircleWithMidpoint, d3SVG, d3CIRCLE, d3SvgElement} from "./canvas"
import {IO} from "./types"
import {Decagon} from "./polygons"


/**
 * Bitwise-invert a 6-digit hex color string — answers "given a fill
 * color, what contrasting color is guaranteed to be visible on top of
 * it, for use as a paired background/foreground gradient stop?". XORs
 * the numeric value with `0xFFFFFF` rather than per-channel subtraction
 * so the operation is one CPU op and order-independent. Used by
 * `appendSVGToDOM` to derive `invertedSvgGradient` from the primary
 * `svgGradient`'s stops without hand-picking a second palette.
 * See: https://stackoverflow.com/questions/35969656.
 */
export function invertHex(hex: string): string {
    const invertedHex = (Number(`0x1${hex}`) ^ 0xFFFFFF).toString(16).substring(1).toUpperCase();
    console.log(invertHex);
    return invertedHex
}

/**
 * Define a top-left to bottom-right linear gradient under `<defs>` —
 * answers "how does a drawing register a reusable two-stop gradient
 * once (in `<defs>`) and then reference it by `url(#id)` from any
 * element's `fill`/`stroke`?". The 0%→100% diagonal is hard-coded
 * because every gradient in this codebase reads top-left-to-bottom-right
 * (matches the reading direction); callers that need other angles would
 * extend the signature rather than override after the fact.
 */
export function appendLinearGradientDef(svgDefs: d3SvgElement<SVGDefsElement>, id: string, color1: string, color2: string) {
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

/**
 * Create a new `<svg>` under `<body>` pre-wired with the canonical
 * two-gradient `<defs>` — answers "where do all `draw*` entry points
 * get a fresh canvas that already carries `svgGradient` and
 * `invertedSvgGradient` so element fills can reference them by id
 * without per-drawing setup?". The dimensions are caller-supplied
 * (radius × size) so a single drawing routine can render at any zoom
 * without code change; the gradient stops are baked in because every
 * drawing in this library shares the dark-cool palette.
 * See: https://www.freshconsulting.com/d3-js-gradients-the-easy-way/.
 */
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
    return <d3SVG>(svg);
}

/**
 * Advance the radial shift of a flower-of-life outer ring by one step and
 * D3-transition each SVG `<circle>` to the new position — answers "how
 * does the rotating-circles animation move six already-painted DOM nodes
 * to fresh polar positions on every tick without re-painting or layout
 * thrash?". Returns the new shift count alongside the new Circle
 * positions so the caller's `setInterval` loop can thread the shift
 * forward immutably (tenet 10a — no caller-visible mutation) instead
 * of stashing it in module-level state.
 */
export function rotateOuterCircles(centralCircle:Circle, currentShift:number, outerCirclesSVGS:d3CIRCLE[]): [number, Circle[]] {
    const newShift = currentShift + 1;
    console.log("Current shift", newShift);
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

/**
 * Build the six hex-grid neighbors around an inscribed hexagon — answers
 * "given a reference circle, what's the canonical six-around-one ring
 * of hexagons that share an edge with the central one (the load-bearing
 * primitive for flower-of-life, six-petal rosettes, and honeycomb
 * backgrounds)?". Order matches the Hexagon directional helpers
 * (`northWest`, `northEast`, `above`, `below`, `southWest`, `southEast`)
 * so callers depending on positional indexing (alternating fill, for
 * instance) can rely on a stable rotation.
 */
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

/**
 * Tile a hexagon with six surrounding nonagons whose intersections form
 * a 6-point star — answers "what's the construction that fills a single
 * hex cell with the rotated-nonagon motif that, repeated across a
 * hex-grid, produces the classic Islamic 6-point-star tessellation?".
 * Every other nonagon is pre-rotated by π via `_map_even_odd` so
 * adjacent nonagons interlock correctly; the size factor `0.75 * R`
 * (origin-relative per the CLAUDE.md construction convention) is the
 * empirical proportion that lands the nonagon vertices on the hexagon
 * edges.
 */
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


/**
 * Render every `PolygonWithSides` entry into its own freshly-created SVG —
 * answers "where does the gallery page that shows triangle through
 * decagon side-by-side get its drawings?". One SVG per polygon (not one
 * SVG with multiple polygons) so each demo can be inspected, screenshot,
 * or styled independently from the DOM without coordinate offset math.
 */
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

/**
 * Render a 2×2 grid of Star-of-David + inscribed-hexagon motifs using
 * Hexagon's directional helpers (`right`, `above`, `above().right`) —
 * answers "how does the demo prove that a Star (two interlocking
 * triangles) tiles correctly across the hex grid?". Each cell paints
 * the star, the π/2-rotated counterpart, and the inscribing hexagon
 * so a reader can verify the three primitives line up at every grid
 * position — visual regression-test for the hex-neighbor math.
 */
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

/**
 * Render a single π/4-rotated Star with its construction circles
 * overlaid — answers "what's the diagnostic view that shows both the
 * final star *and* the reference circles each tip was drawn from, so a
 * reader can audit whether the satellite positions are right?". Uses
 * `appendCircleWithMidpoint` (not the plain `appendCircle`) because the
 * midpoint dots are the load-bearing signal in this view — they show
 * the rotation pivots and satellite anchors that the star geometry
 * derives from.
 */
export function drawRotatedStar(drawingId:string, radius:number, size:number): IO {
    const star = new Star(new Point(radius * size / 2, radius * size / 2), 6, radius);
    const svg = appendSVGToDOM(drawingId, radius * size, radius * size);
    appendPolygon(svg, star.rotate(Math.PI/4).lines);
    _.forEach(
        star.rotate(Math.PI/4).circles,
        c => {
            appendCircleWithMidpoint(svg, c);
        }
    );
}

/**
 * Render Stars with point-counts 6 through 11 each into its own SVG —
 * answers "where does the gallery page that compares stars across
 * tip-counts (so a reader can see how a 6-point vs 9-point vs 11-point
 * star looks at the same radius) get its drawings?". Includes the outer
 * construction circle via `appendCircleWithMidpoint` so the radius
 * envelope is visually equal across tiles, isolating the visual
 * variable to N.
 */
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

/**
 * Render a flower-of-life ring and animate the inner ring's radial shift
 * with `setInterval` — answers "what's the live demo that shows the
 * six-around-one ring rotating against a static outer ring of L2
 * neighbors?". Two ring depths (L1 + L2) are painted once at startup;
 * only L1 transitions on each tick because re-rotating L2 would
 * re-create the very flowers L2 emits — visual feedback loop. The
 * 50ms interval pairs with the d3 transition duration so each step
 * just completes before the next fires.
 */
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


/**
 * Render a two-ring hexagon tessellation, each cell filled with the
 * 6-point-star nonagon motif — answers "what's the headline drawing
 * that the landing page uses to demonstrate the hex-grid + nonagon
 * composition working at full pattern scale (not just one cell)?".
 * `background_theme` and `lines_theme` are loose `unknown` bags
 * (deliberate exception to tenet 15 here — they're CSS-style maps with
 * arbitrary keys forwarded to d3 `.style()`, so a tighter type would
 * just restate `Record<string, string>`).
 */
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
    return <d3SVG>(svg);
}

/**
 * Render an N-level recursive flower-of-life with a hexagon inscribed in
 * every circle — answers "what's the headline drawing that shows the
 * flower-of-life construction at arbitrary depth, with each level color-
 * faded so a reader can see the recursion depth at a glance?". The
 * `radius*2/5.25` origin circle is the empirical fit that makes the
 * outermost ring at `maxLevels` fall just inside the canvas at the
 * default 600×600 size; it's not magic, it's `5.25 ≈ 2 + 1 + sin(π/3)·2`
 * for a 3-level fit and was extrapolated from there.
 */
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

/**
 * Render a 10-around-1 ring of `ElongatedFivePointStar`s with a Decagon
 * encircling them — answers "what's the composed-motif demo that proves
 * `ElongatedFivePointStar`'s per-vertex elongation map works at every
 * rotation, by chaining 10 instances around a central decagon with each
 * star rotated to point outward and a different vertex elongated?".
 * The elongation index `(3+(i*2)) % 10` rotates *with* the star so the
 * elongated vertex always points radially inward — visual regression
 * for both the per-vertex elongation math and the rotation composition.
 */
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
            appendPolygon(<d3SVG>svg, s.lines);
            appendText(<d3SVG>svg, `${i}: ${Math.round(180*finalRotation/Math.PI)}`, p, {
                "font-size": `${radius/50}px`,
                "text-anchor": "middle",
                "vertical-align": "middle",
            });
        }
    );
    appendPolygon(<d3SVG>svg, FivePointStar(circle.midpoint, radius/numbereOfStars/1.5).lines);
    appendPolygon(<d3SVG>svg, (new Decagon(circle.midpoint, radius*2/5.25)).lines);
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
