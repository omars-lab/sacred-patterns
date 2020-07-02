import * as _ from "lodash";
import {Point} from "./points"
import {Circle} from "./circles"
import {Line, Lines} from "./lines"

/* eslint-disable-next-line no-unused-vars, no-redeclare */
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

export function FivePointStar(point:Point, size:number): Star {
    const s = (new Star(point, 5, size)).rotate(Math.PI/2);
    return s;
}

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
