import * as _ from "lodash";
import {Point} from "./points"

// https://github.com/lodash/lodash/issues/2173
function _rotate_list_right<T>(arr:T[]): T[] {
    const arr_copy = _.concat([], arr);
    const head = arr_copy.shift();
    if (!_.isEmpty(head)) {
        arr_copy.push(<T>head);
    }
    return arr_copy;
}

/**
 * Directed line segment between two `Point`s — answers "what carries
 * a finite straight-line primitive plus the slope/orientation/length
 * helpers every construction routine needs to compose stars, polygons,
 * and chord intersections without re-deriving the inequalities each
 * time?". The segment is *directed* (p1 → p2) because extend-and-scale
 * operations need an anchor point (p1) and a movable endpoint (p2);
 * callers wanting an undirected edge ignore the direction at the
 * point of comparison. Slope is computed lazily (no cache) because
 * the construction path mutates rarely and re-reads are cheap.
 */
export class Line {

    constructor(public p1:Point, public p2:Point) {}

    get dx(): number {
        return this.p2.x - this.p1.x;
    }

    get dy(): number {
        return this.p2.y - this.p1.y;
    }

    slope(): number {
        return this.dy / this.dx;
    }

    get distanceBetweenPoints(): number {
        return Point.distanceBetweenPoints(this.p1, this.p2);
    }

    get length(): number {
        return this.distanceBetweenPoints;
    }

    // get yIntercept(): Point | undefined {
    //     if (this.isHorizontal() && this.p1.y != 0) {
    //         return undefined;
    //     }
    //
    //     // return
    // }

    isHorizontal(): boolean {
        if ( this.p1.y === this.p2.y || Math.abs(this.slope()) < (1.0/1000000.0) ) {
            return true;
        }
        return false;
    }

    isVerticle(): boolean {
        if (this.p1.x === this.p2.x || Math.abs(this.slope()) > 1000000) {
            return true;
        }
        return false;
    }

    replaceEndingPoint(p2:Point): Line {
        return new Line(this.p1, p2);
    }

    extendLineRight(newDistance:number): Line {
        if (this.isHorizontal()) {
            return this.replaceEndingPoint(
                new Point(
                    this.p1.x + newDistance,
                    this.p1.y
                )
            );
        }
        const currentDistance = this.distanceBetweenPoints;
        if (this.slope() > 0) {
            return this.replaceEndingPoint(
                new Point(
                    this.p1.x + ((newDistance*Math.abs(this.dx))/currentDistance),
                    this.p1.y + ((newDistance*Math.abs(this.dy))/currentDistance)
                )
            );
        }
        else {
            return this.replaceEndingPoint(
                new Point(
                    this.p1.x + ((newDistance*Math.abs(this.dx))/currentDistance),
                    this.p1.y - ((newDistance*Math.abs(this.dy))/currentDistance)
                )
            );
        }
    }

    extendLineLeft(newDistance:number): Line {
        if (this.isHorizontal()) {
            return this.replaceEndingPoint(
                new Point(
                    this.p1.x - newDistance,
                    this.p1.y
                )
            );
        }
        const currentDistance = this.distanceBetweenPoints;
        if (this.slope() > 0) {
            return this.replaceEndingPoint(
                new Point(
                    this.p1.x - ((newDistance*Math.abs(this.dx))/currentDistance),
                    this.p1.y - ((newDistance*Math.abs(this.dy))/currentDistance)
                )
            );
        }
        else {
            return this.replaceEndingPoint(
                new Point(
                    this.p1.x - ((newDistance*Math.abs(this.dx))/currentDistance),
                    this.p1.y + ((newDistance*Math.abs(this.dy))/currentDistance)
                )
            );
        }
    }

    extendLine(newDistance:number): Line {
        console.log("Extending line between", this.p1, this.p2);
        // let [x1, y1] = p1;
        // let [x2, y2] = p2;
        if (this.isVerticle()) {
            if (this.p2.isUnder(this.p1)) {
                return this.replaceEndingPoint(
                    new Point(this.p2.x, this.p1.y-newDistance)
                );
            }
            return this.replaceEndingPoint(
                new Point(this.p2.x, this.p1.y+newDistance)
            );
        }
        if (this.p1.isInQuadrant2(this.p2) || this.p1.isInQuadrant3(this.p2)) {
            return this.extendLineLeft(newDistance);
        }
        return this.extendLineRight(newDistance);
    }

    scaleLine(factor:number) : Line {
        return this.extendLine(factor*this.length);
    }

}

/**
 * Static factory namespace for bulk-constructing `Line`s — answers
 * "where does code that takes an ordered list of polygon vertices and
 * needs the closed-polygon edges live, without forcing every call site
 * to write its own `_.zip(points, points.slice(1).concat(points[0]))`
 * boilerplate?". Implemented as a class with static methods (rather than
 * a bare module) so the call site reads `Lines.fromPoints(...)`, which
 * parallels the `Line` primitive name and signals "many lines" by
 * pluralization at the type level.
 */
export class Lines {

    static fromPoints(points:Point[]): Line[] {
        // Form lines by connecting the points ...
        return _.map(
            // https://www.tutorialsteacher.com/typescript/typescript-tuple
            (<[Point, Point][]>_.zip(
                points,
                _rotate_list_right(points)
            )),
            ([p1, p2]) => new Line(p1, p2),
        );
    }

    // static intersection(l1:Line, l2:Line): Point | undefined {}

}
