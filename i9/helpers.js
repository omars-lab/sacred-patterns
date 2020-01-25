"use strict";
function isEven(value) {
    if (value % 2 == 0)
        return true;
    else
        return false;
}
function _map_even_odd(array_to_map, even_func, odd_func) {
    if (even_func === void 0) { even_func = _.identity; }
    if (odd_func === void 0) { odd_func = _.identity; }
    var list = [];
    _.takeRightWhile(array_to_map, function (value, index, array) {
        list.push(isEven(index) ? even_func(value, index, array) : odd_func(value, index, array));
        return true;
    });
    return list;
}
function applyTransformationPipeline(a, pipeline) {
    var returnVal = a;
    _.forEach(pipeline, function (p) {
        returnVal = p(returnVal);
    });
    return returnVal;
}
