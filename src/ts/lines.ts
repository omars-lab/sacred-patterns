// https://github.com/lodash/lodash/issues/2173
function _rotate_list_right(arr:any[]): any[] {
    var arr_copy = _.concat([], arr);
    arr_copy.push(arr_copy.shift())
    return arr_copy;
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
class Line {

    constructor(public p1:Point, public p2:Point) {}

    get dx() {
        return this.p2.x - this.p1.x;
    }

    get dy() {
        return this.p2.y - this.p1.y;
    }

    slope() {
        return this.dy / this.dx;
    }

    // get yIntercept(): Point | undefined {
    //     if (this.isHorizontal() && this.p1.y != 0) {
    //         return undefined;
    //     }
    //
    //     // return
    // }

    isHorizontal() {
        if ( this.p1.y === this.p2.y || Math.abs(this.slope()) < (1.0/1000000.0) ) {
            return true;
        }
        return false;
    }

    isVerticle() {
        if (this.p1.x === this.p2.x || Math.abs(this.slope()) > 1000000) {
            return true;
        }
        return false;
    }

    distanceBetweenPoints() {
        return Point.distanceBetweenPoints(this.p1, this.p2);
    }

    replaceEndingPoint(p2:Point) {
        return new Line(this.p1, p2);
    }

    extendLineRight(newDistance:number) {
        if (this.isHorizontal()) {
            return this.replaceEndingPoint(
                new Point(
                    this.p1.x + newDistance,
                    this.p1.y
                )
            );
        }
        var currentDistance = this.distanceBetweenPoints();
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

    extendLineLeft(newDistance:number) {
        if (this.isHorizontal()) {
            return this.replaceEndingPoint(
                new Point(
                    this.p1.x - newDistance,
                    this.p1.y
                )
            );
        }
        var currentDistance = this.distanceBetweenPoints();
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

    extendLine(newDistance:number) {
        console.log("Extending line between", this.p1, this.p2);
        // var [x1, y1] = p1;
        // var [x2, y2] = p2;
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

}

class Lines {

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
