/**
 * Void result alias — answers "how does the codebase signal that a function
 * is called for its side effect (mutating SVG DOM, scheduling a D3 update)
 * rather than for a return value?". Using a named alias instead of bare
 * `void` makes the intent (side-effecting drawing operation) grep-able and
 * lets call-site signatures read as "this returns nothing because it
 * paints" rather than the weaker "this returns nothing because reasons".
 */
export type IO = void;

/**
 * Nullable + undefined wrapper — answers "how does code distinguish 'value
 * possibly not set' from 'value set to null' across optional fields in
 * geometric primitives and rendering metadata?". TypeScript's `?` syntax
 * gives `T | undefined` only; this alias additionally includes `null`
 * because D3 selections and SVG attributes return `null` for missing
 * elements, and the codebase needs one type that covers both shapes when
 * narrowing user input.
 * See https://github.com/microsoft/TypeScript/issues/7426 for why the
 * built-in `T?` does not include `null`.
 */
export type Optional<T> = T | null | undefined;
