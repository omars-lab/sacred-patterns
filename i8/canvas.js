"use strict";
// https://www.typescriptlang.org/docs/handbook/advanced-types.html
// https://www.logicbig.com/tutorials/misc/typescript/ts-config-json.html
// Introspecting types ...
// var x = d3.select("body");
// var x = d3.select("body").append("line");
// var x = d3.select("body").append("circle");
function colorForLevel(level, maxLevels) {
    // The higher the level ... the more clear ...
    if (_.isEmpty(level) || _.isEmpty(maxLevels)) {
        return 'red';
    }
    else {
        var color = 200 / ((200 / (maxLevels + 1)) * (level + 1));
        return "rgba(" + color + "," + color + "," + color + "," + Math.min(1, (level + 1) / (maxLevels + 1)) + ")";
    }
}
function appendCircleWithMidpoint(onto, c, maxLevels) {
    console.log("HIIIII", c);
    // Append Circle
    onto.append('circle')
        .attr('cx', c.x)
        .attr('cy', c.y)
        .attr('r', c.r)
        .attr('stroke', colorForLevel(c.metadata.level, maxLevels))
        // .attr('stroke', 'black')
        .attr('fill', 'none');
    // Append Midpoint
    onto.append('circle')
        .attr('cx', c.x)
        .attr('cy', c.y)
        .attr('r', 1)
        .attr('stroke', colorForLevel(c.metadata.level, maxLevels))
        // .attr('stroke', 'black');
        .attr('fill', colorForLevel(c.metadata.level, maxLevels));
}
function appendLine(onto, l, color) {
    if (color === void 0) { color = "black"; }
    console.log("Drawing Line From", l.p1, " to ", l.p2);
    onto.append("line")
        .attr("x1", l.p1.x)
        .attr("y1", l.p1.y)
        .attr("x2", l.p2.x)
        .attr("y2", l.p2.y)
        .attr("class", "line")
        .style("stroke", color);
}
