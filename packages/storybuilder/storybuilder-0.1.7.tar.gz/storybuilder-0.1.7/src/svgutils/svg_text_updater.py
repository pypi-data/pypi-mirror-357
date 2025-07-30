#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import xml.etree.ElementTree as ET
import re
import glob

class SVGTextProcessor:
    def __init__(self):
        self.ns = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
        ET.register_namespace('', self.ns['svg'])
        ET.register_namespace('xlink', self.ns['xlink'])

    def merge_text_elements(self, svg_path, output_path=None, max_x_offset=200):
        """Merge text elements with same attributes and close x positions
        
        Args:
            svg_path: Path to SVG file
            output_path: Output path (optional)
            max_x_offset: Maximum gap between text elements to merge (default: 200)
        """
        tree = ET.parse(svg_path)
        root = tree.getroot()
        made_changes = False

        for parent in root.findall('.//svg:g', self.ns):
            text_elements = parent.findall('svg:text', self.ns)
            if len(text_elements) <= 1:
                continue

            text_groups = {}
            for text in text_elements:
                # Preserve original text-anchor and transform
                original_anchor = text.get('text-anchor', '')
                original_transform = text.get('transform', '')
                
                y_offset = None
                x_pos = None
                width = 0
                if original_transform:
                    matrix_values = re.findall(r'matrix\((.*?)\)', original_transform)[0].split()
                    y_offset = matrix_values[5]
                    x_pos = float(matrix_values[4])
                    font_size = float(text.get('font-size', '12').rstrip('px'))
                    width = len(text.text or '') * font_size * 0.6

                key = (
                    text.get('font-family', ''),
                    text.get('font-size', ''),
                    text.get('font-weight', ''),
                    text.get('fill', ''),
                    y_offset,
                    original_anchor  # Include text-anchor in the key
                )

                if key not in text_groups:
                    text_groups[key] = []
                text_groups[key].append((text, x_pos, width, original_transform))

            # Process each group
            for key, elements in text_groups.items():
                if len(elements) <= 1:
                    continue

                elements.sort(key=lambda x: x[1] if x[1] is not None else float('-inf'))
                
                current_group = [elements[0]]
                merged_groups = []
                
                for i in range(1, len(elements)):
                    current_elem = elements[i]
                    prev_elem = current_group[-1]
                    
                    if (current_elem[1] is not None and 
                        prev_elem[1] is not None and 
                        current_elem[1] - (prev_elem[1] + prev_elem[2]) <= max_x_offset):
                        current_group.append(current_elem)
                    else:
                        if len(current_group) > 1:
                            merged_groups.append(current_group)
                        current_group = [current_elem]
                
                if len(current_group) > 1:
                    merged_groups.append(current_group)

                # Merge each group
                for group in merged_groups:
                    made_changes = True
                    base_element = group[0][0]
                    combined_text = ''

                    for elem, _, _, _ in group:
                        if elem.text:
                            combined_text += elem.text

                    base_element.text = combined_text
                    
                    # Remove other elements
                    for elem, _, _, _ in group[1:]:
                        parent.remove(elem)

        if made_changes:
            output_path = output_path or svg_path
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            print(f"Merged text elements in: {output_path}")
            return True
        else:
            print(f"No merging needed: {svg_path}")
            return False

    def update_font(self, svg_path, font_family, output_path=None):
        """Update font family for text elements"""
        tree = ET.parse(svg_path)
        root = tree.getroot()
        made_changes = False

        for text in root.findall('.//svg:text', self.ns):
            current_font = text.get('font-family', '')
            if current_font != font_family:
                text.set('font-family', font_family)
                made_changes = True

        if made_changes:
            output_path = output_path or svg_path
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            print(f"Updated: {output_path}")
            return True
        else:
            print(f"No changes needed: {svg_path}")
            return False

    def set_text_anchor(self, svg_path, output_path=None):
        """Set text-anchor to middle
        
        Args:
            svg_path: Path to SVG file
            output_path: Output path (optional)
        """
        tree = ET.parse(svg_path)
        root = tree.getroot()
        made_changes = False

        # Process all text elements
        for text in root.findall('.//svg:text', self.ns):
            # Set text-anchor to middle
            if text.get('text-anchor') != 'middle':
                text.set('text-anchor', 'middle')
                made_changes = True

        if made_changes:
            output_path = output_path or svg_path
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            print(f"Updated text-anchor in: {output_path}")
            return True
        else:
            print(f"No text-anchor changes needed: {svg_path}")
            return False

    def align_text(self, svg_path, output_path=None):
        """Align text elements horizontally to center
        
        Args:
            svg_path: Path to SVG file
            output_path: Output path (optional)
        """
        tree = ET.parse(svg_path)
        root = tree.getroot()
        made_changes = False

        # Get SVG width
        width = float(root.get('width', '0'))
        if width == 0:
            viewBox = root.get('viewBox', '').split()
            if len(viewBox) == 4:
                width = float(viewBox[2])
        
        if width == 0:
            print(f"Warning: Could not determine width for {svg_path}")
            return False

        center_x = width / 2

        # Process all text elements
        for text in root.findall('.//svg:text', self.ns):
            # Update transform to center position
            transform = text.get('transform', '')
            if transform:
                # Check for matrix transform
                matrix_match = re.match(r'matrix\(([^)]+)\)', transform)
                if matrix_match:
                    matrix_values = matrix_match.group(1).split()
                    if len(matrix_values) == 6:
                        matrix_values[4] = str(center_x)
                        new_transform = f"matrix({' '.join(matrix_values)})"
                        text.set('transform', new_transform)
                        made_changes = True
                else:
                    # Check for translate transform
                    translate_match = re.match(r'translate\(([-\d.]+)(?:[,\s]+([-\d.]+))?\)', transform)
                    if translate_match:
                        y_value = translate_match.group(2) or '0'
                        new_transform = f"translate({center_x},{y_value})"
                        text.set('transform', new_transform)
                        made_changes = True

        if made_changes:
            output_path = output_path or svg_path
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            print(f"Aligned text in: {output_path}")
            return True
        else:
            print(f"No alignment changes needed: {svg_path}")
            return False

    def center_text(self, svg_path, output_path=None):
        """Center text elements by both anchor and position
        
        Args:
            svg_path: Path to SVG file
            output_path: Output path (optional)
        """
        # First set text-anchor
        self.set_text_anchor(svg_path, output_path)
        # Then align position
        self.align_text(svg_path, output_path)

