// https://www.typescriptlang.org/docs/handbook/advanced-types.html
// https://www.logicbig.com/tutorials/misc/typescript/ts-config-json.html

type d3SvgElement<T extends d3.BaseType> = d3.Selection<T, unknown, HTMLElement, any>;
// type d3SvgElement<T extends d3.BaseType> = d3.Selection<T, {}, HTMLElement, any> | d3.Selection<T, unknown, HTMLElement, any>;
type d3SVG = d3SvgElement<SVGSVGElement>;
type d3CIRCLE = d3SvgElement<SVGCircleElement>;
type d3LINE = d3SvgElement<SVGLineElement>;
type d3POLYLINE = d3SvgElement<SVGPolylineElement>;

// Introspecting types ...
// var x = d3.select("body");
// var x = d3.select("body").append("line");
// var x = d3.select("body").append("circle");

function colorForLevel(level?:number, maxLevels?:number){
    console.log(level, maxLevels);
    // The higher the level ... the more clear ...
    if (_.isUndefined(level) || _.isUndefined(maxLevels)) {
        return 'red';
    }
    else {
        var color = 200 / ((200 / (<number>maxLevels + 1)) * (<number>level + 1));
        return `rgba(${color},${color},${color},${Math.min(1, (<number>level + 1)/(<number>maxLevels + 1))})`;
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
function appendCircleWithMidpoint(onto:d3SVG, c:Circle, maxLevels?:number) {
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
function appendCircle(onto:d3SVG, c:Circle, maxLevels?:number) {
    console.log("HIIIII", c, c.metadata, maxLevels);
    // Append Circle
    return (
        (<d3CIRCLE>onto.append('circle'))
          .attr('cx', c.x)
          .attr('cy', c.y)
          .attr('r', c.r)
          .attr('stroke', colorForLevel(c.metadata.level, maxLevels))
          // .attr('stroke', 'black')
          .attr('fill', 'none')
    );
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
function appendLine(onto:d3SVG, l:Line, color="black") {
    console.log("Drawing Line From", l.p1, " to ", l.p2);
    (<d3LINE>onto.append("line"))
       .attr("x1", l.p1.x)
       .attr("y1", l.p1.y)
       .attr("x2", l.p2.x)
       .attr("y2", l.p2.y)
       .attr("class","line")
       .style("stroke", color);
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
function appendPolygon(onto:d3SVG, lines:Line[], color="black") {
    // Assumes lines are in connected order ...
    if (_.isEmpty(lines)) {
        return;
    }
    var last_line = (<Line>_.last(lines));
    var last_point = [last_line.p2.x, last_line.p2.y];
    // Skip over the ending points of the line ... except for the last line ...
    var points = _.concat(_.map(lines, l => [l.p1.x, l.p1.y]), [last_point]);
    var poly_points = _.join(_.map(points, p =>_.join(p, ",")), ", ");
    (<d3POLYLINE>onto.append("polyline"))        // attach a polyline
        .style("stroke",color)                   // colour the line
        .style("fill", "none")                   // remove any fill colour
        .attr("points", poly_points);            // x,y points
}
