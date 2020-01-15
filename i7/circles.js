function pickHigherLevel(ca, cb) {
    if (_.isEmpty(ca) || _.isEmpty(cb)) {
        return undefined;
    }
    if (ca.metadata.level >= cb.metadata.level) {
        // console.log('picked ca over cb', ca, cb);
        return ca;
    }
    // console.log('picked cb over ca', ca, cb);
    return cb;
}

const Circle = class {
    constructor(x, y, r, metadata) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.metadata = _.isEmpty(metadata) ? {} : metadata;
    }

    get id() {
        return `x:${Math.ceil(this.x)}-y:${Math.ceil(this.y)}-r:${this.r}`;
    }

    // circlesAround
    surroundingCircles(count, distance_modifier=1, shift_in_radians=0, metadata={}) {
        const {x, y, r} = this;
        var circles = _.map(
            _.range(0, 2 * Math.PI, 2 * Math.PI / count),
            radians => new Circle(
                x + (Math.cos(radians + shift_in_radians) * r * distance_modifier),
                y + (Math.sin(radians + shift_in_radians) * r * distance_modifier),
                r,
                _.merge(
                    {},
                    this.metadata,
                    _.isEmpty(metadata) ? {} : metadata,
                ),
            )
        );
        return circles;
    }

    // flowersAround
    surroundWithFlower(metadata) {
        return this.surroundingCircles(6, 1, 0, metadata);
    }

    static indexCircles(circles) {
        return _.fromPairs(_.map(
            circles,
            (c) => [c.id, c],
        ));
    }
    // appendFlowersRecursively
    _surroundWithFlowersRecursively(recursionLevel) {
        const {x, y, r} = this;
        // Returns Circles that will get drawn ...
        var circlesToDraw = {};
        var aroundCenter = Circle.indexCircles(
            this.surroundWithFlower({level: recursionLevel})
        );
        console.log("around center", aroundCenter);
        circlesToDraw = _.merge({}, aroundCenter);
        if (recursionLevel > 0) {
            var recursiveCircles =  Circle.indexCircles(
                _.flatMap(
                    this.surroundWithFlower({level: recursionLevel - 1}),
                    (c) => _.values(c._surroundWithFlowersRecursively(recursionLevel - 1))
                )
            );
            console.log("recursiveCircles", recursiveCircles);
            circlesToDraw = _.mergeWith({}, circlesToDraw, recursiveCircles, pickHigherLevel);
        }
        // console.log("circlesToDraw", circlesToDraw);
        return circlesToDraw;
    }

    surroundWithFlowersRecursively(recursionLevel) {
        return _.values(this._surroundWithFlowersRecursively(recursionLevel));
    }

    get midpoint() {
        return new Point(this.x, this.y);
    }

    static lineBetweenMidpoints(c1, c2) {
        return new Line(c1.midpoint, c2.midpoint);
    }
};
