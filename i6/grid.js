function inQuadrant1(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (x2 >= x1) && (y2 >= y1)
}

function inQuadrant2(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (x2 <= x1) && (y2 >= y1)
}

function inQuadrant3(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (x2 <= x1) && (y2 <= y1)
}

function inQuadrant4(p1, p2) {
    var [x1, y1] = p1;
    var [x2, y2] = p2;
    return (x2 >= x1) && (y2 <= y1)
}
