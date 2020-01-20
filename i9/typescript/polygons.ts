// https://codepen.io/Elf/details/rOrRaw
// https://www.d3indepth.com/shapes/

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Polygon {
    constructor(public center:Point, public size:number, public radial_shift:number=0) {}

    get number_of_points():number {
        throw "Not Yet Implemented";
    }

    static onCircle(c:Circle) {
        return new Hexagon(new Point(c.midpoint.x, c.midpoint.y), c.r)
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
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Octagon extends Polygon {
    get number_of_points() {
        return 8;
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
    8: Octagon,
    10: Decagon,
};
