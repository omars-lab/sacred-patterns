#!/usr/bin/env python3
"""Generate pattern-interpretation.html from template + session data.

Usage:
    python3 tools/generate-interpretation.py <session-dir> [--template <path>]

Reads:
    <session>/input/shapes.json       — image_size + shapes array
    <session>/input/pattern-config.json — pattern metadata + zones

Writes:
    <session>/input/pattern-interpretation.html
"""

import argparse
import json
import os
import sys


OVERLAY_COLORS = [
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4',
    '#ffeaa7', '#fd79a8', '#6c5ce7', '#00b894',
    '#e17055', '#0984e3', '#fdcb6e', '#dfe6e9',
]

SHAPE_DEFAULTS = {
    'count_tolerance': 0,
    'area_tolerance': 0.3,
    'visible': True,
    'distance_from_center': None,
}


def find_reference_image(input_dir):
    """Auto-detect reference image extension."""
    for ext in ('jpg', 'jpeg', 'png', 'webp'):
        path = os.path.join(input_dir, f'reference.{ext}')
        if os.path.exists(path):
            return f'reference.{ext}'
    return 'reference.jpg'  # fallback


def prepare_shapes(raw_shapes):
    """Fill default fields on shapes and assign overlay colors."""
    for i, shape in enumerate(raw_shapes):
        for key, default in SHAPE_DEFAULTS.items():
            shape.setdefault(key, default)
        shape.setdefault('approximate_area_ratio', None)
        shape.setdefault('notes', '')
        if 'overlay_color' not in shape:
            shape['overlay_color'] = OVERLAY_COLORS[i % len(OVERLAY_COLORS)]
    return raw_shapes


def main():
    parser = argparse.ArgumentParser(description='Generate pattern-interpretation.html from template')
    parser.add_argument('session_dir', help='Path to session directory (e.g., /path/to/session-1)')
    parser.add_argument('--template', help='Path to template HTML (auto-detected if omitted)')
    args = parser.parse_args()

    session_dir = os.path.abspath(args.session_dir)
    input_dir = os.path.join(session_dir, 'input')

    if not os.path.isdir(input_dir):
        print(f'Error: input directory not found: {input_dir}', file=sys.stderr)
        sys.exit(1)

    # Resolve template path
    if args.template:
        template_path = args.template
    else:
        # Auto-detect: relative to this script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(script_dir)
        template_path = os.path.join(
            repo_root, '.claude', 'skills', 'interpret-pattern',
            'templates', 'pattern-interpretation.html'
        )

    if not os.path.exists(template_path):
        print(f'Error: template not found: {template_path}', file=sys.stderr)
        sys.exit(1)

    # Read shapes.json
    shapes_path = os.path.join(input_dir, 'shapes.json')
    if not os.path.exists(shapes_path):
        print(f'Error: shapes.json not found: {shapes_path}', file=sys.stderr)
        sys.exit(1)

    with open(shapes_path, 'r') as f:
        shapes_data = json.load(f)

    width, height = shapes_data['image_size']
    raw_shapes = shapes_data['shapes']
    shapes = prepare_shapes(raw_shapes)

    # Read pattern-config.json
    config_path = os.path.join(input_dir, 'pattern-config.json')
    if not os.path.exists(config_path):
        print(f'Error: pattern-config.json not found: {config_path}', file=sys.stderr)
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = json.load(f)

    pattern_meta = config['pattern']
    zones = config['zones']
    pattern_name = pattern_meta['name'].replace('-', ' ').title()

    # Auto-detect reference image
    ref_image = find_reference_image(input_dir)

    # Read template
    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    output = template
    output = output.replace('{{PATTERN_NAME}}', pattern_name)
    output = output.replace('{{WIDTH}}', str(width))
    output = output.replace('{{HEIGHT}}', str(height))
    output = output.replace('{{REFERENCE_IMAGE_PATH}}', ref_image)
    output = output.replace('{{PATTERN_META_JSON}}', json.dumps(pattern_meta, indent=6))
    output = output.replace('{{ZONES_JSON}}', json.dumps(zones, indent=6))
    output = output.replace('{{SHAPES_JSON}}', json.dumps(shapes, indent=6))

    # Write output
    output_path = os.path.join(input_dir, 'pattern-interpretation.html')
    with open(output_path, 'w') as f:
        f.write(output)

    print(f'Generated: {output_path}')
    print(f'  Pattern: {pattern_name}')
    print(f'  Image:   {width}x{height} ({ref_image})')
    print(f'  Shapes:  {len(shapes)}')


if __name__ == '__main__':
    main()
