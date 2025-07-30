import os
import xml.etree.ElementTree as ET
import re
import sys
import argparse
from itertools import product
from collections import defaultdict
import json
import glob

def extract_parts(filename):
    """
    Extract body part and posture from filename.
    
    Args:
        filename (str): Name of the SVG file
        
    Returns:
        tuple: (body_part, posture) if found, (None, None) otherwise
    """
    if filename == 'mat.svg':
        return ('mat', '')
        
    # Valid body parts and their variations
    valid_body_parts = {
        'head', 'torso', 'leg', 'left-arm', 'right-arm'
    }
    
    # Extract everything after the prefix and before .svg
    pattern = re.compile(r'[a-zA-Z]+-(.+)\.svg')
    match = pattern.match(filename)
    
    if not match:
        print(f"Skipping {filename}: Doesn't match expected pattern")
        return None, None
    
    # Get the full content after the prefix
    content = match.group(1)
    
    # Try to find the longest valid body part at the start
    found_part = None
    for part in valid_body_parts:
        if content.startswith(part + '-'):
            # Keep the longest matching part (important for cases like 'left-arm' vs 'arm')
            if found_part is None or len(part) > len(found_part):
                found_part = part
    
    if found_part:
        # Extract the posture (everything after the body part and the hyphen)
        posture = content[len(found_part) + 1:]
        return found_part, posture
    
    print(f"Warning: Could not identify valid body part in {filename}")
    return None, None

