import * as _ from "lodash";

export interface Function1<A, B> {
    (arg1: A): B;
}


/**
 * Reduce a list to "do all members satisfy the predicate?" — answers "how
 * does construction code express 'every vertex is inside the bounding
 * circle' or 'every line crosses the axis' without inlining a Lodash
 * `every` call with a closure each time?". Defined alongside `any` (its
 * disjunctive sibling) so reads at call sites form a parallel pair
 * (`all(verts, inside)` vs `any(verts, outside)`) rather than the
 * `every`/`some` Lodash naming, which doesn't carry the same logical
 * symmetry for a reader scanning geometry code.
 */
export function all<T>(l:T[], f: Function1<T,boolean>): boolean {
    return _.reduce(
        _.map(l, f),
        (sum:boolean, n: boolean) => sum && n,
        true
    )
}

/**
 * Reduce a list to "does any member satisfy the predicate?" — the
 * disjunctive sibling of `all`. Answers the same "why named instead of
 * Lodash `some`" question: keeps reads at construction call sites
 * symmetric (`all(verts, inside)` vs `any(verts, outside)`) so a reader
 * scanning a geometric guard can pattern-match the logical shape rather
 * than the helper's name.
 */
export function any<T>(l:T[], f: Function1<T,boolean>): boolean {
    return _.reduce(
        _.map(l, f),
        (sum:boolean, n: boolean) => sum || n,
        false
    )
}

/**
 * Parity check exposed as a named function — answers "why have a named
 * helper for `value % 2 === 0` when the inline expression would do?".
 * Because every star/polygon construction that alternates fill colors,
 * tile types, or strapwork-over/under semantics threads parity decisions
 * through map-callbacks (`_map_even_odd`), and a named predicate keeps
 * those callbacks declarative rather than scattering modulus arithmetic
 * across draw routines.
 */
export function isEven(value:number): boolean {
	if (value%2 == 0)
		return true;
	else
		return false;
}


/**
 * Negation of `isEven` — answers the same parity question from the
 * opposite side so call sites can read in either direction
 * (`if (isOdd(i))` vs `if (!isEven(i))`) and the choice carries the
 * geometric intent (odd-indexed tile vs not-even-indexed tile) into the
 * code rather than asking the reader to negate a predicate mentally.
 */
export function isOdd(value:number): boolean {
	return ! isEven(value);
}

/**
 * Map an array with index-parity dispatch — answers "how does strapwork
 * code apply two different transforms (e.g., over-crossing vs
 * under-crossing, satellite-A vs satellite-B colors) to alternating
 * elements without a manual loop with an `if (i % 2)` inside?". Both
 * `even_func` and `odd_func` default to identity so callers can override
 * one side only and keep the other passthrough — common for "decorate
 * every other vertex" patterns. Note: implemented via `takeRightWhile`
 * with an always-true predicate, which is an idiomatic way to use Lodash
 * for a side-effecting traversal with index access; behaviour is a
 * forward-order map despite the `Right` in the helper name.
 */
export function _map_even_odd<T>(array_to_map:T[], even_func:_.ArrayIterator<T, T>=_.identity, odd_func:_.ArrayIterator<T, T>=_.identity): T[] {
    const list:T[] = [];
    _.takeRightWhile(
        array_to_map,
        (value, index:number, array) => {
            list.push(
                isEven(index) ?
                    even_func(value, index, <T[]>array) :
                    odd_func(value, index, <T[]>array)
            );
            return true;
        }
    );
    return list;
}


/**
 * Apply a sequence of A→A transforms left-to-right — answers "how does a
 * construction express 'rotate then scale then translate' (or 'apply
 * level-1 then level-2 then level-3 recursion') as a flat list of steps
 * instead of nested function calls that have to be read inside-out?".
 * Each step receives the output of the previous, mirroring the immutable
 * transform discipline (tenet 10a) used by `Point.rotate()`,
 * `Line.scale()`, etc. — every stage returns a fresh `A` so the original
 * input is never mutated.
 */
export function applyTransformationPipeline<A>(a: A, pipeline:Function1<A, A>[]): A {
	let returnVal = a;
	_.forEach(
		pipeline,
		p => {
			returnVal = p(returnVal);
		}
	);
	return returnVal;
}
