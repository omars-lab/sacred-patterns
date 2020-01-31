"use strict";
// https://github.com/lodash/lodash/issues/2173
function _rotate_list_right(arr) {
    var arr_copy = _.concat([], arr);
    arr_copy.push(arr_copy.shift());
    return arr_copy;
}
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Line = /** @class */ (function () {
    function Line(p1, p2) {
        this.p1 = p1;
        this.p2 = p2;
    }
    Object.defineProperty(Line.prototype, "dx", {
        get: function () {
            return this.p2.x - this.p1.x;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Line.prototype, "dy", {
        get: function () {
            return this.p2.y - this.p1.y;
        },
        enumerable: true,
        configurable: true
    });
    Line.prototype.slope = function () {
        return this.dy / this.dx;
    };
    // get yIntercept(): Point | undefined {
    //     if (this.isHorizontal() && this.p1.y != 0) {
    //         return undefined;
    //     }
    //
    //     // return
    // }
    Line.prototype.isHorizontal = function () {
        if (this.p1.y === this.p2.y || Math.abs(this.slope()) < (1.0 / 1000000.0)) {
            return true;
        }
        return false;
    };
    Line.prototype.isVerticle = function () {
        if (this.p1.x === this.p2.x || Math.abs(this.slope()) > 1000000) {
            return true;
        }
        return false;
    };
    Line.prototype.distanceBetweenPoints = function () {
        return Point.distanceBetweenPoints(this.p1, this.p2);
    };
    Line.prototype.replaceEndingPoint = function (p2) {
        return new Line(this.p1, p2);
    };
    Line.prototype.extendLineRight = function (newDistance) {
        if (this.isHorizontal()) {
            return this.replaceEndingPoint(new Point(this.p1.x + newDistance, this.p1.y));
        }
        var currentDistance = this.distanceBetweenPoints();
        if (this.slope() > 0) {
            return this.replaceEndingPoint(new Point(this.p1.x + ((newDistance * Math.abs(this.dx)) / currentDistance), this.p1.y + ((newDistance * Math.abs(this.dy)) / currentDistance)));
        }
        else {
            return this.replaceEndingPoint(new Point(this.p1.x + ((newDistance * Math.abs(this.dx)) / currentDistance), this.p1.y - ((newDistance * Math.abs(this.dy)) / currentDistance)));
        }
    };
    Line.prototype.extendLineLeft = function (newDistance) {
        if (this.isHorizontal()) {
            return this.replaceEndingPoint(new Point(this.p1.x - newDistance, this.p1.y));
        }
        var currentDistance = this.distanceBetweenPoints();
        if (this.slope() > 0) {
            return this.replaceEndingPoint(new Point(this.p1.x - ((newDistance * Math.abs(this.dx)) / currentDistance), this.p1.y - ((newDistance * Math.abs(this.dy)) / currentDistance)));
        }
        else {
            return this.replaceEndingPoint(new Point(this.p1.x - ((newDistance * Math.abs(this.dx)) / currentDistance), this.p1.y + ((newDistance * Math.abs(this.dy)) / currentDistance)));
        }
    };
    Line.prototype.extendLine = function (newDistance) {
        console.log("Extending line between", this.p1, this.p2);
        // var [x1, y1] = p1;
        // var [x2, y2] = p2;
        if (this.isVerticle()) {
            if (this.p2.isUnder(this.p1)) {
                return this.replaceEndingPoint(new Point(this.p2.x, this.p1.y - newDistance));
            }
            return this.replaceEndingPoint(new Point(this.p2.x, this.p1.y + newDistance));
        }
        if (this.p1.isInQuadrant2(this.p2) || this.p1.isInQuadrant3(this.p2)) {
            return this.extendLineLeft(newDistance);
        }
        return this.extendLineRight(newDistance);
    };
    return Line;
}());
var Lines = /** @class */ (function () {
    function Lines() {
    }
    Lines.fromPoints = function (points) {
        // Form lines by connecting the points ...
        return _.map(
        // https://www.tutorialsteacher.com/typescript/typescript-tuple
        _.zip(points, _rotate_list_right(points)), function (_a) {
            var p1 = _a[0], p2 = _a[1];
            return new Line(p1, p2);
        });
    };
    return Lines;
}());
