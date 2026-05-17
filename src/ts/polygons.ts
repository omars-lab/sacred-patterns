import {Point} from "./points"
import {Circle} from "./circles"
import {Line, Lines} from "./lines"

// https://codepen.io/Elf/details/rOrRaw
// https://www.d3indepth.com/shapes/

/**
 * Abstract regular-N-gon base — answers "what carries the shared
 * inscribed-in-a-circle construction (center, size, radial-shift) for
 * every regular polygon, so per-N subclasses (`Triangle`, `Square`,
 * `Pentagon`, ...) only override `number_of_points` and inherit the
 * `points` / `lines` / `outerCircle` derivations?". The construction
 * convention: every regular polygon is inscribed in an `outerCircle`
 * of radius `size`, vertices sampled at `2π/n` intervals starting at
 * angle `radial_shift`. Subclasses are tagged-union-style (no extra
 * fields, only `number_of_points` differs) rather than dispatch
 * tables so call sites read as `new Pentagon(...)` rather than
 * `new Polygon(5, ...)` — the type-name *is* the documentation.
 */
export class Polygon {
    constructor(public center:Point, public size:number, public radial_shift:number=0) {}

    get number_of_points(): number {
        throw "Not Yet Implemented";
    }

    static withinCircle<T extends Polygon>(c:Circle): T {
        // Does this work in a static and non static setting?
        // No ... 'this' in a static method ... is the type of the class itself ...
        return <T>(new this(c.midpoint, c.r));
    }

    get outerCircle(): Circle {
        return new Circle(this.center.x, this.center.y, this.size);
    }

    get points(): Point[] {
        const points_of_hexagon = this.outerCircle.pointsOnCircumference(this.number_of_points, this.radial_shift);
        return points_of_hexagon;
    }

    get lines(): Line[] {
        return Lines.fromPoints(this.points);
    }

    rotate(increment_radial_shift:number): this {
        // Make this return a new Polygon polymorphically ...
        this.radial_shift = this.radial_shift + increment_radial_shift;
        return this;
    }

}

/**
 * Chord length between two radian-positions on a circle — answers
 * "given two points on a circle of radius r at angles rad1 and rad2,
 * what's the straight-line distance between them?". Needed because
 * polygon-to-polygon adjacency math (hexagon tiling, packing offsets)
 * is expressed as 'shift by one chord-length in the right direction.'
 * Order-independent: `max - min` collapses to the absolute angular
 * gap so callers don't have to pre-sort the inputs. See:
 * https://byjus.com/maths/chord-of-circle/.
 */
export function determine_chord_length(r: number, rad1: number, rad2: number): number {
    return 2 * r * Math.sin((Math.max(rad1, rad2) - Math.min(rad1, rad2))/2);
}

/**
 * Sagitta (arc-to-chord vertical distance) between two radian-positions
 * — answers "how deep is the arc bulge from a chord on a circle of
 * radius r?". Used wherever construction needs to offset a polygon by
 * the *vertical* gap between two parallel rows (hexagon tiling: row
 * spacing = chord-length minus sagitta), not the chord itself. See:
 * https://www.mathopenref.com/sagitta.html.
 */
export function determine_sagitta_length(r: number, rad1: number, rad2: number): number {
    // https://www.mathopenref.com/sagitta.html
    const l = determine_chord_length(r, rad1, rad2) / 2;
    return r - Math.sqrt(Math.pow(r, 2)-Math.pow(l, 2))
}

/** Regular 3-gon — `Polygon` subclass that fixes `number_of_points` to 3. */
export class Triangle extends Polygon {
    get number_of_points(): number {
        return 3;
    }
}

/** Regular 4-gon — `Polygon` subclass that fixes `number_of_points` to 4. */
export class Square extends Polygon {
    get number_of_points(): number {
        return 4;
    }
}

/** Regular 5-gon — `Polygon` subclass that fixes `number_of_points` to 5. */
export class Pentagon extends Polygon {
    get number_of_points(): number {
        return 5;
    }
}


/**
 * Regular 6-gon with hex-grid adjacency helpers — answers "why does
 * `Hexagon` carry per-direction neighbor constructors (`above`,
 * `below`, `northEast`, ...) when other polygons don't?". Because
 * hexagons tile the plane in a six-around-one grid that's a
 * load-bearing construction primitive (flower-of-life, six-petal
 * rosettes, honeycomb backgrounds), so the directional offsets are
 * compiled in once here rather than re-derived at every call site.
 * The magic constants (1.729, 2.15) are sagitta-and-chord values
 * pre-computed for radius 1 — the inline comments link to the
 * trigonometric derivations that produced them.
 */
export class Hexagon extends Polygon {

    get number_of_points(): number {
        return 6;
    }

