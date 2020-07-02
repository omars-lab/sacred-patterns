import * as _ from "lodash";
import {Circle} from "./circles"
import {Line} from "./lines"
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

// Introspecting types ...
// let x = d3.select("body");
// let x = d3.select("body").append("line");
// let x = d3.select("body").append("circle");

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

/* eslint-disable-next-line no-unused-vars, no-redeclare */
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

/* eslint-disable-next-line no-unused-vars, no-redeclare */
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

/* eslint-disable-next-line no-unused-vars, no-redeclare */
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

/* eslint-disable-next-line no-unused-vars, no-redeclare */
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
