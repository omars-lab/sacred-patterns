import * as _ from "lodash";
import {Line} from "./lines";
import {Point} from "./points";

export interface CircleMetadata {
    level: number;
    fill?: string;
    stroke?: string;
}

/* eslint-disable-next-line no-unused-vars, no-redeclare */
export class Circle {

    constructor(public x:number, public y:number, public r:number, private _metadata?:CircleMetadata) {}

    get id(): string {
        return `x:${Math.ceil(this.x)}-y:${Math.ceil(this.y)}-r:${this.r}`;
    }

    get metadata(): CircleMetadata | any {
        return _.isEmpty(this._metadata) ? {} : (<CircleMetadata>this._metadata);
    }

    pointsOnCircumference(numberOfPoints:number, shift_in_radians=0): Point[] {
        return _.map(
            <number[]>(_.range(0, 2 * Math.PI, 2 * Math.PI / numberOfPoints)),
            radians => this.pointOnCircumferenceAtRadian(radians + shift_in_radians)
        );
    }

    pointOnCircumferenceAtRadian(radian:number): Point {
        return new Point(
            this.x + (Math.cos(radian) * this.r),
            this.y + (Math.sin(radian) * this.r),
        )
    }

    pointOnCircumferenceAtDegree(degree:number): Point {
        return this.pointOnCircumferenceAtRadian((degree/360.0)*2*Math.PI);
    }
    // circlesAround
    // https://stackoverflow.com/questions/17186566/how-do-i-fix-error-ts1015-parameter-cannot-have-question-mark-and-initializer
    surroundingCircles(count:number, distance_modifier=1, shift_in_radians=0, metadata:CircleMetadata|undefined=undefined): Circle[] {
        const {x, y, r} = this;
        let circles = _.map(
            _.range(0, 2 * Math.PI, 2 * Math.PI / count),
            radians => new Circle(
                x + (Math.cos(radians + shift_in_radians) * r * distance_modifier),
                y + (Math.sin(radians + shift_in_radians) * r * distance_modifier),
                r,
                _.isEmpty(metadata) ? undefined : _.merge({}, metadata),
            )
        );
        return circles;
    }

    // flowersAround
    surroundWithFlower(metadata?:CircleMetadata): Circle[] {
        return this.surroundingCircles(6, 1, 0, metadata);
    }

    static indexCircles(circles:Circle[]): Record<string, Circle> {
        return _.fromPairs(_.map(
            circles,
            (c) => [c.id, c],
        ));
    }
    // appendFlowersRecursively
    _surroundWithFlowersRecursively(recursionLevel:number): Record<string, Circle> {
        // Returns Circles that will get drawn ...
        let circlesToDraw = {};
        let aroundCenter = Circle.indexCircles(
            this.surroundWithFlower({level: recursionLevel})
        );
        console.log("around center", aroundCenter);
        circlesToDraw = _.merge({}, aroundCenter);
        if (recursionLevel > 1) {
            let recursiveCircles =  _.flatMap(
                this.surroundWithFlower({level: recursionLevel - 1}),
                (c) => c._surroundWithFlowersRecursively(recursionLevel - 1)
            );
            console.log("recursiveCircles", recursiveCircles);
            circlesToDraw = _.mergeWith({}, circlesToDraw, ...recursiveCircles, Circle.pickHigherLevel);
        }
        // console.log("circlesToDraw", circlesToDraw);
        return circlesToDraw;
    }

    surroundWithFlowersRecursively(recursionLevel:number): Circle[] {
        return _.values(this._surroundWithFlowersRecursively(recursionLevel));
    }

    get midpoint(): Point {
        return new Point(this.x, this.y);
    }

    static lineBetweenMidpoints(c1:Circle, c2:Circle): Line {
        return new Line(c1.midpoint, c2.midpoint);
    }

    static pickHigherLevel(ca?: Circle, cb?: Circle): Circle | undefined {
        if (_.isUndefined(ca) || _.isUndefined(cb)) {
            return undefined;
        }

        // https://dzone.com/articles/using-casting-typescript
        if ((<CircleMetadata>ca.metadata).level >= (<CircleMetadata>cb.metadata).level) {
            // console.log('picked ca over cb', ca, cb);
            return ca;
        }
        // console.log('picked cb over ca', ca, cb);
        return cb;
    }

    adjacent(x_shift:number=0, y_shift:number=0, r_scaler:number=1, metadata:CircleMetadata=this.metadata): Circle {
        console.log(this);
        return new Circle(
            this.x+x_shift, this.y+y_shift, this.r * r_scaler, metadata
        );
    }

}


// Intersection of Circles ...
// http://jsfiddle.net/g0r9n090/
// https://stackoverflow.com/questions/33330074/d3-js-detect-intersection-area
