export type IO = void;
// https://github.com/microsoft/TypeScript/issues/7426
export type Optional<T> = T | null | undefined;

// https://www.typescriptlang.org/docs/handbook/advanced-types.html
// https://www.logicbig.com/tutorials/misc/typescript/ts-config-json.html

// type d3SvgElement<T extends d3.BaseType> = d3.Selection<T, {}, HTMLElement, any> | d3.Selection<T, unknown, HTMLElement, any>;
export type d3SvgElement<T extends d3.BaseType> = d3.Selection<T, unknown, HTMLElement, unknown>;
export type d3SVG = d3SvgElement<SVGSVGElement>;
export type d3SVGDef = d3SvgElement<SVGDefsElement>;
export type d3CIRCLE = d3SvgElement<SVGCircleElement>;
export type d3LINE = d3SvgElement<SVGLineElement>;
export type d3POLYLINE = d3SvgElement<SVGPolylineElement>;
export type d3TEXT = d3SvgElement<SVGTextElement>;

// Introspecting types ...
// let x = d3.select("body");
// let x = d3.select("body").append("line");
// let x = d3.select("body").append("circle");

/* eslint-disable-next-line no-unused-vars, no-redeclare */
export type ValueOf<T> = T[keyof T];