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

/* eslint-disable-next-line no-unused-vars, no-redeclare */
export function appendText(onto:d3SVG, text:string, point:Point, metadata:unknown={}): IO {
    const x = (<d3TEXT>onto.append("text"))
        .attr("x", point.x)
        .attr("y", point.y)
        .style('stroke', _.get(metadata, "stroke", "black"))
        .style('stroke-width', _.get(metadata, "stroke-width", "1"))
        .style('fill', _.get(metadata, "fill", 'none'))
        .text((_) => <string>text);
    _.forOwn(
        metadata,
        (value,  key) => {
            x.style(key, value)
        }
    )
}
