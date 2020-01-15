function slope(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (y2 - y1) / (x2 - x1);
}

function isHorizontalLine(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    if (y2 === y1 || Math.abs(slope(p1, p2)) < (1.0/1000000.0) ) {
        return true;
    }
    return false;
}

function isVerticleLine(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    if (x1 === x2 || Math.abs(slope(p1, p2)) > 1000000) {
        return true;
    }
    return false;
}

function distanceBetweenPoints(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    // https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
    return Math.sqrt(Math.pow(x2-x1, 2) + Math.pow(y2-y1, 2))
}

function extendLineRight(p1, p2, newDistance) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    if (isHorizontalLine(p1, p2)) {
        return [x1+newDistance, y1];
    }
    var currentDistance = distanceBetweenPoints(p1, p2);
    if (slope(p1, p2) > 0) {
        return [
            x1 + ((newDistance*Math.abs(x2-x1))/currentDistance),
            y1 + ((newDistance*Math.abs(y2-y1))/currentDistance)
        ];
    }
    else {
        return [
            x1 + ((newDistance*Math.abs(x2-x1))/currentDistance),
            y1 - ((newDistance*Math.abs(y2-y1))/currentDistance)
        ];
    }
}

function extendLineLeft(p1, p2, newDistance) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    if (isHorizontalLine(p1, p2)) {
        return [x1-newDistance, y1];
    }
    var currentDistance = distanceBetweenPoints(p1, p2);
    if (slope(p1, p2) > 0) {
        return [
            x1 - ((newDistance*Math.abs(x2-x1))/currentDistance),
            y1 - ((newDistance*Math.abs(y2-y1))/currentDistance)
        ];
    }
    else {
        return [
            x1 - ((newDistance*Math.abs(x2-x1))/currentDistance),
            y1 + ((newDistance*Math.abs(y2-y1))/currentDistance)
        ];
    }
}

function extendLine(p1, p2, newDistance) {
    console.log("Extending line between", p1, p2);
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    if (isVerticleLine(p1, p2)) {
        // y2 under y1 ...
        if (y2 < y1) {
            return [x2, y1-newDistance];
        }
        return [x2, y1+newDistance];
    }
    if (inQuadrant2(p1, p2) || inQuadrant3(p1, p2)) {
        return extendLineLeft(p1, p2, newDistance);
    }
    return extendLineRight(p1, p2, newDistance);
}