def process_svg_files(input_folder, character_name="character"):
    """
    Process SVG files in the specified folder, modifying the class attribute
    of the top-level <g> element to include both body part and posture.
    
    Args:
        input_folder (str): Path to the folder containing SVG files
    """
    # Register the SVG namespace
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    namespace = True
    
    # Process each SVG file in the folder
    for filename in os.listdir(input_folder):
        if (not filename.endswith('.svg')) or (not filename.startswith(character_name)):
            continue
            
        file_path = os.path.join(input_folder, filename)
        
        # Extract body part and posture from filename
        body_part, posture = extract_parts(filename)
        if body_part is None:
            continue
        
        # Combine body part and posture for the class attribute
        class_value = body_part if body_part == 'mat' else f"{body_part}-{posture}"
        
        try:
            # Parse the SVG file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find the first g element
            np_str = '{http://www.w3.org/2000/svg}' if namespace else ''
            g_elem = root.find('.//' + np_str + 'g')
            #g_elem = root.find('.//{http://www.w3.org/2000/svg}g')
            
            if g_elem is not None:
                # Set or update the class attribute
                g_elem.set('class', class_value)
                
                # Write back to file
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
                print(f"Successfully processed {filename} - Set class to '{class_value}'")
            else:
                print(f"No <g> element found in {filename}")
                
        except ET.ParseError as e:
            print(f"Error parsing {filename}: {str(e)}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

def get_body_parts_from_files(input_folder, prefix=""):
    """
    Scan folder and organize SVG files by body part type.
    
    Returns:
        dict: Dictionary with body parts as keys and lists of (filename, class_name) tuples as values
    """
    parts_dict = defaultdict(list)
    
    for filename in os.listdir(input_folder):
        if (not filename.endswith('.svg')) or (not filename.startswith(prefix)):
            continue
            
        body_part, posture = extract_parts(filename)
        if body_part and body_part != 'mat':
            class_name = f"{body_part}-{posture}"
            file_path = os.path.join(input_folder, filename)
            parts_dict[body_part].append((file_path, class_name))
    
    return parts_dict

def remove_namespace_prefix(element):
    """
    Recursively remove namespace prefixes from element and its children.
    
    Args:
        element: XML element to process
    """
    # Remove namespace from current element
    if '}' in element.tag:
        element.tag = element.tag.split('}', 1)[1]
    
    # Remove xmlns attributes
    for key in list(element.attrib.keys()):
        if key.startswith('xmlns:'):
            del element.attrib[key]
    
    # Process children recursively
    for child in element:
        remove_namespace_prefix(child)

def extract_transform_values(transform_str):
    """
    Extract translate values from transform attribute.
    
    Args:
        transform_str (str): Transform attribute string
        
    Returns:
        tuple: (x, y) translation values or (0, 0) if not found
    """
    if not transform_str:
        return 0, 0
        
    match = re.search(r'translate\(([-\d.]+)(?:,|\s+)([-\d.]+)\)', transform_str)
    if match:
        return float(match.group(1)), float(match.group(2))
    return 0, 0

def apply_transform_offset(element, x_offset, y_offset):
    """
    Apply offset to element's transform attribute.
    
    Args:
        element: XML element
        x_offset (float): X offset to add
        y_offset (float): Y offset to add
    """
    transform = element.get('transform', '')
    current_x, current_y = extract_transform_values(transform)
    
    # Combine existing translate with new offset
    new_x = current_x + x_offset
    new_y = current_y + y_offset
    
    # Create new transform attribute
    new_transform = f'translate({new_x} {new_y})'
    
    # If there are other transforms, preserve them
    other_transforms = re.sub(r'translate\([^)]+\)', '', transform).strip()
    if other_transforms:
        new_transform = f'{new_transform} {other_transforms}'
    
    element.set('transform', new_transform)

def extract_g_content(file_path, ext_width=0, ext_height=0, part_x_offset=0, part_y_offset=0,namespace=True):
    """
    Extract the content of the top-level g element from an SVG file.
    
    Returns:
        str: The g element and its contents as a string
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract width and height from root SVG element
        width = root.get('width')
        height = root.get('height')
        
        # If width/height not found as attributes, try viewBox
        if not width or not height:
            viewbox = root.get('viewBox')
            if viewbox:
                try:
                    # viewBox format: min-x min-y width height
                    parts = viewbox.split()
                    if len(parts) == 4:
                        width = parts[2]
                        height = parts[3]
                except:
                    pass
            
        # Find the first g element
        np_str = '{http://www.w3.org/2000/svg}' if namespace else ''
        g_elem = root.find('.//'+np_str+'g')
        
        if g_elem is not None:
            # Create a deep copy of the g element
            g_copy = ET.fromstring(ET.tostring(g_elem))
            
            # Remove namespace prefixes from the copied element
            remove_namespace_prefix(g_copy)

            # Apply offset to the transform attribute
            x_offset = (ext_width - int(width))/2 + part_x_offset
            y_offset = (ext_height - int(height))/2 + part_y_offset
            if x_offset != 0 or y_offset != 0:
                apply_transform_offset(g_copy, x_offset, y_offset)

            # Convert to string without namespace declarations
            g_str = ET.tostring(g_copy, encoding='unicode')
            
            # Remove any remaining namespace declarations
            g_str = re.sub(r'\sxmlns:ns0="[^"]*"', '', g_str)
            g_str = re.sub(r'\sxmlns="[^"]*"', '', g_str)

            return g_str
        else:
            print(f"No <g> element found in {file_path}")
            return None
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

static_output_height = {
    'girl': 390,
    'boy': 400,
    'sportsboy': 405
}

# Define static canvas sizes
static_canvas_sizes = {
    'full': {
        'girl': "0 0 1072 2200",    # maximum[190, 390]
        'boy': "0 0 1255 2330",      # maximum[222, 400]
        'sportsboy': "0 0 1300 2360"      # maximum[223, 405]
    },
    'half': {
        'girl': "0 0 1072 1100",    # maximum[300, 260]
        'boy': "0 0 1255 1165",      # maximum[300, 260]
        'sportsboy': "0 0 1300 1180"      # maximum[300, 260]
    }
}

static_body_type = {
    'boy': {'full': 'stand', 'half': 'half'},
    'girl': {'full': 'stand', 'half': 'half'},
    'sportsboy': {'full': 'standright', 'half': 'half'},
}

# Define static offsets for every body part
static_body_part_offsets = {
    'girl': {
        'head': (0, -860), # base body part(neutral), x_offset=0
        'left': (200, 265),
        'right': (-355, -565),
        'torso': (-40, -445),
        'leg': (70, 343)
    },
    'boy': {
        'head': (0, -904), # base body part(neutral), x_offset=0
        'left': (368, -547),
        'right': (-250, -402),
        'torso': (-5, -433),
        'leg': (-25, 446)
    },
    'sportsboy': {
        'head': (0, -931), # base body part(laugh), x_offset=0
        'left': (352, -555),
        'right': (-235, -424),
        'torso': (14, -431),
        'leg': (17, 422)
    }
}

# Define static offsets for every body part
static_body_part_gesture_offsets = {
    'girl': {
        'head-embarrassed': (5, 11),
        'head-happy': (-12, 9),
        'head-laugh': (-23, 13),
        'head-blissful': (-25, 13),
        'head-blinkgrin': (0, 14),
        'head-neutral': (-12, 10),
        'head-neutral-crown': (-12, 10),
        'head-questioning': (-12, 10),
        'head-playful': (0, 14),
        'head-shy': (5, 15),
        'head-smug': (5, 14),
        'head-surprised': (-13, 11),
        'left-arm-fistup': (18, -887),
        'left-arm-handonhip': (-30, -655),
        'left-arm-open': (460, -923),
        'left-arm-straight': (905, -563),
        'right-arm-fistup': (40, -170),
        'right-arm-handonhip': (60, 160),
        'right-arm-open': (456, -304),
        'right-arm-thumbup': (10, -50),
        'torso-shoulder-flat': (0, 0), # base posture
        'torso-shoulder-up': (0, -10),
        'leg-1forward': (-145, 10),
        'leg-apart': (-166, 21),
        'leg-crossing': (-130, 25),
        'leg-straight': (-145, 44)
    },
    'boy': {
        'head-blinkgrin': (-5, 0),
        'head-happy': (-2, 0),
        'head-playful': (-5, 0),
        'head-smug': (-2, 0),
        'left-arm-fistup': (-68, -154),
        'left-arm-thumbup': (-0, -0),
        'left-arm-open': (58.5, 171),
        'left-arm-straight': (-130, 305),
        'right-arm-fistup': (-70, -355),
        'right-arm-handonhip': (0, 0),
        'right-arm-open': (-180, 237),
        'right-arm-straight': (0, 170),
        'torso-shoulder-flat': (0, 0), # base posture
        'torso-shoulder-tilt': (-15, 0),
        'leg-1forward': (55, 37),
        'leg-apart': (61, -11),
        'leg-crossing': (-13, 10),
        'leg-straight': (-10, 0)
    },
    'sportsboy': {
        'left-arm-fistup': (-28, -229),
        'left-arm-handonhip': (-80, 110),
        'left-arm-holding-basketball': (-100, 180),
        'left-arm-thumbup': (-0, -0),
        'left-arm-open': (63, 167),
        'left-arm-straight': (-85, 275),
        'right-arm-fistup': (-70, -305),
        'right-arm-handonhip': (0, 0),
        'right-arm-open': (-140, 219),
        'right-arm-straight': (0, 127),
        'torso-shoulder-flat': (0, 0), # base posture
        'torso-shoulder-tilt': (-1, 0),
        'leg-1forward': (3, -3),
        'leg-apart': (-49, -9),
        'leg-crossing': (-28, 7),
        'leg-stepping': (10, 0) # base posture
    }
}

static_type_offsets = {
    'full': (0, 0),
    'half': {
        'girl': (40, 590),
        'boy': (55, 550),
        'sportsboy': (30, 600)
    }
}

static_overall_transforms = {
    'half': {
        'boy': 'translate(33 0) matrix(-1 0 0 1 {view_width} {view_height})',
        'girl': 'translate(80 551)',
        'sportsboy': 'translate(25 601)'
    }
}

combination_rules = {
    'girl': [
        {
            'input': 'torso-shoulder-flat'
            ,'allow': {
                'left-arm': ['handonhip', 'open', 'straight'],
                'right-arm': ['finger1up', 'handonhip', 'open', 'thumbup']
            }
        },
        {
            'input': 'torso-shoulder-open'
            ,'allow': {
                'left-arm': ['handonhip', 'open', 'straight'],
                'right-arm': ['finger1up', 'handonhip', 'open', 'thumbup']
            }
        },
        {
            'input': 'torso-shoulder-up'
            ,'allow': {
                'left-arm': ['fistup'],
                'right-arm': ['fistup'],
                'head': ['blinkgrin', 'blissful', 'laugh'],
                'leg': ['apart']
            }
        },
        {
            'input': 'left-arm-handonhip'
            ,'avoid': {
                'head': ['blissful', 'shy']
            }
        },
        {
            'input': 'left-arm-straight'
            ,'avoid': {
                'right-arm': ['finger1up', 'thumbup']
            }
        },
        {
            'input': 'right-arm-handonhip'
            ,'avoid': {
                'head': ['blissful', 'embarrassed', 'questioning', 'shy', 'surprised']
            }
        },
        {
            'input': 'right-arm-finger1up'
            ,'avoid': {
                'head': ['blissful', 'embarrassed', 'laugh', 'shy', 'surprised']
            }
        },
        {
            'input': 'right-arm-thumbup'
            ,'allow': {
                'head': ['blinkgrin', 'neutral', 'laugh', 'playful', 'happy', 'happy-olive']
            }
        },
        {
            'input': 'leg-1forward'
            ,'avoid': {
                'head': ['embarrassed', 'happy', 'happy-olive', 'neutral', 'questioning', 'shy', 'surprised']
            }
        },
        {
            'input': 'leg-crossing'
            ,'avoid': {
                'head': ['embarrassed', 'happy', 'happy-olive', 'neutral', 'questioning', 'shy', 'surprised']
            }
        },
        {
            'input': 'leg-stepping'
            ,'avoid': {
                'head': ['embarrassed', 'happy', 'happy-olive', 'neutral', 'questioning', 'shy', 'surprised']
            }
        },
        {
            'input': 'leg-straight'
            ,'allow': {
                'head': ['embarrassed', 'happy', 'happy-olive', 'neutral', 'questioning', 'shy', 'surprised']
            }
        },
        {
            'input': 'leg-apart'
            ,'avoid': {
                'head': ['embarrassed', 'happy', 'happy-olive', 'neutral', 'questioning', 'shy', 'surprised']
            }
        },
        # 可以添加更多的组合规则
    ],
    'boy': [
        {
            'input': 'torso-shoulder-flat'
            ,'allow': {
                'left-arm': ['thumbup', 'finger1up', 'straight', 'open'],
                'right-arm': ['handonhip', 'open', 'straight']
            }
            # ,'avoid': {}
        },
        {
            'input': 'torso-shoulder-tilt'
            ,'allow': {
                'left-arm': ['fistup'],
                'right-arm': ['handonhip', 'open', 'straight'],
                'head': ['blinkgrin', 'blissful', 'laugh', 'playful', 'smug']
            }
        },
        {
            'input': 'torso-shoulder-up'
            ,'allow': {
                'left-arm': ['fistup'],
                'right-arm': ['fistup'],
                'head': ['blinkgrin', 'blissful', 'laugh']
            }
        },
        {
            'input': 'left-arm-finger1up'
            ,'avoid': {
                'head': ['embarrassed', 'shy', 'surprised', 'worried', 'blissful', 'laugh', 'questioning']
            }
        },
        {
            'input': 'left-arm-fistup'
            ,'avoid': {
                'head': ['blissful', 'neutral', 'neutral-crown', 'laugh'],
                'right-arm': ['open']
            }
        },
        {
            'input': 'left-arm-thumbup'
            ,'allow': {
                'head': ['blinkgrin', 'neutral', 'neutral-crown', 'laugh', 'playful', 'happy']
            }
            ,'avoid': {
                'right-arm': ['open']
            }
        },
        {
            'input': 'left-arm-straight'
            ,'avoid': {
                'head': ['blinkgrin', 'neutral', 'neutral-crown', 'laugh', 'playful', 'happy']
            }
        },
        {
            'input': 'leg-1forward'
            ,'allow': {
                'head': ['blissful', 'laugh', 'neutral', 'neutral-crown']
            }
        },
        {
            'input': 'leg-crossing'
            ,'allow': {
                'head': ['blinkgrin', 'happy', 'playful']
            }
        },
        {
            'input': 'leg-straight'
            ,'allow': {
                'head': ['embarrassed', 'happy', 'neutral', 'neutral-crown', 'questioning', 'shy', 'surprised', 'worried']
            }
        },
        {
            'input': 'leg-apart'
            ,'avoid': {
                'head': ['embarrassed', 'happy', 'neutral', 'neutral-crown', 'questioning', 'shy', 'surprised', 'worried']
            }
        },
        # 可以添加更多的组合规则
    ],
    'sportsboy': [
        {
            'input': 'head-crying'
            ,'allow': {
                'leg': ['apart']
            }
        },
        {
            'input': 'head-worried'
            ,'allow': {
                'leg': ['apart']
            }
        },
        {
            'input': 'torso-shoulder-flat'
            ,'allow': {
                'left-arm': ['thumbup', 'finger1up', 'straight', 'open'],
                'right-arm': ['handonhip', 'open', 'straight']
            }
            # ,'avoid': {}
        },
        {
            'input': 'torso-shoulder-tilt'
            ,'allow': {
                'left-arm': ['handonhip', 'open', 'straight', 'holding-basketball'],
                'right-arm': ['fistup'],
                'head': ['blinkgrin', 'blissful', 'laugh', 'playful', 'smug']
            }
        },
        {
            'input': 'torso-shoulder-up'
            ,'allow': {
                'left-arm': ['fistup'],
                'right-arm': ['fistup'],
                'head': ['blinkgrin', 'blissful', 'laugh', 'playful'],
                'leg': ['apart']
            }
        },
        {
            'input': 'left-arm-open'
            ,'avoid': {
                'right-arm': ['straight']
            }
        },
        {
            'input': 'right-arm-fistup'
            ,'avoid': {
                'head': ['blissful', 'laugh'],
                'left-arm': ['open']
            }
        },
        {
            'input': 'right-arm-thumbup'
            ,'allow': {
                'head': ['blinkgrin', 'laugh', 'playful', 'happy']
            }
        },
        {
            'input': 'right-arm-finger1up'
            ,'avoid': {
                'head': ['embarrassed', 'shy', 'surprised', 'worried', 'crying']
            }
        },
        {
            'input': 'leg-1forward'
            ,'avoid': {
                'head': ['embarrassed', 'happy', 'shy', 'surprised', 'worried', 'crying']
            }
        },
        {
            'input': 'leg-crossing'
            ,'avoid': {
                'head': ['embarrassed', 'happy', 'shy', 'surprised', 'worried', 'crying']
            }
        },
        {
            'input': 'leg-stepping'
            ,'allow': {
                'head': ['embarrassed', 'happy', 'questioning', 'shy', 'surprised', 'worried', 'crying']
            }
        },
        {
            'input': 'leg-apart'
            ,'avoid': {
                'head': ['embarrassed', 'happy', 'questioning', 'shy', 'surprised', 'worried', 'crying']
            }
        },
        # 可以添加更多的组合规则
    ],
    "half": [
        {
            'input': 'head'
            ,'avoid': {
                'head': ['worried', 'crying', 'surprised', 'embarrassed', 'shy']
            }
        }
    ]
}

def is_valid_combination(character_name, type, input_pose, other_poses, accessory=None):
    # Check accessory requirement for head part
    if accessory and 'head' in other_poses:
        if accessory not in other_poses['head']:
            # print(f'Accessory check failed: {accessory} not found in {other_poses["head"]}')
            return False
    
    for rule in combination_rules.get(character_name, []):
        # print('Checking rules for input:', rule['input'], ', gesture:', input_pose)
        if rule['input'] == input_pose:
            # check allowed combinations
            if rule.get('allow', None):
                for part, poses in rule['allow'].items():
                    if part in other_poses and other_poses[part] not in poses:
                        # print('<not in> allow rule:', character_name, part, other_poses[part])
                        return False
            
            # check avoided combinations
            if rule.get('avoid', None):
                for part, poses in rule['avoid'].items():
                    if part in other_poses and other_poses[part] in poses:
                        # print('<in> avoid rule:', character_name, part, other_poses[part])
                        return False
    
    for rule in combination_rules.get(type, []):
        full_poses = other_poses.copy()
        full_poses[input_pose] = input_pose
        if rule['input'] in input_pose:
            # check allowed combinations
            if rule.get('allow', None):
                for part, poses in rule['allow'].items():
                    if part in full_poses and full_poses[part] not in poses:
                        # print('<not in> allow rule:', character_name, part, other_poses[part])
                        return False

            if rule.get('avoid', None):
                for part, poses in rule['avoid'].items():
                    if part in full_poses and full_poses[part] in poses:
                        # print('<in> avoid rule:', character_name, part, other_poses[part])
                        return False
            
    return True

def generate_combinations(input_folder, type="full", character_name="character", output_folder=None, namespace=True, accessory=None, verbose=False):
    """
    Generate all possible combinations of body parts into full body SVG files.
    
    Args:
        input_folder (str): Path to the folder containing individual body part SVG files
        character_name (str): Prefix to use for generated files
        output_folder (str): Optional separate output folder path
        namespace (bool): Whether to use XML namespace
        accessory (str): Optional accessory requirement for head part (e.g., 'crown')
        verbose (bool): Whether to print detailed information about each combination
    """
    if output_folder is None:
        output_folder = input_folder
    os.makedirs(output_folder, exist_ok=True)

    view_box = static_canvas_sizes.get(type, {}).get(character_name, "0 0 0 0")
    
    # Get all body parts organized by type
    parts_dict = get_body_parts_from_files(input_folder, prefix=character_name)
    
    # Verify we have all required body parts
    required_parts = []
    if type == "full":
        required_parts = ['head', 'left-arm', 'right-arm', 'torso', 'leg']
    elif type == "half":
        required_parts = ['head', 'left-arm', 'right-arm', 'torso']
    missing_parts = required_parts - parts_dict.keys()
    if missing_parts:
        print(f"Error: Missing required body parts: {missing_parts}")
        return
    
    # SVG template for full body
    svg_template = '''<svg viewBox="''' \
                    +view_box+          \
                    '''" xmlns="http://www.w3.org/2000/svg" overflow="hidden">
{}
</svg>'''
    
    # Generate all possible combinations
    combinations = product(
        *[parts_dict[body_part] for body_part in required_parts]
    )

    count = 0
    for combination_set in combinations:
        # whether combination is valid
        is_combination_valid = True

        body_parts = {
            'head': combination_set[required_parts.index('head')][1].split('-', 1)[1],
            'torso': combination_set[required_parts.index('torso')][1].split('-', 1)[1],
            'left-arm': combination_set[required_parts.index('left-arm')][1].split('-', 2)[2],
            'right-arm': combination_set[required_parts.index('right-arm')][1].split('-', 2)[2],
        }
        if type == "full":
            body_parts['leg'] = combination_set[required_parts.index('leg')][1].split('-', 1)[1]

        # interate on body parts to check validity of combination
        for part, pose in body_parts.items():
            if not is_valid_combination(character_name, type, f"{part}-{pose}", body_parts, accessory):
                is_combination_valid = False
                break

        # continue if combination is not valid
        if not is_combination_valid:
            # print('not is_combination_valid')
            continue

        # Print head file information for valid combinations if verbose mode is enabled
        if verbose:
            head_file_path = combination_set[required_parts.index('head')][0]
            head_filename = os.path.basename(head_file_path)
            print(f"Valid combination #{count + 1}: Head file = {head_filename}, Head type = {body_parts['head']}")

        # generate output file name for character
        filename = f"{character_name}"\
                    + f"-{static_body_type.get(character_name, {}).get(type, 'stand')}" \
                    + f"-left-{body_parts.get('left-arm', '')}" \
                    + f"-right-{body_parts.get('right-arm', '')}" \
                    + f"-torso-{body_parts.get('torso', '')}"\
                    + (f"-leg-{body_parts.get('leg')}" if body_parts.get("leg", None) is not None else "") \
                    + f"-{body_parts.get('head', '')}" \
                    + "-anime.svg"
        output_path = os.path.join(output_folder, filename)
        
        # Extract and combine g elements
        parts_content = []
        if character_name == "girl":
            part_name_list = ['head', 'right-arm', 'torso', 'leg', 'left-arm']
        elif character_name == "sportsboy":
            part_name_list = ['head', 'right-arm', 'leg', 'torso', 'left-arm']
        else: #boy
            part_name_list = ['head', 'left-arm', 'torso', 'leg', 'right-arm']

        part_list = []
        for part_name in part_name_list:
            if part_name in body_parts:
                part_list.append(combination_set[required_parts.index(part_name)][0])
        # print(f"part_list: {part_list}")

        for part_file in part_list:
            part_filename = os.path.basename(part_file)
            # combination_set[required_parts.index('head')][0]
            part_filename_without_extension = os.path.splitext(part_filename)[0]

            # print(part_filename, part_filename_without_extension.split('-', 1))

            part_x_offset, part_y_offset = static_body_part_offsets \
                                                .get(character_name, {}) \
                                                .get(part_filename_without_extension.split('-')[1], (0, 0))
            gesture_x_offset, gesture_y_offset = static_body_part_gesture_offsets \
                                                .get(character_name, {}) \
                                                .get(part_filename_without_extension.split('-', 1)[1], (0, 0))
            type_x_offset, type_y_offset = static_type_offsets.get(type) \
                if type in static_type_offsets and isinstance(static_type_offsets.get(type), tuple) \
                else static_type_offsets.get(character_name, (0, 0)) \

            content = extract_g_content(
                part_file, 
                ext_width = int(view_box.split()[2]),
                ext_height = int(view_box.split()[3]),
                part_x_offset = part_x_offset+gesture_x_offset+type_x_offset,
                part_y_offset = part_y_offset+gesture_y_offset+type_y_offset,
                namespace=namespace
            )
            if content:
                parts_content.append(content)
            else:
                print(f"Skipping combination due to error in {part_file}")
                break
        
        if len(parts_content) == len(required_parts):  # All parts were successfully extracted
            # Combine all parts into final SVG
            if type in static_overall_transforms \
                and character_name in static_overall_transforms[type]:
                parts_content.insert(0, f'<g transform="{static_overall_transforms[type][character_name]}">'\
                                     .replace('{view_width}', str(view_box.split()[2]))\
                                     .replace('{view_height}', str(int(view_box.split()[3])/2)))
                parts_content.append('</g>')
            full_svg = svg_template.format('\n'.join(parts_content))
            
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_svg)
                count += 1
                if count % 100 == 0:  # Progress report every 100 files
                    print(f"Generated {count} {type} body combinations...")
            except Exception as e:
                print(f"Error writing {output_path}: {str(e)}")
    
    print(f"Successfully generated {count} {type} body combinations")

def calculate_new_size(width, height, target_height):
    """
    Calculate new dimensions maintaining aspect ratio based on target height.
    
    Args:
        width (float): Original width
        height (float): Original height
        target_height (float): Desired height
        
    Returns:
        tuple: (new_width, new_height)
    """
    aspect_ratio = width / height
    new_height = target_height
    new_width = round(target_height * aspect_ratio)
    return [new_width, new_height]

def get_svg_dimensions(file_path):
    """
    Extract width and height from SVG file.
    
    Args:
        file_path (str): Path to SVG file
        
    Returns:
        tuple: (width, height) or None if not found
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Try to get width and height from attributes
        width = root.get('width')
        height = root.get('height')
        
        # If not found, try viewBox
        if not width or not height:
            viewbox = root.get('viewBox')
            if viewbox:
                parts = viewbox.split()
                if len(parts) == 4:
                    width = float(parts[2])
                    height = float(parts[3])
                    return width, height
        
        # Convert string dimensions to float
        if width and height:
            return float(width), float(height)
            
    except Exception as e:
        print(f"Error reading dimensions from {file_path}: {str(e)}")
    
    return None, None

def build_character_tsx(input_folder, character_name="character", output_folder=None):
    """
    Build character TSX file with figure dimensions.
    
    Args:
        input_folder (str): Path to the folder containing SVG files
        character_name (str): Character name prefix
        output_folder (str): Optional output folder path
    """
    if output_folder is None:
        output_folder = input_folder
    os.makedirs(output_folder, exist_ok=True)
    
    target_height = static_output_height.get(character_name)
    if not target_height:
        print(f"Error: No target height defined for character '{character_name}'")
        return
    
    figures = []
    
    # Process each SVG file
    for filename in os.listdir(input_folder):
        if not (filename.endswith('.svg') and filename.startswith(character_name)):
            continue
        
        file_path = os.path.join(input_folder, filename)
        width, height = get_svg_dimensions(file_path)
        
        if width and height:
            new_size = calculate_new_size(width, height, target_height)
            figure_data = {
                "source": f"/story/characters/figures/{filename}",
                "size": new_size,
                "type": "svg"
            }
            figures.append(figure_data)
        else:
            print(f"Warning: Could not process {filename}")
    
    # Create character data structure
    character_data = {
        character_name: {
            "figure": figures
        }
    }
    
    # Write to TSX file
    output_path = os.path.join(output_folder, f"{character_name}.tsx")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("export default ")
            json.dump(character_data, f, indent=2)
        print(f"Successfully generated {output_path}")
    except Exception as e:
        print(f"Error writing TSX file: {str(e)}")

def extract_paths(root):
    """
    提取SVG中的所有路径元素
    
    Args:
        root: SVG的根元素
        
    Returns:
        list: 路径元素列表的深拷贝
    """
    paths = []
    for path in root.findall('.//path') + root.findall('.//{http://www.w3.org/2000/svg}path'):
        # 创建新的path元素
        new_path = ET.Element('path')
        # 复制所有属性
        for key, value in path.attrib.items():
            new_path.set(key, value)
        paths.append(new_path)
    return paths

def apply_paths(input_folder, pattern, layer_position='top'):
    """
    将源SVG文件中的路径应用到匹配模式的所有文件上
    
    Args:
        input_folder (str): 源SVG文件路径
        pattern (str): 目标文件匹配模
        layer_position (str): 'top' 或 'bottom'，决定新路径添加的位置
    """
    # 解析源文件
    source_tree = ET.parse(input_folder)
    source_root = source_tree.getroot()
    
    # 提取路径
    paths = extract_paths(source_root)
    print(f"Extracted {len(paths)} paths from {input_folder}")
    
    # 获取目标文件列表
    if isinstance(pattern, list):  # 如果pattern是文件列表
        target_files = pattern
    else:  # 如果pattern是通配符模式
        target_files = glob.glob(pattern)
        
    if not target_files:
        print(f"No files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(target_files)} matching files")
    print(f"Applying paths at {layer_position} layer")
    
    # 处理每个目标文件
    for target_file in target_files:
        try:
            # 跳过源文件
            if os.path.abspath(target_file) == os.path.abspath(input_folder):
                print(f"Skipping source file: {target_file}")
                continue
                
            print(f"Processing {target_file}...")
            
            # 解析目标文件
            tree = ET.parse(target_file)
            root = tree.getroot()
            
            # 找到SVG元素可能有命名空间）
            svg = root
            if not (svg.tag.endswith('svg') or svg.tag == 'svg'):
                svg = root.find('.//{http://www.w3.org/2000/svg}svg') or root.find('.//svg')
                if svg is None:
                    print(f"Warning: No SVG element found in {target_file}")
                    continue
            
            # 添加新路径到目标文件
            for path in paths:
                if layer_position == 'bottom':
                    # 在开头插入路
                    svg.insert(0, ET.fromstring(ET.tostring(path)))
                else:  # 'top'
                    # 在末尾添加路径
                    svg.append(ET.fromstring(ET.tostring(path)))
            
            # 保存修改后的文件
            with open(target_file, 'w', encoding='utf-8') as f:
                xml_str = ET.tostring(root, encoding='unicode')
                xml_str = xml_str.replace('ns0:', '').replace(':ns0', '')
                f.write(xml_str)
            
            print(f"Successfully processed: {target_file}")
            
        except Exception as e:
            print(f"Failed to process {target_file}: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Process SVG files - set class attributes and generate combinations or tsx source file. Apply paths from source SVG to target SVGs.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  setclass - Set class attributes for individual SVG files
  combine  - Generate all possible full body combinations
  build    - Generate character TSX file with figure dimensions
  apply    - Apply paths from source SVG to target SVGs

Examples:
  # Set class attributes for SVG files:
  python svg_character_builder.py setclass /path/to/svg/folder --character-name boy
  
  # Generate full body combinations:
  python svg_character_builder.py combine /path/to/svg/folder
  python svg_character_builder.py combine /path/to/svg/folder --character-name girl --output-folder /path/to/output
  python svg_character_builder.py combine /path/to/svg/folder --character-name boy --accessory crown
  python svg_character_builder.py combine /path/to/svg/folder --character-name boy --accessory crown --verbose

  # Generate character TSX file:
  python svg_character_builder.py build /path/to/svg/folder --character-name girl --output-folder /path/to/output
    File naming convention for setclass:
    - Format: prefix-bodypart-posture.svg
    - Valid body parts: head, torso, leg, left-arm, right-arm
    - Special file: mat.svg
    
    Example filenames and resulting classes:
    - girl-head-happy.svg -> class="head-happy"
    - boy-left-arm-raised.svg -> class="left-arm-raised"
    - character-torso-shoulder-open.svg -> class="torso-shoulder-open"
    - girl-leg-1forward.svg -> class="leg-1forward"
    - girl-left-arm-khoikhoi-shield.svg -> class="left-arm-khoikhoi-shield"
    - mat.svg -> class="mat"
            
    Output format for combine:
    - Generated filename: <character>-left-<left-arm>-right-<right-arm>-torso-<torso>-leg-<leg>-<head>.svg
    - SVG viewBox: 0 0 1240 2200
    - Accessory filtering: Use --accessory to filter combinations by head accessory (e.g., --accessory crown will only generate combinations with head parts containing 'crown')

  # Apply paths from source SVG to target SVGs:
  python svg_character_builder.py apply source.svg "target/*.svg" --position top
        """
    )
    
    parser.add_argument(
        'command',
        choices=['setclass', 'combine', 'build', 'apply'],
        help='Command to execute (setclass: set class attributes, combine: generate combinations, build: generate TSX file, apply: apply paths from source SVG to target SVGs)'
    )
    
    parser.add_argument(
        '--type',
        choices=['full', 'half'],
        default='full',
        help='Type of combinations to generate (full: full body, half: half body)'
    )

    parser.add_argument(
        'input_folder',
        help='Path to the folder containing SVG files'
    )
    
    # Optional arguments for combine command
    parser.add_argument(
        '--character-name',
        default='character',
        help='Prefix to filter input and use for generated full body files (default: character)'
    )
    
    parser.add_argument(
        '--output-folder',
        help='Optional separate output folder for generated files'
    )

    # Arguments for apply command
    parser.add_argument(
        '--position',
        choices=['top', 'bottom'],
        default='top',
        help='Position to add paths (top or bottom) for apply command'
    )
    
    # Argument for accessory requirement in combine command
    parser.add_argument(
        '--accessory',
        help='Optional accessory requirement for head part in combine command (e.g., crown)'
    )
    
    # Argument for verbose output in combine command
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed information about each combination in combine command'
    )

    args = parser.parse_args()

    # Validate folder path
    if not os.path.exists(args.input_folder):
        print(f"Error: Folder '{args.input_folder}' does not exist")
        sys.exit(1)

    if not os.path.isdir(args.input_folder):
        print(f"Error: '{args.input_folder}' is not a directory")
        sys.exit(1)

    # Execute requested command
    if args.command == 'setclass':
        process_svg_files(
            args.input_folder,
            character_name=args.character_name
        )
        print("Class setting complete!")
        
    elif args.command == 'combine':
        generate_combinations(
            input_folder=args.input_folder,
            type=args.type,
            character_name=args.character_name,
            output_folder=args.output_folder,
            namespace=True,
            accessory=args.accessory,
            verbose=args.verbose
        )
        print("Combination generation complete!")
        
    elif args.command == 'build':
        build_character_tsx(
            input_folder=args.input_folder,
            character_name=args.character_name,
            output_folder=args.output_folder
        )
        print("TSX file generation complete!")
        
    elif args.command == 'apply':
        # For apply command, input_folder is the source SVG file
        input_folder = args.input_folder
        if not os.path.isfile(input_folder):
            print(f"Error: Source file '{input_folder}' does not exist")
            sys.exit(1)
            
        # Get target pattern from remaining arguments
        target_pattern = args.output_folder if args.output_folder else "*.svg"
        
        apply_paths(
            input_folder, target_pattern, args.position)
        print("Path application complete!")

if __name__ == "__main__":
    main()

