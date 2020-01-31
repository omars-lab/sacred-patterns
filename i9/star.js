"use strict";
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Star = /** @class */ (function () {
    function Star(center, numberOfPoints, size, radial_shift) {
        if (radial_shift === void 0) { radial_shift = 0; }
        this.center = center;
        this.numberOfPoints = numberOfPoints;
        this.size = size;
        this.radial_shift = radial_shift;
    }
    Object.defineProperty(Star.prototype, "centralCircle", {
        get: function () {
            return new Circle(this.center.x, this.center.y, this.size);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Star.prototype, "innerCircles", {
        get: function () {
            return this.centralCircle.surroundingCircles(this.numberOfPoints, undefined, this.radial_shift);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Star.prototype, "outerCircle", {
        get: function () {
            return new Circle(this.center.x, this.center.y, this.size * 2);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Star.prototype, "circles", {
        get: function () {
            return _.concat([this.centralCircle], this.innerCircles, [this.outerCircle]);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Star.prototype, "points", {
        get: function () {
            var _this = this;
            var _points = [];
            console.log(this.radial_shift);
            _points.push(this.centralCircle.pointOnCircumferenceAtRadian(0 + this.radial_shift));
            _.forEach(_.range(0, this.numberOfPoints), 
            // 2 * Math.PI, 2 * Math.PI /
            function (circleIndex) {
                var radian = ((circleIndex + 1) * 2 * Math.PI / _this.numberOfPoints) + _this.radial_shift;
                _points.push(_this.innerCircles[circleIndex].pointOnCircumferenceAtRadian(radian));
                _points.push(_this.centralCircle.pointOnCircumferenceAtRadian(radian));
            });
            _points.push(this.centralCircle.pointOnCircumferenceAtRadian(0 + this.radial_shift));
            // Drawing page 16 from Islamic Design
            // - 01st point ... on Center Circle ...               at its  000th degree
            // - 02nd point ... on 1st circle (00d from center)    at its  045th degree
            // - 03rd point ... on Center Circle ...               at its  045th degree
            // - 04th point ... on 2nd circle (45d from center)    at its  135th degree
            // - 05th point ... on Center Circle ...               at its  135th degree
            // - 06th point ... on 3rd circle (135d from center)   at its  180th degree
            // - 07th point ... on Center Circle ...               at its  180th degree
            // - 08th point ... on 4th circle (180d from center)   at its  225th degree
            // - 09th point ... on Center Circle ...               at its  225th degree
            // - 10th point ... on 5th circle (225d from center)   at its  315th degree
            // - 11th point ... on Center Circle ...               at its  315th degree
            // - 12th point ... on 6th circle (315d from center)   at its  000th degree
            // - 13th point ... on Center Circle ...               at its  000th degree
            console.log(_points);
            return _points;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Star.prototype, "lines", {
        get: function () {
            return Lines.fromPoints(this.points);
        },
        enumerable: true,
        configurable: true
    });
    Star.prototype.rotate = function (radians) {
        return new Star(this.center, this.numberOfPoints, this.size, this.radial_shift + radians);
    };
    Star.prototype.adjacent = function (x, y) {
        if (x === void 0) { x = 0; }
        if (y === void 0) { y = 0; }
        return new Star(new Point(this.center.x + x, this.center.y + y), this.numberOfPoints, this.size, this.radial_shift);
    };
    Star.prototype.above = function () {
        return this.adjacent(0, (this.size * this.size / 1.155));
    };
    Star.prototype.below = function () {
        return this.adjacent(0, -(this.size * this.size / 1.155));
    };
    Star.prototype.right = function () {
        return this.adjacent((this.size * this.size / 1.155), 0);
    };
    Star.prototype.left = function () {
        return this.adjacent(-(this.size * this.size / 1.155), 0);
    };
    return Star;
}());