def process_files(processor, command, files, recursive=False, **kwargs):
    """Process multiple files with given command"""
    for pattern in files:
        pattern = os.path.expanduser(pattern)
        
        if recursive and '**' not in pattern:
            base_dir = os.path.dirname(pattern) or '.'
            file_pattern = os.path.basename(pattern)
            pattern = os.path.join(base_dir, '**', file_pattern)
        
        matching_files = glob.glob(pattern, recursive=recursive)
        
        if not matching_files:
            print(f"No files found matching pattern: {pattern}")
            continue
        
        print(f"Found {len(matching_files)} files matching pattern: {pattern}")
        for file_path in matching_files:
            if file_path.lower().endswith('.svg'):
                command_func = getattr(processor, command)
                try:
                    command_func(file_path, **kwargs)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description='SVG text element processor',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # merge command
    merge_parser = subparsers.add_parser('merge', 
        help='Merge similar text elements',
        description='Merge text elements with same attributes when the gap between them is within the specified limit')
    merge_parser.add_argument('files', nargs='+', help='SVG files to process')
    merge_parser.add_argument('-r', '--recursive', action='store_true', help='Process directories recursively')
    merge_parser.add_argument('-o', '--output', help='Output directory')
    merge_parser.add_argument('-x', '--max-x-offset', type=float, default=200,
                         help='Maximum gap between text elements to merge (default: 200)')

    # font command
    font_parser = subparsers.add_parser('font', help='Update font family')
    font_parser.add_argument('files', nargs='+', help='SVG files to process')
    font_parser.add_argument('-f', '--font-family', default="Verdana, Consolas, Monaco, sans-serif", help='Font family to set')
    font_parser.add_argument('-r', '--recursive', action='store_true', help='Process directories recursively')
    font_parser.add_argument('-o', '--output', help='Output directory')

    # center command
    center_parser = subparsers.add_parser('center', help='Center text elements')
    center_parser.add_argument('files', nargs='+', help='SVG files to process')
    center_parser.add_argument('-r', '--recursive', action='store_true', help='Process directories recursively')
    center_parser.add_argument('-o', '--output', help='Output directory')

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    processor = SVGTextProcessor()
    
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    if args.command == 'merge':
        process_files(processor, 'merge_text_elements', args.files, args.recursive,
                     output_path=args.output, max_x_offset=args.max_x_offset)
    elif args.command == 'font':
        process_files(processor, 'update_font', args.files, args.recursive,
                     font_family=args.font_family, output_path=args.output)
    elif args.command == 'center':
        process_files(processor, 'center_text', args.files, args.recursive,
                     output_path=args.output)

if __name__ == '__main__':
    main() 