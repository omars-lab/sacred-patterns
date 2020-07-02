/* eslint-disable-next-line no-unused-vars, no-redeclare */
export class Point {

    constructor(public x:number, public y:number) {}

    static distanceBetweenPoints(p1:Point, p2:Point): number {
        const [x1, y1] = [p1.x, p1.y];
        const [x2, y2] = [p2.x, p2.y];
        // https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
        return Math.hypot(x2-x1, y2-y1);
    }

    isUnder(p2:Point): boolean {
        return this.y < p2.y;
    }

    isInQuadrant1(p2:Point): boolean {
        // Assuming the current point is at (0,0), is the supplied point north east of it
        const [x1, y1] = [this.x, this.y];
        const [x2, y2] = [p2.x, p2.y];
        return (x2 >= x1) && (y2 >= y1);
    }

    isInQuadrant2(p2:Point): boolean {
        // Assuming the current point is at (0,0), is the supplied point north west of it
        const [x1, y1] = [this.x, this.y];
        const [x2, y2] = [p2.x, p2.y];
        return (x2 <= x1) && (y2 >= y1);
    }

    isInQuadrant3(p2:Point): boolean {
        // Assuming the current point is at (0,0), is the supplied point south west of it
        const [x1, y1] = [this.x, this.y];
        const [x2, y2] = [p2.x, p2.y];
        return (x2 <= x1) && (y2 <= y1);
    }

    isInQuadrant4(p2:Point): boolean {
        // Assuming the current point is at (0,0), is the supplied point south east of it
        const [x1, y1] = [this.x, this.y];
        const [x2, y2] = [p2.x, p2.y];
        return (x2 >= x1) && (y2 <= y1);
    }
}
