"""
Natural Language Description Generator for Object Detection
Generates human-readable descriptions from detected objects.
"""

from collections import Counter


def generate_description(detections):
    """
    Generate a natural language description from detected objects.

    Args:
        detections (list): List of detection dictionaries with 'label' and 'position'.

    Returns:
        str: Natural language description of the scene.
    """
    if not detections:
        return "No objects detected in the frame."

    # Count objects by label
    object_counts = Counter([det['label'] for det in detections])

    # Group objects by position
    position_groups = {'left': [], 'center': [], 'right': []}
    for det in detections:
        position_groups[det['position']].append(det['label'])

    # Build description
    description_parts = []

    # Overall count
    total_objects = len(detections)
    if total_objects == 1:
        description_parts.append("I see 1 object:")
    else:
        description_parts.append(f"I see {total_objects} objects:")

    # List unique objects with counts
    object_list = []
    for obj, count in object_counts.most_common():
        if count == 1:
            object_list.append(f"a {obj}")
        else:
            object_list.append(f"{count} {obj}s")

    if len(object_list) == 1:
        description_parts.append(object_list[0])
    elif len(object_list) == 2:
        description_parts.append(f"{object_list[0]} and {object_list[1]}")
    else:
        description_parts.append(", ".join(object_list[:-1]) + f", and {object_list[-1]}")

    # Add positional information for variety
    position_desc = []
    for pos in ['left', 'center', 'right']:
        if position_groups[pos]:
            unique_objs = list(set(position_groups[pos]))
            if len(unique_objs) == 1:
                position_desc.append(f"{unique_objs[0]} on the {pos}")
            elif len(unique_objs) == 2:
                position_desc.append(f"{unique_objs[0]} and {unique_objs[1]} on the {pos}")

    if position_desc and len(position_desc) <= 2:
        description_parts.append("with " + ", ".join(position_desc))

    return " ".join(description_parts) + "."