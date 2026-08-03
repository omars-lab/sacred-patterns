import {Circle} from "./circles"
import {Line} from "./lines"
import {Point} from "./points"
import {IO, d3SVG, d3CIRCLE, d3LINE, d3POLYLINE, d3TEXT} from "./types"
import {all} from "./helpers"

/* eslint-disable-next-line no-unused-vars, no-redeclare */
import * as _ from "lodash";

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
export function appendCircleWithMidpoint(onto:d3SVG, c:Circle, color:string="black"): IO {
    console.log("HIIIII", c, c.metadata, color);
    appendCircle(onto, c, color);
    appendMidpoint(onto, c, color);
}

// colorForLevel(c.metadata.level, maxLevels)

/* eslint-disable-next-line no-unused-vars, no-redeclare */
export function appendCircle(onto:d3SVG, c:Circle, color:string="black", metadata:unknown={}): d3CIRCLE {
    console.log("HIIIII", c, c.metadata, color);
    // Append Circle
    const x = (
        (<d3CIRCLE>onto.append('circle'))
          .attr('cx', c.x)
          .attr('cy', c.y)
          .attr('r', c.r)
          .attr('stroke', _.get(c.metadata, "stroke", color))
          .attr('fill', _.get(c.metadata, "fill", 'none'))
    );
    _.forOwn(
        metadata,
        (value,  key) => {
            x.style(key, value)
        }
    )
    return x;
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
export function appendMidpoint(onto:d3SVG, c:Circle, color:string="black", metadata:unknown={}): d3CIRCLE {
    console.log("HIIIII", c, c.metadata, color);
    // Append Midpoint
    return (
        appendPoint(onto, c.midpoint, color, metadata)
        // appendPoint(onto, c.midpoint, _.get(c.metadata, "stroke", color))
        // appendPoint(onto, c.midpoint, _.get(c.metadata, "fill", 'none'))
    );
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
export function appendPoint(onto:d3SVG, p:Point, color:string="black", metadata:unknown={}): d3CIRCLE {
    console.log("HIIIII", p, color);
    // Append Midpoint
    const x = (
        (<d3CIRCLE>onto.append('circle'))
        .attr('cx', p.x)
        .attr('cy', p.y)
        .attr('r', 1)
        .attr('stroke', color)
        // .attr('stroke', _.get(c.metadata, "stroke", color))
        .attr('fill', color)
        // .attr('fill', _.get(c.metadata, "fill", 'none'))
    );
    _.forOwn(
        metadata,
        (value,  key) => {
            x.style(key, value)
        }
    )
    return x;
}
/* eslint-disable-next-line no-unused-vars, no-redeclare */
export function appendLine(onto:d3SVG, l:Line, color="black", metadata:unknown={}): d3LINE {
    console.log("Drawing Line From", l.p1, " to ", l.p2);
    const x = (<d3LINE>onto.append("line"))
       .attr("x1", l.p1.x)
       .attr("y1", l.p1.y)
       .attr("x2", l.p2.x)
       .attr("y2", l.p2.y)
       .attr("class", "line")
       .style("stroke", color);
    _.forOwn(
        metadata,
        (value,  key) => {
            x.style(key, value)
        }
    )
    return x;
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
export function appendPolygon(onto:d3SVG, lines:Line[], metadata:unknown={}): d3POLYLINE | undefined {
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
    return (<d3POLYLINE>onto.append("polyline"))
        .style('stroke', _.get(metadata, "stroke", "black"))
        .style('stroke-width', _.get(metadata, "stroke-width", "1"))
        .style('fill', _.get(metadata, "fill", 'none'))
        .attr("points", poly_points);
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
export function appendText(onto:d3SVG, text:string, point:Point, metadata:unknown={}): d3TEXT {
    const color = _.get(metadata, "stroke", "black");
    const x = (<d3TEXT>onto.append("text"))
        .attr("x", point.x)
        .attr("y", point.y)
        .style('stroke', color)
        .style('stroke-width', _.get(metadata, "stroke-width", "1"))
        .style('fill', _.get(metadata, "fill", 'none'))
        .text((_) => <string>text);
    _.forOwn(
        metadata,
        (value,  key) => {
            x.style(key, value)
        }
    )
    appendPoint(onto, point, color);
    return x;
}
