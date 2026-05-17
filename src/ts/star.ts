import * as _ from "lodash";
import {Point} from "./points"
import {Circle} from "./circles"
import {Line, Lines} from "./lines"

/**
 * Compass-and-straightedge N-pointed star — answers "how does a construction
 * express an N-pointed star as the zigzag between a central reference circle
 * and N surrounding circles, the way Islamic-geometry pattern books (e.g.,
 * Broug's *Islamic Geometric Patterns*, p. 16) draw it?". The star is
 * parameterized by `numberOfPoints` (N) and `size` (the central radius);
 * `radial_shift` rotates the whole figure so callers can align star tips with
 * existing geometry without re-deriving vertex angles. The construction
 * builds `numberOfPoints` satellite circles around the center, then walks
 * vertices by alternating between satellite-circumference points and
 * central-circumference points — the same alternation that produces the
 * star's convex/concave silhouette in the reference diagrams.
 */
export class Star {

    constructor(public center:Point, public numberOfPoints:number, public size:number, public radial_shift:number=0) {}

    get centralCircle(): Circle {
        return new Circle(this.center.x, this.center.y, this.size);
    }

    get innerCircles(): Circle[] {
        return this.centralCircle.surroundingCircles(this.numberOfPoints, undefined, this.radial_shift);
    }

    get outerCircle(): Circle {
        return new Circle(this.center.x, this.center.y, this.size * 2);
    }

    get circles(): Circle[] {
        return _.concat(
            [this.centralCircle],
            this.innerCircles,
            [this.outerCircle],
        );
    }

    get points(): Point[] {
        const _points = [];
        console.log(this.radial_shift);
        _points.push(this.centralCircle.pointOnCircumferenceAtRadian(0+this.radial_shift));
        _.forEach(
            _.range(0, this.numberOfPoints),
            // 2 * Math.PI, 2 * Math.PI /
            circleIndex => {
                const radian = ((circleIndex + 1) * 2 * Math.PI / this.numberOfPoints) + this.radial_shift;
                _points.push(this.innerCircles[circleIndex].pointOnCircumferenceAtRadian(radian));
                _points.push(this.centralCircle.pointOnCircumferenceAtRadian(radian));
            }
        );
        _points.push(this.centralCircle.pointOnCircumferenceAtRadian(0+this.radial_shift));
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
    }

    get lines(): Line[] {
        return Lines.fromPoints(this.points);
    }

    rotate(radians:number): Star {
        return new Star(
            this.center, this.numberOfPoints, this.size, this.radial_shift + radians,
        );
    }

    adjacent(x=0, y=0): Star {
        return new Star(
            new Point(this.center.x+x, this.center.y+y), this.numberOfPoints, this.size, this.radial_shift,
        );
    }

    above(): Star {
        return this.adjacent(0, (this.size * this.size/1.155));
    }

    below(): Star {
        return this.adjacent(0, -(this.size * this.size/1.155));
    }

    right(): Star {
        return this.adjacent((this.size * this.size/1.155), 0);
    }

    left(): Star {
        return this.adjacent(-(this.size * this.size/1.155), 0);
    }
}

/**
 * Pre-rotated 5-pointed star convenience constructor — answers "why is there
 * a named helper when `new Star(p, 5, s)` would do?". Because a bare 5-star
 * lands one tip on the positive x-axis (radian 0), but every reference
 * pentagram diagram in the catalog draws the star tip-up. The π/2 rotation
 * is folded in here so call sites read as `FivePointStar(p, s)` without
 * sprinkling the same orientation correction across every pentagram
 * construction.
 */
export function FivePointStar(point:Point, size:number): Star {
    const s = (new Star(point, 5, size)).rotate(Math.PI/2);
    return s;
}

/**
 * Per-vertex radial elongation wrapper around a `Star` — answers "how does a
 * construction stretch some star tips farther from the center than others
 * (asymmetric stars, decorative variations) without re-deriving every
 * vertex's angle?". Wraps a finished `Star`, then for each vertex index `i`
 * scales the center→vertex line by `elongationFactors[i]` (defaulting to 1
 * so unmentioned vertices stay put). The factor map is sparse on purpose:
 * callers specify only the vertices they want to push out or pull in, and
 * the rest inherit the underlying star's geometry — keeping the diff
 * between "regular star" and "decorated star" readable at the call site.
 */
export class ElongatedFivePointStar {
    constructor(public star:Star, public elongationFactors: Record<number, number>) {}

    get lines(): Line[] {
        const points = _.map(
            this.star.points,
            (p, i) => (new Line(this.star.center, p)).scaleLine(_.get(this.elongationFactors, i, 1)).p2
        );
        return Lines.fromPoints(points);
    }
}
