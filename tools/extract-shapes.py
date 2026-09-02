#!/usr/bin/env python3
"""
extract-shapes.py — Image-based shape extraction for pattern interpretation.

Analyzes a reference image and outputs detected tile boundaries as JSON,
plus edge and strapwork overlay PNGs. Uses only Pillow + NumPy (no OpenCV/SciPy).

Usage:
    python3 tools/extract-shapes.py <reference-image> \
        [--output shapes.json] [--tolerance 60] [--min-area 200] \
        [--simplify 3.0] [--colors 8] [--edge-threshold 30] \
        [--work-size 600] [--connectivity 8] \
        [--luminance-threshold 240] [--edge-dilation 0] \
        [--snap-radius 5] [--mode auto] [--morph-close 1] \
        [--segmentation auto]
"""

import argparse
import json
import math
import os
import sys
from collections import deque

import numpy as np
from PIL import Image


# ──────────────────────────────────────────────────────────────
# Perceptual Color Distance
# ──────────────────────────────────────────────────────────────

def perceptual_color_distance(c1, c2):
    """Weighted Euclidean color distance (green-weighted, more perceptually uniform).

    Uses weights: R=2, G=4, B=3 based on human color sensitivity.
    Returns scalar distance.
    """
    dr = float(c1[0]) - float(c2[0])
    dg = float(c1[1]) - float(c2[1])
    db = float(c1[2]) - float(c2[2])
    return math.sqrt(2.0 * dr * dr + 4.0 * dg * dg + 3.0 * db * db)


def perceptual_color_distance_array(pixels, target_color):
    """Vectorized perceptual color distance for an entire pixel array.

    pixels: (H, W, 3) uint8 array
    target_color: (R, G, B) tuple
    Returns: (H, W) float64 distance array
    """
    target = np.array(target_color, dtype=np.float64)
    diff = pixels.astype(np.float64) - target
    # Weights: R=2, G=4, B=3
    weighted_sq = 2.0 * diff[:, :, 0] ** 2 + 4.0 * diff[:, :, 1] ** 2 + 3.0 * diff[:, :, 2] ** 2
    return np.sqrt(weighted_sq)


# ──────────────────────────────────────────────────────────────
# Edge Detection (Sobel via NumPy)
# ──────────────────────────────────────────────────────────────

def sobel_edge_detect(gray: np.ndarray, threshold: float = 30) -> np.ndarray:
    """Compute Sobel edge magnitude on a grayscale image.

    Returns a binary edge mask (uint8, 0 or 255).
    """
    # Gaussian-like blur first (simple 3x3 average for noise reduction)
    kernel = np.ones((3, 3), dtype=np.float64) / 9.0
    blurred = convolve2d(gray.astype(np.float64), kernel)

    # Sobel kernels
    Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    Ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)

    Gx = convolve2d(blurred, Kx)
    Gy = convolve2d(blurred, Ky)

    magnitude = np.sqrt(Gx ** 2 + Gy ** 2)
    # Normalize to 0-255
    mag_max = magnitude.max()
    if mag_max > 0:
        magnitude = magnitude / mag_max * 255.0

    edge_mask = (magnitude > threshold).astype(np.uint8) * 255
    return edge_mask


def convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Simple 2D convolution (valid padding, then pad back to original size)."""
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    h, w = image.shape

    # Pad image
    padded = np.pad(image, ((ph, ph), (pw, pw)), mode='edge')
    result = np.zeros_like(image, dtype=np.float64)

    for i in range(kh):
        for j in range(kw):
            result += padded[i:i + h, j:j + w] * kernel[i, j]

    return result


# ──────────────────────────────────────────────────────────────
# Color Quantization
# ──────────────────────────────────────────────────────────────

def quantize_colors(image: Image.Image, n_colors: int = 8,
                     merge_threshold: float = 30, work_size: int = 600) -> list:
    """Extract dominant colors using Pillow's quantize.

    Returns de-duplicated list of (R, G, B) tuples. Colors within
    merge_threshold perceptual distance are merged (keeps the first).
    """
    small = image.copy()
    small.thumbnail((work_size, work_size), Image.Resampling.LANCZOS)
    # Request more colors than needed to account for merging
    raw_n = min(n_colors * 3, 24)
    quantized = small.quantize(colors=raw_n, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    raw_colors = []
    for i in range(raw_n):
        r, g, b = palette[i * 3], palette[i * 3 + 1], palette[i * 3 + 2]
        raw_colors.append((r, g, b))

    # De-duplicate: merge colors within merge_threshold (perceptual distance)
    unique = []
    for color in raw_colors:
        is_dup = False
        for existing in unique:
            if perceptual_color_distance(color, existing) < merge_threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(color)

    return unique[:n_colors]


def color_mask(pixels: np.ndarray, target_color: tuple, tolerance: float) -> np.ndarray:
    """Create binary mask of pixels within tolerance of target_color (perceptual distance)."""
    diff = perceptual_color_distance_array(pixels, target_color)
    return (diff <= tolerance).astype(np.uint8)


# ──────────────────────────────────────────────────────────────
# Morphological Operations
# ──────────────────────────────────────────────────────────────

def dilate_mask(mask: np.ndarray, radius: int) -> np.ndarray:
    """Morphological dilation via shifted-array OR (pure NumPy).

    mask: 2D uint8 array (0 or 1/255)
    radius: dilation radius in pixels
    Returns dilated mask (same dtype as input).
    """
    binary = (mask > 0)
    result = binary.copy()
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            if dr * dr + dc * dc <= radius * radius:
                shifted = np.roll(np.roll(binary, dr, axis=0), dc, axis=1)
                result = result | shifted
    return result.astype(mask.dtype) * (255 if mask.max() > 1 else 1)


def erode_mask(mask: np.ndarray, radius: int) -> np.ndarray:
    """Morphological erosion via complement dilation (pure NumPy).

    Erosion shrinks foreground regions by `radius` pixels.
    Equivalent to: erode(A) = complement(dilate(complement(A)))
    """
    max_val = 255 if mask.max() > 1 else 1
    complement = ((mask == 0).astype(mask.dtype)) * max_val
    dilated_complement = dilate_mask(complement, radius)
    return ((dilated_complement == 0).astype(mask.dtype)) * max_val


def morphological_close(mask: np.ndarray, radius: int) -> np.ndarray:
    """Morphological closing: dilate then erode.

    Seals small gaps in the mask without expanding the overall boundary.
    Useful for closing 1-2px breaks in strapwork without eating into tile interiors.
    """
    if radius <= 0:
        return mask
    dilated = dilate_mask(mask, radius)
    return erode_mask(dilated, radius)


# ──────────────────────────────────────────────────────────────
# Image Classification
# ──────────────────────────────────────────────────────────────

def classify_image_type(pixels: np.ndarray) -> str:
    """Classify image type based on luminance distribution.

    Analyzes the luminance histogram to detect bimodal images with
    distinct white strapwork and colored tiles.

    Returns: 'white-strapwork' or 'general'
    """
    luminance = (0.299 * pixels[:, :, 0].astype(np.float64) +
                 0.587 * pixels[:, :, 1].astype(np.float64) +
                 0.114 * pixels[:, :, 2].astype(np.float64))

    total = luminance.size
    white_frac = np.sum(luminance > 245) / total
    colored_frac = np.sum(luminance < 200) / total
    transition_frac = 1.0 - white_frac - colored_frac

    print(f"  Image classification: white={white_frac:.1%}, "
          f"colored={colored_frac:.1%}, transition={transition_frac:.1%}")

    if white_frac > 0.3 and colored_frac > 0.2 and transition_frac < 0.15:
        return 'white-strapwork'
    return 'general'


# ──────────────────────────────────────────────────────────────
# Barrier Detection (replaces strapwork-only detection)
# ──────────────────────────────────────────────────────────────

def detect_barrier_mask(pixels: np.ndarray, edge_mask: np.ndarray,
                        mode: str = 'general',
                        luminance_threshold: int = 240,
                        edge_dilation: int = 0,
                        morph_close: int = 1) -> np.ndarray:
    """Detect barrier mask that separates tiles, adapting strategy to image type.

    Two modes:
    - 'white-strapwork': luminance-only barrier (>threshold), no edge union,
      no dilation. Morphological close seals tiny gaps. Drops barrier from ~85%
      to ~59% on bimodal images.
    - 'general': original behavior — luminance OR dilated edges.

    pixels: (H, W, 3) uint8 RGB array
    edge_mask: (H, W) uint8 edge mask (0 or 255)
    mode: 'white-strapwork' or 'general'
    luminance_threshold: brightness cutoff (0-255)
    edge_dilation: radius to dilate edge mask (only used in 'general' mode)
    morph_close: morphological closing radius to seal small gaps

    Returns: (H, W) uint8 barrier mask (0 or 1)
    """
    # Luminance: Y = 0.299R + 0.587G + 0.114B
    luminance = (0.299 * pixels[:, :, 0].astype(np.float64) +
                 0.587 * pixels[:, :, 1].astype(np.float64) +
                 0.114 * pixels[:, :, 2].astype(np.float64))
    bright_mask = (luminance > luminance_threshold).astype(np.uint8)

    if mode == 'white-strapwork':
        # Pure luminance barrier — no edge union, no dilation
        barrier = bright_mask
        # Seal tiny gaps in strapwork without expanding into tiles
        barrier = morphological_close(barrier, morph_close)
    else:
        # General mode: union of bright pixels and dilated edges
        edge_binary = (edge_mask > 0).astype(np.uint8)
        if edge_dilation > 0:
            dilated_edges = dilate_mask(edge_binary, edge_dilation)
        else:
            dilated_edges = edge_binary
        barrier = ((bright_mask > 0) | (dilated_edges > 0)).astype(np.uint8)
        if morph_close > 0:
            barrier = morphological_close(barrier, morph_close)

    return barrier


# ──────────────────────────────────────────────────────────────
# Connected Components (BFS flood-fill)
# ──────────────────────────────────────────────────────────────

NEIGHBORS_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
NEIGHBORS_8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def find_connected_components(mask: np.ndarray, min_area: int = 200,
                              connectivity: int = 8) -> list:
    """Find connected components in a binary mask using iterative BFS.

    connectivity: 4 or 8 (default 8)
    Returns list of lists of (row, col) tuples, filtered by min_area.
    """
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    components = []
    neighbors = NEIGHBORS_8 if connectivity == 8 else NEIGHBORS_4

    for r in range(h):
        for c in range(w):
            if mask[r, c] == 1 and not visited[r, c]:
                # BFS
                component = []
                queue = deque([(r, c)])
                visited[r, c] = True
                while queue:
                    cr, cc = queue.popleft()
                    component.append((cr, cc))
                    for dr, dc in neighbors:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w and not visited[nr, nc] and mask[nr, nc] == 1:
                            visited[nr, nc] = True
                            queue.append((nr, nc))

                if len(component) >= min_area:
                    components.append(component)

    return components


# ──────────────────────────────────────────────────────────────
# Connected Component Labeling (Two-Pass with Union-Find)
# ──────────────────────────────────────────────────────────────

def connected_component_label(mask: np.ndarray, connectivity: int = 4) -> np.ndarray:
    """Label connected components in a binary mask using two-pass algorithm with Union-Find.

    Unlike BFS flood fill, this uses a two-pass scan with equivalence resolution.
    Two tiles of identical color separated by a 1px barrier get different labels
    because CCL only cares about connectivity, not color.

    mask: (H, W) uint8 array where 1 = foreground, 0 = background
    connectivity: 4 (default) or 8
    Returns: (H, W) int32 array where each connected region has a unique positive integer label.
             Background pixels have label 0.
    """
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    next_label = 1

    # Union-Find data structure (dict-based)
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            # Keep smaller label as root
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    # Neighbor offsets for checking already-visited pixels (above and left)
    if connectivity == 4:
        check_offsets = [(-1, 0), (0, -1)]  # up, left
    else:
        check_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1)]  # up-left, up, up-right, left

    # Pass 1: assign provisional labels and record equivalences
    for r in range(h):
        for c in range(w):
            if mask[r, c] == 0:
                continue

            neighbor_labels = []
            for dr, dc in check_offsets:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and labels[nr, nc] > 0:
                    neighbor_labels.append(labels[nr, nc])

            if not neighbor_labels:
                # New label
                labels[r, c] = next_label
                parent[next_label] = next_label
                next_label += 1
            else:
                min_label = min(neighbor_labels)
                labels[r, c] = min_label
                # Union all neighbor labels
                for lbl in neighbor_labels:
                    if lbl != min_label:
                        union(min_label, lbl)

    # Pass 2: resolve all labels to canonical roots
    for r in range(h):
        for c in range(w):
            if labels[r, c] > 0:
                labels[r, c] = find(labels[r, c])

    return labels


# ──────────────────────────────────────────────────────────────
# Watershed Segmentation (barrier-constrained flood fill)
# ──────────────────────────────────────────────────────────────

def watershed_segment(pixels: np.ndarray, barrier_mask: np.ndarray,
                      color_tolerance: float = 60, min_area: int = 200,
                      connectivity: int = 8) -> list:
    """Segment image into tile regions using barrier-constrained flood fill.

    For each unvisited non-barrier pixel, BFS-floods to neighbors within
    color_tolerance of both the seed color AND the running mean color.

    Returns list of dicts: {'pixels': [(r,c),...], 'mean_color': (R,G,B), 'area': int}
    """
    h, w = pixels.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    neighbors = NEIGHBORS_8 if connectivity == 8 else NEIGHBORS_4

    # Mark all barrier pixels as visited
    visited[barrier_mask > 0] = True

    regions = []
    pixels_f = pixels.astype(np.float64)

    for r in range(h):
        for c in range(w):
            if visited[r, c]:
                continue

            # Seed color
            seed_color = pixels_f[r, c].copy()
            running_sum = seed_color.copy()
            running_count = 1

            component = [(r, c)]
            visited[r, c] = True
            queue = deque([(r, c)])

            while queue:
                cr, cc = queue.popleft()
                for dr, dc in neighbors:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr, nc]:
                        px = pixels_f[nr, nc]
                        # Check distance to seed color
                        seed_dist = perceptual_color_distance(px, seed_color)
                        # Check distance to running mean
                        mean_color = running_sum / running_count
                        mean_dist = perceptual_color_distance(px, mean_color)

                        if seed_dist <= color_tolerance and mean_dist <= color_tolerance:
                            visited[nr, nc] = True
                            queue.append((nr, nc))
                            component.append((nr, nc))
                            running_sum += px
                            running_count += 1

            if len(component) >= min_area:
                mean_color = running_sum / running_count
                regions.append({
                    'pixels': component,
                    'mean_color': tuple(int(round(v)) for v in mean_color),
                    'area': len(component),
                })

    return regions


# ──────────────────────────────────────────────────────────────
# Contour Tracing (Moore neighborhood) + Douglas-Peucker
# ──────────────────────────────────────────────────────────────

def trace_boundary(component: list, mask_shape: tuple) -> list:
    """Trace the outer boundary of a connected component using Moore neighborhood.

    Returns list of (col, row) points — (x, y) order for polygon rendering.
    """
    h, w = mask_shape
    # Build a local binary grid for the component
    rows = [p[0] for p in component]
    cols = [p[1] for p in component]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    # Pad by 1 to ensure boundary tracing works at edges
    pad = 1
    local_h = max_r - min_r + 1 + 2 * pad
    local_w = max_c - min_c + 1 + 2 * pad
    local = np.zeros((local_h, local_w), dtype=np.uint8)
    for r, c in component:
        local[r - min_r + pad, c - min_c + pad] = 1

    # Find starting point: topmost, then leftmost
    start = None
    for lr in range(local_h):
        for lc in range(local_w):
            if local[lr, lc] == 1:
                start = (lr, lc)
                break
        if start:
            break

    if not start:
        return []

    # Moore neighborhood: 8 directions, starting from left
    #   7 0 1
    #   6 . 2
    #   5 4 3
    directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

    boundary = [start]
    current = start
    # Start direction: come from left (direction index 6)
    backtrack_dir = 6

    max_steps = len(component) * 4  # Safety limit
    steps = 0

    while steps < max_steps:
        steps += 1
        # Start searching from (backtrack_dir + 1) % 8
        search_start = (backtrack_dir + 1) % 8
        found = False

        for i in range(8):
            d_idx = (search_start + i) % 8
            dr, dc = directions[d_idx]
            nr, nc = current[0] + dr, current[1] + dc

            if 0 <= nr < local_h and 0 <= nc < local_w and local[nr, nc] == 1:
                if (nr, nc) == start and len(boundary) > 2:
                    # Completed the loop
                    # Convert local coords back to image coords
                    result = [(c - pad + min_c, r - pad + min_r) for r, c in boundary]
                    return result

                boundary.append((nr, nc))
                current = (nr, nc)
                # Backtrack direction: opposite of the direction we came from
                backtrack_dir = (d_idx + 4) % 8
                found = True
                break

        if not found:
            break

    # Convert local coords back to image coords (x, y order)
    result = [(c - pad + min_c, r - pad + min_r) for r, c in boundary]
    return result


def douglas_peucker(points: list, epsilon: float) -> list:
    """Simplify a polygon using the Douglas-Peucker algorithm.

    points: list of (x, y) tuples
    epsilon: tolerance in pixels
    """
    if len(points) <= 2:
        return points

    # Find the point with maximum distance from line(start, end)
    start = np.array(points[0], dtype=np.float64)
    end = np.array(points[-1], dtype=np.float64)

    max_dist = 0
    max_idx = 0

    line_vec = end - start
    line_len = np.linalg.norm(line_vec)

    for i in range(1, len(points) - 1):
        pt = np.array(points[i], dtype=np.float64)
        if line_len == 0:
            dist = np.linalg.norm(pt - start)
        else:
            # Distance from point to line segment
            t = max(0, min(1, np.dot(pt - start, line_vec) / (line_len ** 2)))
            proj = start + t * line_vec
            dist = np.linalg.norm(pt - proj)

        if dist > max_dist:
            max_dist = dist
            max_idx = i

    if max_dist > epsilon:
        left = douglas_peucker(points[:max_idx + 1], epsilon)
        right = douglas_peucker(points[max_idx:], epsilon)
        return left[:-1] + right
    else:
        return [points[0], points[-1]]


def visvalingam_whyatt(points: list, target_n: int) -> list:
    """Simplify a polygon using the Visvalingam-Whyatt algorithm.

    Iteratively removes the vertex forming the smallest-area triangle with
    its neighbors. Better than Douglas-Peucker for geometric tiles: naturally
    preserves sharp corners (large-area triangles) while removing noise points.

    points: list of (x, y) tuples (closed or open polygon)
    target_n: target vertex count to reduce to (minimum 3)
    Returns: simplified list of (x, y) tuples
    """
    if len(points) <= target_n or len(points) < 4:
        return points

    target_n = max(target_n, 3)

    # Work with a mutable list of indices into the original points
    indices = list(range(len(points)))

    def triangle_area(i_prev, i_curr, i_next):
        """Area of triangle formed by three vertices (shoelace)."""
        x1, y1 = points[indices[i_prev]]
        x2, y2 = points[indices[i_curr]]
        x3, y3 = points[indices[i_next]]
        return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)

    while len(indices) > target_n:
        n = len(indices)
        min_area = float('inf')
        min_idx = -1

        for i in range(n):
            i_prev = (i - 1) % n
            i_next = (i + 1) % n
            area = triangle_area(i_prev, i, i_next)
            if area < min_area:
                min_area = area
                min_idx = i

        if min_idx == -1:
            break

        indices.pop(min_idx)

    return [points[i] for i in indices]


def estimate_target_vertices(area_pixels: int, img_area: int) -> int:
    """Estimate target vertex count from shape area relative to image.

    Tiny tiles → 4-5 vertices, medium → 5-8, large → 8-12.
    """
    ratio = area_pixels / img_area if img_area > 0 else 0

    if ratio < 0.002:
        return 4
    elif ratio < 0.005:
        return 5
    elif ratio < 0.01:
        return 6
    elif ratio < 0.02:
        return 8
    elif ratio < 0.05:
        return 10
    else:
        return 12


# ──────────────────────────────────────────────────────────────
# Edge-Guided Boundary Snapping
# ──────────────────────────────────────────────────────────────

def snap_boundary_to_edges(boundary: list, edge_mask: np.ndarray,
                           snap_radius: int = 5) -> list:
    """Snap boundary points to nearby edge pixels for sharper boundaries.

    For each boundary point, searches within snap_radius pixels for the
    nearest edge pixel and moves the point there.

    boundary: list of (x, y) tuples (col, row order)
    edge_mask: (H, W) uint8 edge mask (0 or 255)
    snap_radius: search radius in pixels
    Returns: list of (x, y) tuples with snapped coordinates
    """
    if not boundary:
        return boundary

    h, w = edge_mask.shape
    edge_binary = edge_mask > 0
    snapped = []

    for bx, by in boundary:
        # Search within snap_radius for nearest edge pixel
        best_dist = float('inf')
        best_x, best_y = bx, by

        for dy in range(-snap_radius, snap_radius + 1):
            for dx in range(-snap_radius, snap_radius + 1):
                nx, ny = bx + dx, by + dy
                if 0 <= ny < h and 0 <= nx < w and edge_binary[ny, nx]:
                    dist = dx * dx + dy * dy
                    if dist < best_dist:
                        best_dist = dist
                        best_x, best_y = nx, ny

        snapped.append((best_x, best_y))

    return snapped


# ──────────────────────────────────────────────────────────────
# Geometry-Aware Polygon Fitting
# ──────────────────────────────────────────────────────────────

def _angle_between(v1, v2):
    """Angle in degrees between two 2D vectors."""
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    angle = math.atan2(abs(cross), dot)
    return math.degrees(angle)


def _interior_angle(p_prev, p_curr, p_next):
    """Interior angle at p_curr in degrees."""
    v1 = (p_prev[0] - p_curr[0], p_prev[1] - p_curr[1])
    v2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    angle = math.atan2(cross, dot)
    return abs(math.degrees(angle))


def merge_collinear_segments(vertices: list, angle_threshold: float = 10.0) -> list:
    """Remove vertices where consecutive edges are nearly collinear.

    If the angle at a vertex is within angle_threshold of 180 degrees,
    the vertex is redundant and removed.
    """
    if len(vertices) < 4:
        return vertices

    result = []
    n = len(vertices)
    for i in range(n):
        p_prev = vertices[(i - 1) % n]
        p_curr = vertices[i]
        p_next = vertices[(i + 1) % n]
        angle = _interior_angle(p_prev, p_curr, p_next)
        # Keep vertex if angle is NOT close to 180 (i.e., not collinear)
        if abs(angle - 180.0) > angle_threshold:
            result.append(p_curr)

    return result if len(result) >= 3 else vertices


# Known angles in Islamic geometric patterns
KNOWN_ANGLES = [36, 45, 54, 60, 72, 90, 108, 120, 135, 144, 150, 160, 170, 180]


def snap_angles(vertices: list, angle_tolerance: float = 8.0) -> list:
    """Snap interior angles to known Islamic geometry values.

    Adjusts vertex positions to achieve exact known angles where the
    measured angle is within angle_tolerance of a known value.
    """
    if len(vertices) < 3:
        return vertices

    n = len(vertices)
    result = list(vertices)

    for i in range(n):
        p_prev = result[(i - 1) % n]
        p_curr = result[i]
        p_next = result[(i + 1) % n]

        angle = _interior_angle(p_prev, p_curr, p_next)

        # Find nearest known angle
        nearest = min(KNOWN_ANGLES, key=lambda a: abs(a - angle))
        if abs(nearest - angle) <= angle_tolerance and abs(nearest - angle) > 0.1:
            # Rotate the outgoing edge to achieve the target angle
            # We adjust p_next direction from p_curr
            v_in = (p_prev[0] - p_curr[0], p_prev[1] - p_curr[1])
            len_in = math.sqrt(v_in[0] ** 2 + v_in[1] ** 2)
            if len_in < 1e-9:
                continue

            v_out = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])
            len_out = math.sqrt(v_out[0] ** 2 + v_out[1] ** 2)
            if len_out < 1e-9:
                continue

            # Current angle of incoming edge
            angle_in = math.atan2(v_in[1], v_in[0])
            # Determine sign of the turn
            cross = v_in[0] * v_out[1] - v_in[1] * v_out[0]
            sign = 1 if cross >= 0 else -1

            # Target outgoing angle
            target_rad = math.radians(nearest)
            angle_out = angle_in + sign * target_rad

            # New p_next position (keep same distance)
            new_next_x = p_curr[0] + len_out * math.cos(angle_out)
            new_next_y = p_curr[1] + len_out * math.sin(angle_out)
            result[(i + 1) % n] = (new_next_x, new_next_y)

    return result


def snap_parallel_edges(vertices: list, parallel_threshold: float = 5.0) -> list:
    """For even-sided polygons, snap nearly-parallel opposite edges to exactly parallel.

    parallel_threshold: max angle deviation in degrees to consider "nearly parallel"
    """
    n = len(vertices)
    if n < 4 or n % 2 != 0:
        return vertices

    result = list(vertices)
    half = n // 2

    for i in range(half):
        # Edge i: vertices[i] → vertices[(i+1)%n]
        # Opposite edge: vertices[i+half] → vertices[(i+half+1)%n]
        e1_start = result[i]
        e1_end = result[(i + 1) % n]
        e2_start = result[i + half]
        e2_end = result[(i + half + 1) % n]

        v1 = (e1_end[0] - e1_start[0], e1_end[1] - e1_start[1])
        v2 = (e2_end[0] - e2_start[0], e2_end[1] - e2_start[1])

        len1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        len2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

        if len1 < 1e-9 or len2 < 1e-9:
            continue

        angle_diff = _angle_between(v1, v2)
        # For parallel edges, angle should be ~0 or ~180
        parallel_dev = min(angle_diff, abs(180 - angle_diff))

        if parallel_dev <= parallel_threshold and parallel_dev > 0.1:
            # Average the direction and apply to both edges
            avg_angle = math.atan2(v1[1] / len1 - v2[1] / len2,
                                   v1[0] / len1 - v2[0] / len2) + math.pi / 2
            # Simpler: just make e2 parallel to e1 by adjusting e2_end
            dir1 = (v1[0] / len1, v1[1] / len1)
            # Opposite edge goes in reverse direction
            new_e2_end_x = e2_start[0] - dir1[0] * len2
            new_e2_end_y = e2_start[1] - dir1[1] * len2
            result[(i + half + 1) % n] = (new_e2_end_x, new_e2_end_y)

    return result


# ──────────────────────────────────────────────────────────────
# Classification + Normalization
# ──────────────────────────────────────────────────────────────

OVERLAY_COLORS = [
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4',
    '#ffeaa7', '#dfe6e9', '#fd79a8', '#6c5ce7',
    '#00b894', '#e17055', '#0984e3', '#fdcb6e',
]


def classify_zone(cx: float, cy: float, img_cx: float, img_cy: float, radius: float) -> str:
    """Classify a shape into a zone based on distance from image center."""
    dist = math.sqrt((cx - img_cx) ** 2 + (cy - img_cy) ** 2)
    ratio = dist / radius if radius > 0 else 0

    if ratio < 0.2:
        return 'inner-star'
    elif ratio < 0.45:
        return 'rosette'
    elif ratio < 0.65:
        return 'transition'
    elif ratio < 0.85:
        return 'satellite'
    else:
        return 'outer'


def polygon_centroid(vertices: list) -> tuple:
    """Compute centroid of a polygon given as list of (x, y) tuples."""
    if not vertices:
        return (0, 0)
    n = len(vertices)
    cx = sum(v[0] for v in vertices) / n
    cy = sum(v[1] for v in vertices) / n
    return (cx, cy)


def polygon_area(vertices: list) -> float:
    """Compute area of a polygon using the shoelace formula."""
    n = len(vertices)
    if n < 3:
        return 0
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    return abs(area) / 2


def shape_type_from_vertices(n_vertices: int) -> str:
    """Guess shape type from vertex count."""
    mapping = {
        3: 'polygon',  # triangle
        4: 'kite',  # could be kite, rhombus, square
        5: 'pentagon',
        6: 'hexagon',
        7: 'polygon',
        8: 'polygon',  # octagon
        9: 'polygon',
        10: 'star',
    }
    return mapping.get(n_vertices, 'polygon')


# ──────────────────────────────────────────────────────────────
# Main Pipeline
# ──────────────────────────────────────────────────────────────

def extract_shapes(image_path: str, tolerance: float = 60, min_area: int = 200,
                   simplify: float = 3.0, n_colors: int = 8,
                   edge_threshold: float = 30, work_size: int = 600,
                   connectivity: int = 8, luminance_threshold: int = 240,
                   edge_dilation: int = 0, snap_radius: int = 5,
                   mode: str = 'auto', morph_close: int = 1,
                   segmentation: str = 'auto') -> dict:
    """Run the full shape extraction pipeline.

    Returns dict with image_size, edge_overlay_path, strapwork_overlay_path,
    and shapes list (each shape includes fill_color).
    """
    img = Image.open(image_path).convert('RGB')
    orig_w, orig_h = img.size
    print(f"Image size: {orig_w}x{orig_h}")

    # Resize to working resolution for processing
    work_img = img.copy()
    work_img.thumbnail((work_size, work_size), Image.Resampling.LANCZOS)
    work_w, work_h = work_img.size
    scale_x = orig_w / work_w
    scale_y = orig_h / work_h
    print(f"Working resolution: {work_w}x{work_h} (scale: {scale_x:.2f}x, {scale_y:.2f}x)")

    pixels = np.array(work_img)

    # Image center and approximate radius (at working resolution)
    img_cx, img_cy = work_w / 2, work_h / 2
    img_radius = min(work_w, work_h) / 2

    output_dir = os.path.dirname(image_path) or '.'

    # ── Step 1: Edge detection ──
    print("Step 1: Edge detection (Sobel)...")
    gray = np.array(work_img.convert('L'), dtype=np.float64)
    edge_mask = sobel_edge_detect(gray, threshold=edge_threshold)

    edge_path = os.path.join(output_dir, 'edges.png')
    edge_img = Image.fromarray(edge_mask, mode='L')
    # Save at original resolution
    edge_img_resized = edge_img.resize((orig_w, orig_h), Image.Resampling.LANCZOS)
    edge_img_resized.save(edge_path)
    print(f"  Edge overlay saved: {edge_path}")

    # ── Step 2: Color quantization ──
    print(f"Step 2: Color quantization ({n_colors} colors)...")
    dominant_colors = quantize_colors(work_img, n_colors, work_size=work_size)
    print(f"  Dominant colors: {dominant_colors}")

    # ── Step 3: Image classification + barrier detection ──
    print("Step 3: Detecting barrier mask...")
    if mode == 'auto':
        detected_mode = classify_image_type(pixels)
        print(f"  Auto-detected mode: {detected_mode}")
    else:
        detected_mode = mode
        print(f"  Forced mode: {detected_mode}")

    # Adapt parameters per mode
    effective_connectivity = connectivity
    effective_tolerance = tolerance
    effective_min_area = min_area
    effective_simplify = simplify
    effective_collinear = 10.0
    if detected_mode == 'white-strapwork':
        effective_connectivity = 4  # 4-conn prevents leaking through diagonal gaps
        effective_tolerance = min(tolerance, 50)  # cap color tolerance
        effective_min_area = min(min_area, 100)  # lower area threshold
        effective_simplify = min(simplify, 1.5)  # sharper polygon boundaries
        effective_collinear = 6.0  # tighter collinear merge for crisper vertices
        print(f"  White-strapwork overrides: connectivity=4, "
              f"tolerance={effective_tolerance}, min_area={effective_min_area}, "
              f"simplify={effective_simplify}, collinear={effective_collinear}")

    barrier_mask = detect_barrier_mask(pixels, edge_mask,
                                       mode=detected_mode,
                                       luminance_threshold=luminance_threshold,
                                       edge_dilation=edge_dilation,
                                       morph_close=morph_close)

    strapwork_path = os.path.join(output_dir, 'strapwork.png')
    strapwork_img = Image.fromarray(barrier_mask * 255, mode='L')
    strapwork_img_resized = strapwork_img.resize((orig_w, orig_h), Image.Resampling.NEAREST)
    strapwork_img_resized.save(strapwork_path)
    strapwork_coverage = np.sum(barrier_mask > 0) / barrier_mask.size * 100
    print(f"  Barrier coverage: {strapwork_coverage:.1f}% of image")
    print(f"  Strapwork overlay saved: {strapwork_path}")

    # ── Step 4: Segmentation (CCL or watershed) ──
    use_ccl = (segmentation == 'ccl' or
               (segmentation == 'auto' and detected_mode == 'white-strapwork'))

    if use_ccl:
        print("Step 4: Connected Component Labeling (barrier-inverse)...")
        tile_mask = (1 - barrier_mask).astype(np.uint8)
        label_map = connected_component_label(tile_mask, connectivity=effective_connectivity)
        unique_labels = np.unique(label_map)
        unique_labels = unique_labels[unique_labels > 0]  # skip background

        regions = []
        for lbl in unique_labels:
            coords = np.argwhere(label_map == lbl)  # (N, 2) array of (row, col)
            if len(coords) < effective_min_area:
                continue
            # Compute mean color from original image
            rows, cols = coords[:, 0], coords[:, 1]
            mean_r = int(round(np.mean(pixels[rows, cols, 0])))
            mean_g = int(round(np.mean(pixels[rows, cols, 1])))
            mean_b = int(round(np.mean(pixels[rows, cols, 2])))
            regions.append({
                'pixels': [(int(r), int(c)) for r, c in coords],
                'mean_color': (mean_r, mean_g, mean_b),
                'area': len(coords),
            })
        print(f"  CCL regions: {len(regions)} (from {len(unique_labels)} labels, "
              f"min_area={effective_min_area})")
    else:
        print("Step 4: Watershed segmentation (barrier-constrained flood fill)...")
        regions = watershed_segment(pixels, barrier_mask,
                                    color_tolerance=effective_tolerance,
                                    min_area=effective_min_area,
                                    connectivity=effective_connectivity)
        print(f"  Watershed regions: {len(regions)}")

    # Fallback to per-color BFS if segmentation finds too few regions
    if len(regions) < 3:
        print("  Fallback: per-color BFS (segmentation found < 3 regions)...")
        all_components = []
        for i, color in enumerate(dominant_colors):
            mask = color_mask(pixels, color, tolerance)
            components = find_connected_components(mask, min_area, connectivity)
            print(f"    Color {color}: {len(components)} component(s)")
            for comp in components:
                all_components.append({
                    'pixels': comp,
                    'mean_color': color,
                    'area': len(comp),
                })
        regions = all_components
        print(f"  Fallback total: {len(regions)} components")

    # Sort by area descending — largest shapes first
    regions.sort(key=lambda r: r['area'], reverse=True)

    # ── Step 5: Boundary tracing + edge snapping + simplification + polygon fitting ──
    print("Step 5: Tracing boundaries, snapping to edges, simplifying...")
    raw_shapes = []

    for region in regions:
        boundary = trace_boundary(region['pixels'], (work_h, work_w))
        if len(boundary) < 6:
            continue

        # Sub-sample boundary if very dense (>800 points)
        if len(boundary) > 800:
            step = len(boundary) // 800
            boundary = boundary[::step]

        # Edge-guided boundary snapping
        boundary = snap_boundary_to_edges(boundary, edge_mask, snap_radius=snap_radius)

        # Simplification: Visvalingam-Whyatt for white-strapwork, Douglas-Peucker for general
        if use_ccl:
            target_n = estimate_target_vertices(region['area'], work_w * work_h)
            simplified = visvalingam_whyatt(boundary, target_n)
        else:
            simplified = douglas_peucker(boundary, effective_simplify)

        # Geometry-aware polygon fitting
        simplified = merge_collinear_segments(simplified, angle_threshold=effective_collinear)
        simplified = snap_angles(simplified, angle_tolerance=8.0)
        simplified = snap_parallel_edges(simplified, parallel_threshold=5.0)

        # Filter: need at least 3 vertices and at most 20 for geometric tiles
        n_verts = len(simplified)
        if n_verts < 3 or n_verts > 20:
            continue

        # Scale coordinates back to original image dimensions
        orig_vertices = [(x * scale_x, y * scale_y) for x, y in simplified]

        # Centroid and zone (at original resolution)
        centroid = polygon_centroid(orig_vertices)
        orig_cx, orig_cy = orig_w / 2, orig_h / 2
        orig_radius = min(orig_w, orig_h) / 2
        zone = classify_zone(centroid[0], centroid[1], orig_cx, orig_cy, orig_radius)

        # Area ratio (at original resolution)
        area = polygon_area(orig_vertices)
        total_area = orig_w * orig_h
        area_ratio = area / total_area if total_area > 0 else 0

        # Fill color from region mean
        mean_color = region['mean_color']
        fill_color = f'rgb({mean_color[0]}, {mean_color[1]}, {mean_color[2]})'

        # Normalize vertices to 0-1 (relative to original image dimensions)
        norm_vertices = [[x / orig_w, y / orig_h] for x, y in orig_vertices]

        raw_shapes.append({
            'type': shape_type_from_vertices(n_verts),
            'zone': zone,
            'vertex_count': n_verts,
            'count': 1,
            'approximate_vertices': norm_vertices,
            'approximate_area_ratio': round(area_ratio, 4),
            'fill_color': fill_color,
            'notes': f'auto-detected, {n_verts}-vertex polygon, '
                     f'fill={fill_color}, zone={zone}',
            '_area_for_sort': area_ratio,
        })

    print(f"  Traced {len(raw_shapes)} shapes")

    # Sort by area descending, assign IDs
    raw_shapes.sort(key=lambda s: s['_area_for_sort'], reverse=True)
    shapes = []
    for idx, shape in enumerate(raw_shapes):
        shape.pop('_area_for_sort', None)
        shape['id'] = f'shape-{idx + 1:03d}'
        shape['overlay_color'] = OVERLAY_COLORS[idx % len(OVERLAY_COLORS)]
        shapes.append(shape)

    print(f"  Final output: {len(shapes)} shapes")

    return {
        'image_size': [orig_w, orig_h],
        'edge_overlay_path': os.path.basename(edge_path),
        'strapwork_overlay_path': os.path.basename(strapwork_path),
        'shapes': shapes,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Extract tile shapes from a reference image for pattern interpretation.'
    )
    parser.add_argument('image', help='Path to reference image')
    parser.add_argument('--output', '-o', default=None,
                        help='Output JSON path (default: <image_dir>/shapes.json)')
    parser.add_argument('--tolerance', '-t', type=float, default=60,
                        help='Color tolerance in perceptual distance (default: 60)')
    parser.add_argument('--min-area', type=int, default=200,
                        help='Minimum component area in pixels (default: 200)')
    parser.add_argument('--simplify', '-s', type=float, default=3.0,
                        help='Douglas-Peucker simplification tolerance in pixels (default: 3.0)')
    parser.add_argument('--colors', '-c', type=int, default=8,
                        help='Number of dominant colors to extract (default: 8)')
    parser.add_argument('--edge-threshold', type=float, default=30,
                        help='Sobel edge magnitude threshold 0-255 (default: 30)')
    parser.add_argument('--work-size', type=int, default=600,
                        help='Working resolution for processing (default: 600)')
    parser.add_argument('--connectivity', type=int, default=8, choices=[4, 8],
                        help='BFS connectivity: 4 or 8 (default: 8)')
    parser.add_argument('--luminance-threshold', type=int, default=240,
                        help='Strapwork brightness cutoff 0-255 (default: 240)')
    parser.add_argument('--edge-dilation', type=int, default=0,
                        help='Edge barrier dilation radius in pixels (default: 0)')
    parser.add_argument('--snap-radius', type=int, default=5,
                        help='Boundary-to-edge snapping search radius (default: 5)')
    parser.add_argument('--mode', default='auto', choices=['auto', 'white-strapwork', 'general'],
                        help='Barrier detection mode (default: auto)')
    parser.add_argument('--morph-close', type=int, default=1,
                        help='Morphological closing radius for gap sealing (default: 1)')
    parser.add_argument('--segmentation', default='auto',
                        choices=['auto', 'ccl', 'watershed'],
                        help='Segmentation method: auto (CCL for white-strapwork, '
                             'watershed for general), ccl, or watershed (default: auto)')

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: Image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    result = extract_shapes(
        args.image,
        tolerance=args.tolerance,
        min_area=args.min_area,
        simplify=args.simplify,
        n_colors=args.colors,
        edge_threshold=args.edge_threshold,
        work_size=args.work_size,
        connectivity=args.connectivity,
        luminance_threshold=args.luminance_threshold,
        edge_dilation=args.edge_dilation,
        snap_radius=args.snap_radius,
        mode=args.mode,
        morph_close=args.morph_close,
        segmentation=args.segmentation,
    )

    output_path = args.output or os.path.join(
        os.path.dirname(args.image) or '.', 'shapes.json'
    )
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nOutput: {output_path}")
    print(f"Edge overlay: {result['edge_overlay_path']}")
    print(f"Strapwork overlay: {result['strapwork_overlay_path']}")
    print(f"Shapes detected: {len(result['shapes'])}")


if __name__ == '__main__':
    main()
