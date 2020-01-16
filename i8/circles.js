"use strict";
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
            var default_metadata = { level: 0 };
            return _.isEmpty(this._metadata) ? default_metadata : this._metadata;
        },
        enumerable: true,
        configurable: true
    });
    // circlesAround
    Circle.prototype.surroundingCircles = function (count, distance_modifier, shift_in_radians, metadata) {
        var _this = this;
        if (distance_modifier === void 0) { distance_modifier = 1; }
        if (shift_in_radians === void 0) { shift_in_radians = 0; }
        if (metadata === void 0) { metadata = {}; }
        var _a = this, x = _a.x, y = _a.y, r = _a.r;
        var circles = _.map(_.range(0, 2 * Math.PI, 2 * Math.PI / count), function (radians) { return new Circle(x + (Math.cos(radians + shift_in_radians) * r * distance_modifier), y + (Math.sin(radians + shift_in_radians) * r * distance_modifier), r, _.merge({}, _this.metadata, _.isEmpty(metadata) ? {} : metadata)); });
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
        if (recursionLevel > 0) {
            var recursiveCircles = Circle.indexCircles(_.flatMap(this.surroundWithFlower({ level: recursionLevel - 1 }), function (c) { return _.values(c._surroundWithFlowersRecursively(recursionLevel - 1)); }));
            console.log("recursiveCircles", recursiveCircles);
            circlesToDraw = _.mergeWith({}, circlesToDraw, recursiveCircles, Circle.pickHigherLevel);
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
        if (_.isEmpty(ca) || _.isEmpty(cb)) {
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
    return Circle;
}());
;
