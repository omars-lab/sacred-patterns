// https://codepen.io/Elf/details/rOrRaw
// https://www.d3indepth.com/shapes/

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Polygon {
    constructor(public center:Point, public size:number, public radial_shift:number=0) {}

    get number_of_points(): number {
        throw "Not Yet Implemented";
    }

    static withinCircle<T extends Polygon>(c:Circle): T {
        // Does this work in a static and non static setting?
        // No ... 'this' in a static method ... is the type of the class itself ...
        return <T>(new this(c.midpoint, c.r));
    }

    get outerCircle() {
        return new Circle(this.center.x, this.center.y, this.size);
    }

    get points() {
        var points_of_hexagon = this.outerCircle.pointsOnCircumference(this.number_of_points, this.radial_shift);
        return points_of_hexagon;
    }

    get lines() {
        return Line.fromPoints(this.points);
    }

    rotate(increment_radial_shift:number) {
        // Make this return a new Polygon polymorphically ...
        this.radial_shift = this.radial_shift + increment_radial_shift;
        return this;
    }

}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Triangle extends Polygon {
    get number_of_points() {
        return 3;
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Square extends Polygon {
    get number_of_points() {
        return 4;
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Pentagon extends Polygon {
    get number_of_points() {
        return 5;
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Hexagon extends Polygon {

    get number_of_points() {
        return 6;
    }

    // Figure out why these numbers are right ... and not sin / cos based ...
    above(): Hexagon {
        var refCircle = this.outerCircle;
        var circleAbove = refCircle.adjacent(0, -(refCircle.r * 1.725));
        return (<typeof Hexagon>this.constructor).withinCircle(circleAbove);
    }

    below(): Hexagon {
        var refCircle = this.outerCircle;
        var circleBelow = refCircle.adjacent(0, (refCircle.r * 1.725));
        return (<typeof Hexagon>this.constructor).withinCircle(circleBelow);
    }

    right(): Hexagon {
        var refCircle = this.outerCircle;
        var circleRight = refCircle.adjacent(-(refCircle.r * 2.15), 0);
        return (<typeof Hexagon>this.constructor).withinCircle(circleRight);
    }

    left(): Hexagon {
        var refCircle = this.outerCircle;
        var circleLeft = refCircle.adjacent((refCircle.r * 2.15), 0);
        return (<typeof Hexagon>this.constructor).withinCircle(circleLeft);
    }

    southWest(): Hexagon {
        // https://riptutorial.com/d3-js/example/8402/coordinate-system
        // in s3 ... 0,0 is top left of screen ... not top right ...
        var refCircle = this.outerCircle;
        var newCricle = refCircle.adjacent(
            ((refCircle.r * Math.cos(2*Math.PI*(4/6))) + (refCircle.r * Math.cos(Math.PI))),
            -1 * ((refCircle.r * Math.sin(2*Math.PI*(4/6))) + (refCircle.r * Math.sin(Math.PI)))
        );
        return (<typeof Hexagon>this.constructor).withinCircle(newCricle);
    }

    northWest(): Hexagon {
        // https://riptutorial.com/d3-js/example/8402/coordinate-system
        // in s3 ... 0,0 is top left of screen ... not top right ...
        var refCircle = this.outerCircle;
        var newCricle = refCircle.adjacent(
            ((refCircle.r * Math.cos(2*Math.PI*(2/6))) + (refCircle.r * Math.cos(Math.PI))),
            -1 * ((refCircle.r * Math.sin(2*Math.PI*(2/6))) + (refCircle.r * Math.sin(Math.PI)))
        );
        return (<typeof Hexagon>this.constructor).withinCircle(newCricle);
    }

    northEast(): Hexagon {
        var refCircle = this.outerCircle;
        var newCricle = refCircle.adjacent(
            ((refCircle.r * Math.cos(2*Math.PI*(1/6))) + (refCircle.r * Math.cos(0))),
            -1 * ((refCircle.r * Math.sin(2*Math.PI*(1/6))) + (refCircle.r * Math.sin(0)))
        );
        return (<typeof Hexagon>this.constructor).withinCircle(newCricle);
    }

    southEast(): Hexagon {
        var refCircle = this.outerCircle;
        var newCricle = refCircle.adjacent(
            ((refCircle.r * Math.cos(2*Math.PI*(5/6))) + (refCircle.r * Math.cos(0))),
            -1 * ((refCircle.r * Math.sin(2*Math.PI*(5/6))) + (refCircle.r * Math.sin(0)))
        );
        return (<typeof Hexagon>this.constructor).withinCircle(newCricle);
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Heptagon extends Polygon {
    get number_of_points() {
        return 7;
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Octagon extends Polygon {
    get number_of_points() {
        return 8;
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Nonagon extends Polygon {
    get number_of_points() {
        return 9;
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Decagon extends Polygon {
    get number_of_points() {
        return 10;
    }
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
const PolygonWithSides = {
    3: Triangle,
    4: Square,
    5: Pentagon,
    6: Hexagon,
    7: Heptagon,
    8: Octagon,
    9: Nonagon,
    10: Decagon,
};
