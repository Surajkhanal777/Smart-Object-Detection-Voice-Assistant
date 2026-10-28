
"""
Generating natural-language descriptions for object detection.
Converting detected objects into human-readable scene descriptions.
"""

# Importing Counter for counting occurrences of detected object labels
from collections import Counter


def generate_description(detections):
    """
    Generating a natural-language description from detected objects.

    Args:
        detections (list): Receiving detection dictionaries containing 'label' and 'position'.

    Returns:
        str: Returning a human-readable description of the detected scene.
    """

    # Checking whether the detection list is empty
    if not detections:
        # Returning a message indicating that no objects were detected
        return "No objects detected in the frame."

    # Counting the occurrences of each detected object label
    object_counts = Counter([det['label'] for det in detections])

    # Initializing groups for organizing objects by their positions
    position_groups = {'left': [], 'center': [], 'right': []}

    # Grouping detected object labels according to their positions
    for det in detections:
        position_groups[det['position']].append(det['label'])

    # Initializing a list for assembling the scene description
    description_parts = []

    # Counting the total number of detected objects
    total_objects = len(detections)

    # Checking whether exactly one object has been detected
    if total_objects == 1:
        # Appending a singular object-count statement
        description_parts.append("I see 1 object:")
    else:
        # Appending a plural object-count statement
        description_parts.append(f"I see {total_objects} objects:")

    # Initializing a list for collecting unique object descriptions
    object_list = []

    # Iterating through object labels ordered by their occurrence counts
    for obj, count in object_counts.most_common():

        # Checking whether an object appears only once
        if count == 1:
            # Appending a singular object description
            object_list.append(f"a {obj}")
        else:
            # Appending a plural object description with its count
            object_list.append(f"{count} {obj}s")

    # Checking whether only one unique object label exists
    if len(object_list) == 1:
        # Appending the single object description
        description_parts.append(object_list[0])

    # Checking whether exactly two unique object labels exist
    elif len(object_list) == 2:
        # Joining the two object descriptions using "and"
        description_parts.append(f"{object_list[0]} and {object_list[1]}")

    else:
        # Joining multiple object descriptions using commas and a final "and"
        description_parts.append(", ".join(object_list[:-1]) + f", and {object_list[-1]}")

    # Initializing a list for collecting positional descriptions
    position_desc = []

    # Iterating through the supported positions from left to right
    for pos in ['left', 'center', 'right']:

        # Checking whether any objects have been detected in the current position
        if position_groups[pos]:

            # Collecting distinct object labels appearing in the current position
            unique_objs = list(set(position_groups[pos]))

            # Checking whether one unique object type appears in this position
            if len(unique_objs) == 1:
                # Appending a description identifying the object's position
                position_desc.append(f"{unique_objs[0]} on the {pos}")

            # Checking whether two unique object types appear in this position
            elif len(unique_objs) == 2:
                # Appending a combined positional description
                position_desc.append(f"{unique_objs[0]} and {unique_objs[1]} on the {pos}")

    # Checking whether positional descriptions exist and number no more than two
    if position_desc and len(position_desc) <= 2:

        # Appending positional information to the main scene description
        description_parts.append("with " + ", ".join(position_desc))

    # Combining all description components and returning the completed sentence
    return " ".join(description_parts) + "."