    // Figure out why these numbers are right ... and not sin / cos based ...
    above(): Hexagon {
        const refCircle = this.outerCircle;
        // const circleAbove = refCircle.adjacent(0, -1 * determine_sagitta_length(refCircle.r, 2 * Math.PI * 4 / 6, 2 * Math.PI * 5 / 6));
        const circleAbove = refCircle.adjacent(0, -(refCircle.r * 1.729));
        return (<typeof Hexagon>this.constructor).withinCircle(circleAbove);
    }

    below(): Hexagon {
        const refCircle = this.outerCircle;
        // const circleBelow = refCircle.adjacent(0, determine_sagitta_length(refCircle.r, 2 * Math.PI * 4 / 6, 2 * Math.PI * 5 / 6));
        const circleBelow = refCircle.adjacent(0, (refCircle.r * 1.729));
        return (<typeof Hexagon>this.constructor).withinCircle(circleBelow);
    }

    right(): Hexagon {
        const refCircle = this.outerCircle;
        const circleRight = refCircle.adjacent(-(refCircle.r * 2.15), 0);
        return (<typeof Hexagon>this.constructor).withinCircle(circleRight);
    }

    left(): Hexagon {
        const refCircle = this.outerCircle;
        const circleLeft = refCircle.adjacent((refCircle.r * 2.15), 0);
        return (<typeof Hexagon>this.constructor).withinCircle(circleLeft);
    }

    southWest(): Hexagon {
        // https://riptutorial.com/d3-js/example/8402/coordinate-system
        // in s3 ... 0,0 is top left of screen ... not top right ...
        const refCircle = this.outerCircle;
        const newCricle = refCircle.adjacent(
            ((refCircle.r * Math.cos(2*Math.PI*(4/6))) + (refCircle.r * Math.cos(Math.PI))),
            -1 * ((refCircle.r * Math.sin(2*Math.PI*(4/6))) + (refCircle.r * Math.sin(Math.PI)))
        );
        return (<typeof Hexagon>this.constructor).withinCircle(newCricle);
    }

    northWest(): Hexagon {
        // https://riptutorial.com/d3-js/example/8402/coordinate-system
        // in s3 ... 0,0 is top left of screen ... not top right ...
        const refCircle = this.outerCircle;
        const newCricle = refCircle.adjacent(
            ((refCircle.r * Math.cos(2*Math.PI*(2/6))) + (refCircle.r * Math.cos(Math.PI))),
            -1 * ((refCircle.r * Math.sin(2*Math.PI*(2/6))) + (refCircle.r * Math.sin(Math.PI)))
        );
        return (<typeof Hexagon>this.constructor).withinCircle(newCricle);
    }

    northEast(): Hexagon {
        const refCircle = this.outerCircle;
        const newCricle = refCircle.adjacent(
            ((refCircle.r * Math.cos(2*Math.PI*(1/6))) + (refCircle.r * Math.cos(0))),
            -1 * ((refCircle.r * Math.sin(2*Math.PI*(1/6))) + (refCircle.r * Math.sin(0)))
        );
        return (<typeof Hexagon>this.constructor).withinCircle(newCricle);
    }

    southEast(): Hexagon {
        const refCircle = this.outerCircle;
        const newCricle = refCircle.adjacent(
            ((refCircle.r * Math.cos(2*Math.PI*(5/6))) + (refCircle.r * Math.cos(0))),
            -1 * ((refCircle.r * Math.sin(2*Math.PI*(5/6))) + (refCircle.r * Math.sin(0)))
        );
        return (<typeof Hexagon>this.constructor).withinCircle(newCricle);
    }
}

/** Regular 7-gon — `Polygon` subclass that fixes `number_of_points` to 7. */
export class Heptagon extends Polygon {
    get number_of_points(): number {
        return 7;
    }
}

/** Regular 8-gon — `Polygon` subclass that fixes `number_of_points` to 8. */
export class Octagon extends Polygon {
    get number_of_points(): number {
        return 8;
    }
}

/** Regular 9-gon — `Polygon` subclass that fixes `number_of_points` to 9. */
export class Nonagon extends Polygon {
    get number_of_points(): number {
        return 9;
    }
}

/** Regular 10-gon — `Polygon` subclass that fixes `number_of_points` to 10. */
export class Decagon extends Polygon {
    get number_of_points(): number {
        return 10;
    }
}

/**
 * Sides-to-class dispatch table — answers "how does code that picks a
 * polygon class by numeric N (e.g., 'draw a regular k-gon at this
 * radius for variable k') look up the right constructor without a
 * switch?". The map is keyed by `number_of_points` rather than by
 * shape-name string because callers typically have N from a loop
 * variable or config field, and string-keying would require a
 * round-trip through a name table.
 */
export const PolygonWithSides = {
    3: Triangle,
    4: Square,
    5: Pentagon,
    6: Hexagon,
    7: Heptagon,
    8: Octagon,
    9: Nonagon,
    10: Decagon,
};
