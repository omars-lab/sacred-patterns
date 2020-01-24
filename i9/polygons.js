"use strict";
// https://codepen.io/Elf/details/rOrRaw
// https://www.d3indepth.com/shapes/
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Polygon = /** @class */ (function () {
    function Polygon(center, size, radial_shift) {
        if (radial_shift === void 0) { radial_shift = 0; }
        this.center = center;
        this.size = size;
        this.radial_shift = radial_shift;
    }
    Object.defineProperty(Polygon.prototype, "number_of_points", {
        get: function () {
            throw "Not Yet Implemented";
        },
        enumerable: true,
        configurable: true
    });
    Polygon.onCircle = function (c) {
        return new Hexagon(new Point(c.midpoint.x, c.midpoint.y), c.r);
    };
    Object.defineProperty(Polygon.prototype, "outerCircle", {
        get: function () {
            return new Circle(this.center.x, this.center.y, this.size);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Polygon.prototype, "points", {
        get: function () {
            var points_of_hexagon = this.outerCircle.pointsOnCircumference(this.number_of_points, this.radial_shift);
            return points_of_hexagon;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Polygon.prototype, "lines", {
        get: function () {
            return Line.fromPoints(this.points);
        },
        enumerable: true,
        configurable: true
    });
    Polygon.prototype.rotate = function (increment_radial_shift) {
        // Make this return a new Polygon polymorphically ...
        this.radial_shift = this.radial_shift + increment_radial_shift;
        return this;
    };
    return Polygon;
}());
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Triangle = /** @class */ (function (_super) {
    __extends(Triangle, _super);
    function Triangle() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(Triangle.prototype, "number_of_points", {
        get: function () {
            return 3;
        },
        enumerable: true,
        configurable: true
    });
    return Triangle;
}(Polygon));
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Square = /** @class */ (function (_super) {
    __extends(Square, _super);
    function Square() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(Square.prototype, "number_of_points", {
        get: function () {
            return 4;
        },
        enumerable: true,
        configurable: true
    });
    return Square;
}(Polygon));
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Pentagon = /** @class */ (function (_super) {
    __extends(Pentagon, _super);
    function Pentagon() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(Pentagon.prototype, "number_of_points", {
        get: function () {
            return 5;
        },
        enumerable: true,
        configurable: true
    });
    return Pentagon;
}(Polygon));
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Hexagon = /** @class */ (function (_super) {
    __extends(Hexagon, _super);
    function Hexagon() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(Hexagon.prototype, "number_of_points", {
        get: function () {
            return 6;
        },
        enumerable: true,
        configurable: true
    });
    return Hexagon;
}(Polygon));
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Heptagon = /** @class */ (function (_super) {
    __extends(Heptagon, _super);
    function Heptagon() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(Heptagon.prototype, "number_of_points", {
        get: function () {
            return 7;
        },
        enumerable: true,
        configurable: true
    });
    return Heptagon;
}(Polygon));
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Octagon = /** @class */ (function (_super) {
    __extends(Octagon, _super);
    function Octagon() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(Octagon.prototype, "number_of_points", {
        get: function () {
            return 8;
        },
        enumerable: true,
        configurable: true
    });
    return Octagon;
}(Polygon));
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Nonagon = /** @class */ (function (_super) {
    __extends(Nonagon, _super);
    function Nonagon() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(Nonagon.prototype, "number_of_points", {
        get: function () {
            return 9;
        },
        enumerable: true,
        configurable: true
    });
    return Nonagon;
}(Polygon));
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var Decagon = /** @class */ (function (_super) {
    __extends(Decagon, _super);
    function Decagon() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Object.defineProperty(Decagon.prototype, "number_of_points", {
        get: function () {
            return 10;
        },
        enumerable: true,
        configurable: true
    });
    return Decagon;
}(Polygon));
/* eslint-disable-next-line no-unused-vars, no-redeclare */
var PolygonWithSides = {
    3: Triangle,
    4: Square,
    5: Pentagon,
    6: Hexagon,
    7: Heptagon,
    8: Octagon,
    9: Nonagon,
    10: Decagon,
};
