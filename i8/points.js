"use strict";
var Point = /** @class */ (function () {
    function Point(x, y) {
        this.x = x;
        this.y = y;
    }
    Point.distanceBetweenPoints = function (p1, p2) {
        var _a = [p1.x, p1.y], x1 = _a[0], y1 = _a[1];
        var _b = [p2.x, p2.y], x2 = _b[0], y2 = _b[1];
        // https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
        return Math.hypot(x2 - x1, y2 - y1);
    };
    Point.prototype.isUnder = function (p2) {
        return this.y < p2.y;
    };
    Point.prototype.isInQuadrant1 = function (p2) {
        // Assuming the current point is at (0,0), is the supplied point north east of it
        var _a = [this.x, this.y], x1 = _a[0], y1 = _a[1];
        var _b = [p2.x, p2.y], x2 = _b[0], y2 = _b[1];
        return (x2 >= x1) && (y2 >= y1);
    };
    Point.prototype.isInQuadrant2 = function (p2) {
        // Assuming the current point is at (0,0), is the supplied point north west of it
        var _a = [this.x, this.y], x1 = _a[0], y1 = _a[1];
        var _b = [p2.x, p2.y], x2 = _b[0], y2 = _b[1];
        return (x2 <= x1) && (y2 >= y1);
    };
    Point.prototype.isInQuadrant3 = function (p2) {
        // Assuming the current point is at (0,0), is the supplied point south west of it
        var _a = [this.x, this.y], x1 = _a[0], y1 = _a[1];
        var _b = [p2.x, p2.y], x2 = _b[0], y2 = _b[1];
        return (x2 <= x1) && (y2 <= y1);
    };
    Point.prototype.isInQuadrant4 = function (p2) {
        // Assuming the current point is at (0,0), is the supplied point south east of it
        var _a = [this.x, this.y], x1 = _a[0], y1 = _a[1];
        var _b = [p2.x, p2.y], x2 = _b[0], y2 = _b[1];
        return (x2 >= x1) && (y2 <= y1);
    };
    return Point;
}());
