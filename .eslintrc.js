module.exports = {
    "env": {
        "browser": true,
        "es6": true,
        "commonjs": true, // this is to allow the use of require/export ts does ...
        "node": true // this is so no errors are thrown on the node __dirname code ...
    },
    "extends": "eslint:recommended",
    "globals": {
        "_": "readonly",
        "d3": "readonly",
        "Atomics": "readonly",
        "SharedArrayBuffer": "readonly",
        "Point": "readonly",
        "Circle": "readonly",
        "Line": "readonly",
        "Polygon": "readonly",
        "Star": "readonly",
        "Hexagon": "readonly",
        "PolygonWithSides": "readonly",
        "appendCircleWithMidpoint": "readonly",
        "appendLine": "readonly",
        "appendPolygon": "readonly"
    },
    "parserOptions": {
        "ecmaVersion": 6,
        "ecmaFeatures": {
            "experimentalObjectRestSpread": true
        }
    },
    "rules": {
        "no-prototype-builtins": "off"
    }
}
