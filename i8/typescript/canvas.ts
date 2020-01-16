// https://www.typescriptlang.org/docs/handbook/advanced-types.html
// https://www.logicbig.com/tutorials/misc/typescript/ts-config-json.html

type d3SvgElement<T extends d3.BaseType> = d3.Selection<T, unknown, HTMLElement, any>;
// type d3SvgElement<T extends d3.BaseType> = d3.Selection<T, {}, HTMLElement, any> | d3.Selection<T, unknown, HTMLElement, any>;
type d3SVG = d3SvgElement<SVGSVGElement>;
type d3CIRCLE = d3SvgElement<SVGCircleElement>;
type d3LINE = d3SvgElement<SVGLineElement>;

// Introspecting types ...
// var x = d3.select("body");
// var x = d3.select("body").append("line");
// var x = d3.select("body").append("circle");

function colorForLevel(level?:number, maxLevels?:number){
    // The higher the level ... the more clear ...
    if (_.isEmpty(level) || _.isEmpty(maxLevels)) {
        return 'red';
    }
    else {
        var color = 200 / ((200 / (<number>maxLevels + 1)) * (<number>level + 1));
        return `rgba(${color},${color},${color},${Math.min(1, (<number>level + 1)/(<number>maxLevels + 1))})`;
    }
}

function appendCircleWithMidpoint(onto:d3SVG, c:Circle, maxLevels?:number) {
    console.log("HIIIII", c);
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
