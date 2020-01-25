"use strict";
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Circle = /** @class */ (function () {
    function Circle(x, y, r, _metadata) {
        this.x = x;
        this.y = y;
        this.r = r;
        this._metadata = _metadata;
    }
    Object.defineProperty(Circle.prototype, "id", {
        get: function () {
            return "x:" + Math.ceil(this.x) + "-y:" + Math.ceil(this.y) + "-r:" + this.r;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Circle.prototype, "metadata", {
        get: function () {
            return _.isEmpty(this._metadata) ? {} : this._metadata;
        },
        enumerable: true,
        configurable: true
    });
    Circle.prototype.pointsOnCircumference = function (numberOfPoints, shift_in_radians) {
        var _this = this;
        if (shift_in_radians === void 0) { shift_in_radians = 0; }
        return _.map(_.range(0, 2 * Math.PI, 2 * Math.PI / numberOfPoints), function (radians) { return _this.pointOnCircumferenceAtRadian(radians + shift_in_radians); });
    };
    Circle.prototype.pointOnCircumferenceAtRadian = function (radian) {
        return new Point(this.x + (Math.cos(radian) * this.r), this.y + (Math.sin(radian) * this.r));
    };
    Circle.prototype.pointOnCircumferenceAtDegree = function (degree) {
        return this.pointOnCircumferenceAtRadian((degree / 360.0) * 2 * Math.PI);
    };
    // circlesAround
    // https://stackoverflow.com/questions/17186566/how-do-i-fix-error-ts1015-parameter-cannot-have-question-mark-and-initializer
    Circle.prototype.surroundingCircles = function (count, distance_modifier, shift_in_radians, metadata) {
        if (distance_modifier === void 0) { distance_modifier = 1; }
        if (shift_in_radians === void 0) { shift_in_radians = 0; }
        if (metadata === void 0) { metadata = undefined; }
        var _a = this, x = _a.x, y = _a.y, r = _a.r;
        var circles = _.map(_.range(0, 2 * Math.PI, 2 * Math.PI / count), function (radians) { return new Circle(x + (Math.cos(radians + shift_in_radians) * r * distance_modifier), y + (Math.sin(radians + shift_in_radians) * r * distance_modifier), r, _.isEmpty(metadata) ? undefined : _.merge({}, metadata)); });
        return circles;
    };
    // flowersAround
    Circle.prototype.surroundWithFlower = function (metadata) {
        return this.surroundingCircles(6, 1, 0, metadata);
    };
    Circle.indexCircles = function (circles) {
        return _.fromPairs(_.map(circles, function (c) { return [c.id, c]; }));
    };
    // appendFlowersRecursively
    Circle.prototype._surroundWithFlowersRecursively = function (recursionLevel) {
        // Returns Circles that will get drawn ...
        var circlesToDraw = {};
        var aroundCenter = Circle.indexCircles(this.surroundWithFlower({ level: recursionLevel }));
        console.log("around center", aroundCenter);
        circlesToDraw = _.merge({}, aroundCenter);
        if (recursionLevel > 1) {
            var recursiveCircles = _.flatMap(this.surroundWithFlower({ level: recursionLevel - 1 }), function (c) { return c._surroundWithFlowersRecursively(recursionLevel - 1); });
            console.log("recursiveCircles", recursiveCircles);
            circlesToDraw = _.mergeWith.apply(_, [{}, circlesToDraw].concat(recursiveCircles, [Circle.pickHigherLevel]));
        }
        // console.log("circlesToDraw", circlesToDraw);
        return circlesToDraw;
    };
    Circle.prototype.surroundWithFlowersRecursively = function (recursionLevel) {
        return _.values(this._surroundWithFlowersRecursively(recursionLevel));
    };
    Object.defineProperty(Circle.prototype, "midpoint", {
        get: function () {
            return new Point(this.x, this.y);
        },
        enumerable: true,
        configurable: true
    });
    Circle.lineBetweenMidpoints = function (c1, c2) {
        return new Line(c1.midpoint, c2.midpoint);
    };
    Circle.pickHigherLevel = function (ca, cb) {
        if (_.isUndefined(ca) || _.isUndefined(cb)) {
            return undefined;
        }
        // https://dzone.com/articles/using-casting-typescript
        if (ca.metadata.level >= cb.metadata.level) {
            // console.log('picked ca over cb', ca, cb);
            return ca;
        }
        // console.log('picked cb over ca', ca, cb);
        return cb;
    };
    Circle.prototype.adjacent = function (x_shift, y_shift, r_scaler, metadata) {
        if (x_shift === void 0) { x_shift = 0; }
        if (y_shift === void 0) { y_shift = 0; }
        if (r_scaler === void 0) { r_scaler = 1; }
        if (metadata === void 0) { metadata = this.metadata; }
        console.log(this);
        return new Circle(this.x + x_shift, this.y + y_shift, this.r * r_scaler, metadata);
    };
    // These ratios ... are so hexagons are above each other ... not circless ...
    Circle.prototype.above = function () {
        return this.adjacent(0, -(this.r * 1.725));
    };
    Circle.prototype.below = function () {
        return this.adjacent(0, (this.r * 1.725));
    };
    Circle.prototype.right = function () {
        return this.adjacent(-(this.r * 2.15), 0);
    };
    Circle.prototype.left = function () {
        return this.adjacent((this.r * 2.15), 0);
    };
    Circle.prototype.northWest = function () {
        // https://riptutorial.com/d3-js/example/8402/coordinate-system
        // in s3 ... 0,0 is top left of screen ... not top right ...
        return this.adjacent(-1 * Math.cos(Math.PI / 4 + Math.PI * 1.5) * this.r * 2.15, Math.sin(Math.PI / 4 + Math.PI * 1.5) * this.r * 1.2);
    };
    Circle.prototype.southEast = function () {
        // https://riptutorial.com/d3-js/example/8402/coordinate-system
        // in s3 ... 0,0 is top left of screen ... not top right ...
        return this.adjacent(Math.cos(Math.PI / 4 + Math.PI * 1.5) * this.r * 2.15, -1 * Math.sin(Math.PI / 4 + Math.PI * 1.5) * this.r * 1.2);
    };
    return Circle;
}());
