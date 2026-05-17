import * as _ from "lodash";
import {Circle} from "./circles"
import {Line} from "./lines"
import {Point} from "./points"
import {IO} from "./types"
import {all} from "./helpers"

// https://www.typescriptlang.org/docs/handbook/advanced-types.html
// https://www.logicbig.com/tutorials/misc/typescript/ts-config-json.html

// type d3SvgElement<T extends d3.BaseType> = d3.Selection<T, {}, HTMLElement, any> | d3.Selection<T, unknown, HTMLElement, any>;
export type d3SvgElement<T extends d3.BaseType> = d3.Selection<T, unknown, HTMLElement, unknown>;
export type d3SVG = d3SvgElement<SVGSVGElement>;
export type d3CIRCLE = d3SvgElement<SVGCircleElement>;
export type d3LINE = d3SvgElement<SVGLineElement>;
export type d3POLYLINE = d3SvgElement<SVGPolylineElement>;
export type d3TEXT = d3SvgElement<SVGTextElement>;

// Introspecting types ...
// let x = d3.select("body");
// let x = d3.select("body").append("line");
// let x = d3.select("body").append("circle");

/**
 * Map a recursion level to a fading grayscale color — answers "how does a
 * recursive flower-of-life diagram (or any nested-circle pattern) signal
 * depth visually so an observer can read 'this circle is two levels deep'
 * without counting outward from the center?". Higher levels render lighter
 * (more transparent), so the eye reads the deepest construction primitives
 * as background scaffolding and the surface-level shapes as figure. Falls
 * back to opaque red when either argument is undefined, making un-tagged
 * shapes visually loud (tenet 3: surface, don't hide).
 */
export function colorForLevel(level?:number, maxLevels?:number): string {
    console.log(level, maxLevels);
    // The higher the level ... the more clear ...
    if (_.isUndefined(level) || _.isUndefined(maxLevels)) {
        return 'red';
    }
    else {
        const color = 200 / ((200 / (<number>maxLevels + 1)) * (<number>level + 1));
        return `rgba(${color},${color},${color},${Math.min(1, (<number>level + 1)/(<number>maxLevels + 1))})`;
    }
}

/**
 * Render a circle and a dot at its center — answers "how do construction
 * overlays show both the reference frame (the circle) AND its anchor
 * (the midpoint) in one operation, so a reader can tell which circles
 * are load-bearing reference geometry vs. Decoration?". Used for
 * debugging-and-teaching renders where the center point itself carries
 * meaning (rotation pivots, surrounding-circle anchors); production
 * draws use `appendCircle` instead, which leaves the midpoint implicit.
 */
export function appendCircleWithMidpoint(onto:d3SVG, c:Circle, maxLevels?:number): IO {
    console.log("HIIIII", c, c.metadata, maxLevels);
    // Append Circle
    (<d3CIRCLE>onto.append('circle'))
      .attr('cx', c.x)
      .attr('cy', c.y)
      .attr('r', c.r)
      .attr('stroke', colorForLevel(c.metadata.level, maxLevels))
      // .attr('stroke', 'black')
      .attr('fill', 'none');
    // Append Midpoint
    (<d3CIRCLE>onto.append('circle'))
      .attr('cx', c.x)
      .attr('cy', c.y)
      .attr('r', 1)
      .attr('stroke', colorForLevel(c.metadata.level, maxLevels))
      // .attr('stroke', 'black');
      .attr('fill', colorForLevel(c.metadata.level, maxLevels));
}


// function applyStylesTo(to, styleParams, defaultStyleParams) {
//
// }

/**
 * Render a Circle primitive into a D3 SVG selection — answers "how does
 * construction code lift a pure-geometry `Circle` (no styling) into a
 * styled SVG element while honoring per-instance metadata overrides
 * (stroke, fill) and falling back to recursion-level coloring when no
 * override is set?". Returns the d3 selection so the caller can chain
 * further attributes for one-off cases without forcing every render
 * site to re-derive coordinates.
 */
