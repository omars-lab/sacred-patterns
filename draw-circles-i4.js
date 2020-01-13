function circleId(x, y, r) {
    return `x:${Math.ceil(x)}-y:${Math.ceil(y)}-r:${r}`;
}

function colorForLevel(level, maxLevels){
    // The higher the level ... the more clear ...
    if (level === undefined) {
        return 'red';
    }
    else {
        var color = 200 / ((200 / (maxLevels + 1)) * (level + 1));
        return `rgba(${color},${color},${color},${Math.min(1, (level + 1)/(maxLevels + 1))})`;
    }
}

function circle(x, y, r, level = undefined) {
    return _.fromPairs([
        [
            circleId(x, y, r),
            {
                x,
                y,
                r,
                level
            }
        ]
    ])
}

function circlesAround(c, count, level) {
    const {x, y, r} = c;
    var circles = _.map(
        _.range(0, 2 * Math.PI, 2 * Math.PI / count),
        radians => circle(
            x + (Math.cos(radians) * r),
            y + (Math.sin(radians) * r),
            r,
            level
        )
    );
    // console.log(c, circles);
    return circles;
}

function flowersAround(x, y, r, currentRecursionLevel) {
    return circlesAround({x:x, y:y, r:r}, 6, currentRecursionLevel);
}

function pickHigherLevel(ca, cb) {
    if (_.isEmpty(ca) || _.isEmpty(cb)) {
        return undefined;
    }
  if (ca.level >= cb.level) {
      // console.log('picked ca over cb', ca, cb);
      return ca;
  }
  // console.log('picked cb over ca', ca, cb);
  return cb;
}

// Returns Circles that will get drawn ...
function appendFlowersRecursively(x, y, r, recursionLevel) {
    var circlesToDraw = {};
    var aroundCenter = flowersAround(x, y, r, recursionLevel);
    // console.log("around center", aroundCenter);
    circlesToDraw = _.merge({}, ...aroundCenter);
    if (recursionLevel > 0) {
        var recursiveCircles = _.map(
            _.flatMap(
                circlesAround({x:x, y:y, r:r}, 6),
                _.values,
            ),
            (c) => appendFlowersRecursively(
                c.x,
                c.y,
                c.r,
                recursionLevel - 1
            )
        );
        // console.log("recursiveCircles", recursiveCircles);
        circlesToDraw = _.mergeWith({}, circlesToDraw, ...recursiveCircles, pickHigherLevel);
    }
    // console.log("circlesToDraw", circlesToDraw);
    return circlesToDraw;
}

function appendCircleWithMidpoint(onto, c) {
    // Append Circle
    onto.append('circle')
      .attr('cx', c.x)
      .attr('cy', c.y)
      .attr('r', c.r)
      .attr('stroke', colorForLevel(c.level, maxLevels))
      // .attr('stroke', 'black')
      .attr('fill', 'none');
    // Append Midpoint
    onto.append('circle')
      .attr('cx', c.x)
      .attr('cy', c.y)
      .attr('r', 1)
      .attr('stroke', colorForLevel(c.level, maxLevels))
      // .attr('stroke', 'black');
      .attr('fill', colorForLevel(c.level, maxLevels));
}
