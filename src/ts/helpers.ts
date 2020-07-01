import * as _ from "lodash";

export interface Function1<A, B> {
    (arg1: A): B;
}

export function isEven(value:number) {
	if (value%2 == 0)
		return true;
	else
		return false;
}


export function _map_even_odd<T>(array_to_map:T[], even_func:_.ArrayIterator<T, T>=_.identity, odd_func:_.ArrayIterator<T, T>=_.identity) {
    let list:T[] = [];
    _.takeRightWhile(
        array_to_map,
        (value, index:number, array) => {
            list.push(isEven(index) ? even_func(value, index, <T[]>array) : odd_func(value, index, <T[]>array) );
            return true;
        }
    );
    return list;
}


export function applyTransformationPipeline<A>(a: A, pipeline:Function1<A, A>[]) {
	let returnVal = a;
	_.forEach(
		pipeline,
		p => {
			returnVal = p(returnVal);
		}
	);
	return returnVal;
}