export function appendCircle(onto:d3SVG, c:Circle, maxLevels?:number): d3CIRCLE {
    console.log("HIIIII", c, c.metadata, maxLevels);
    // Append Circle
    return (
        (<d3CIRCLE>onto.append('circle'))
          .attr('cx', c.x)
          .attr('cy', c.y)
          .attr('r', c.r)
          .attr('stroke', _.get(c.metadata, "stroke", colorForLevel(c.metadata.level, maxLevels)))
          .attr('fill', _.get(c.metadata, "fill", 'none'))
    );
}

/**
 * Render a Line primitive into a D3 SVG selection — answers "what is the
 * straight-line analog of `appendCircle` that takes a pure-geometry
 * `Line` (just two `Point`s, no style) and paints it?". Color is the
 * only style argument because Line callers (star-edge construction,
 * polygon-edge rendering) typically style by group (all star edges
 * black; all guide lines red) rather than per-instance, so a single
 * color parameter is the right granularity at this layer.
 */
export function appendLine(onto:d3SVG, l:Line, color="black"): IO {
    console.log("Drawing Line From", l.p1, " to ", l.p2);
    (<d3LINE>onto.append("line"))
       .attr("x1", l.p1.x)
       .attr("y1", l.p1.y)
       .attr("x2", l.p2.x)
       .attr("y2", l.p2.y)
       .attr("class", "line")
       .style("stroke", color);
}

/**
 * Render a polygon as a single SVG `polyline` from an ordered list of
 * connected `Line` segments — answers "how does construction code paint
 * a closed-or-open polygon as one DOM element (so it fills correctly and
 * can be styled atomically) instead of N independent `line` elements
 * that wouldn't honor `fill`?". Assumes the input lines are pre-ordered
 * tip-to-tail (the construction layer guarantees this); silently no-ops
 * on empty input rather than producing a stray DOM element, since the
 * caller's intent for "no lines" is unambiguously "draw nothing.".
 */
export function appendPolygon(onto:d3SVG, lines:Line[], metadata:unknown={}): IO {
    // Assumes lines are in connected order ...
    if (_.isEmpty(lines) || all(lines, _.isEmpty) ) {
        return;
    }
    const last_line = (<Line>_.last(lines));
    console.log(last_line);
    const last_point = [last_line.p2.x, last_line.p2.y];
    // Skip over the ending points of the line ... except for the last line ...
    const points = _.concat(_.map(lines, l => [l.p1.x, l.p1.y]), [last_point]);
    const poly_points = _.join(_.map(points, p =>_.join(p, ",")), ", ");
    (<d3POLYLINE>onto.append("polyline"))
        .style('stroke', _.get(metadata, "stroke", "black"))
        .style('stroke-width', _.get(metadata, "stroke-width", "1"))
        .style('fill', _.get(metadata, "fill", 'none'))
        .attr("points", poly_points);
        
}

/**
 * Render a text label at a point with arbitrary style overrides —
 * answers "how does diagnostic overlay code drop a label (vertex index,
 * coordinate readout, debug tag) at an exact geometric location with
 * full per-instance style control?". Unlike `appendLine`/`appendCircle`
 * which pin styles to a small fixed set, text labels vary widely
 * (font-size, text-anchor, dominant-baseline) so the metadata bag is
 * iterated and each key applied as a CSS style — accepting the loose
 * contract here because debug rendering shouldn't force a typed style
 * model on every caller.
 */
export function appendText(onto:d3SVG, text:string, point:Point, metadata:unknown={}): IO {
    const x = (<d3TEXT>onto.append("text"))
        .attr("x", point.x)
        .attr("y", point.y)
        .style('stroke', _.get(metadata, "stroke", "black"))
        .style('stroke-width', _.get(metadata, "stroke-width", "1"))
        .style('fill', _.get(metadata, "fill", 'none'))
        .text(() => <string>text);
    _.forOwn(
        metadata,
        (value,  key) => {
            x.style(key, value)
        }
    )
}
