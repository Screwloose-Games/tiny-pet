import numpy as np
from enum import Enum
import trimesh
from trimesh.transformations import euler_matrix, translation_matrix
from numpy import float64, ndarray

CAMERA_DISTANCE_PADDING = 0.5

class CameraPoseDirection(Enum):
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

def get_camera_pose_direction_from_matrix(camera_pose: np.ndarray) -> CameraPoseDirection:
    """
    Determines the camera pose direction based on the camera pose matrix.
    """
    # Extract the rotation part of the camera pose
    rotation_matrix = camera_pose[:3, :3]
    # Check the direction of the camera
    if np.allclose(rotation_matrix[:, 2], [0, 0, -1]):
        return CameraPoseDirection.FRONT
    elif np.allclose(rotation_matrix[:, 2], [0, 0, 1]):
        return CameraPoseDirection.BACK
    elif np.allclose(rotation_matrix[:, 0], [-1, 0, 0]):
        return CameraPoseDirection.LEFT
    elif np.allclose(rotation_matrix[:, 0], [1, 0, 0]):
        return CameraPoseDirection.RIGHT
    elif np.allclose(rotation_matrix[:, 1], [0, -1, 0]):
        return CameraPoseDirection.BOTTOM
    elif np.allclose(rotation_matrix[:, 1], [0, 1, 0]):
        return CameraPoseDirection.TOP
    else:
        raise ValueError("Unknown camera pose direction")

def get_camera_pose_from_direction(direction: CameraPoseDirection, scene_bounds: ndarray[float64]) -> np.ndarray:
    """
    Returns a camera pose matrix based on the specified direction.
    """
    bounds = scene_bounds
    center = (bounds[0] + bounds[1]) / 2

    match direction:
        case CameraPoseDirection.FRONT:
            translation = translation_matrix([center[0], center[1], bounds[1][2] + CAMERA_DISTANCE_PADDING])
            rotation = euler_matrix(np.pi, 0, 0)
        case CameraPoseDirection.BACK:
            translation = translation_matrix([center[0], center[1], bounds[0][2] - CAMERA_DISTANCE_PADDING])
            rotation = euler_matrix(0, 0, np.pi)
        case CameraPoseDirection.LEFT:
            translation = translation_matrix([bounds[0][0] - CAMERA_DISTANCE_PADDING, center[1], center[2]])
            rotation = euler_matrix(0, np.pi / 2, 0)
        case CameraPoseDirection.RIGHT:
            translation = translation_matrix([bounds[1][0] + CAMERA_DISTANCE_PADDING, center[1], center[2]])
            rotation = euler_matrix(0, -np.pi / 2, 0)
        case CameraPoseDirection.TOP:
            translation = translation_matrix([center[0], center[1], bounds[1][2] + CAMERA_DISTANCE_PADDING])
            rotation = euler_matrix(-np.pi / 2, 0, 0)
        case CameraPoseDirection.BOTTOM:
            translation = translation_matrix([center[0], center[1], bounds[0][2] - CAMERA_DISTANCE_PADDING])
            rotation = euler_matrix(np.pi / 2, 0, 0)
        case _:
            raise ValueError("Unknown camera pose direction")

    return translation @ rotation

def get_top_down_camera_pose(scene: trimesh.Scene) -> np.ndarray:
    """
    Returns a camera pose for a top-down view of the scene.
    The camera looks down the -Z axis from above the model.
    """

    bounds: ndarray[float64] = scene.bounds
    center = (bounds[0] + bounds[1]) / 2
    center_x = center[0]
    center_y = center[2]
    ending_bound = bounds[1]
    ending_bound_z = ending_bound[1]
    rotation = euler_matrix(-np.pi/2, 0, 0)  
    translation = translation_matrix([center_x, ending_bound_z + CAMERA_DISTANCE_PADDING, center_y])
    camera_pose = translation @ rotation
    return camera_pose

def get_right_side_camera_pose(scene: trimesh.Scene) -> np.ndarray:
    """
    Returns a camera pose for a top-down view of the scene.
    The camera looks down the -Z axis from above the model.
    """
    bounds = scene.bounds
    center = (bounds[0] + bounds[1]) / 2

    center_z = center[1]
    center_y = center[2]

    ending_bound = bounds[1]
    ending_bound_x = ending_bound[0]

    rotation = euler_matrix(0, - np.pi / 2, 0)
    translation = translation_matrix([-ending_bound_x - CAMERA_DISTANCE_PADDING, center_z, center_y])
    camera_pose = translation @ rotation

    return camera_pose

def get_front_camera_pose(scene: trimesh.Scene) -> np.ndarray:
    """
    Returns a camera pose for a top-down view of the scene.
    The camera looks down the -Z axis from above the model.
    """
    bounds = scene.bounds
    center = (bounds[0] + bounds[1]) / 2

    center_x = center[0]
    center_z = center[1]

    ending_bound = bounds[1]

    ending_bound_y = ending_bound[2]

    translation = translation_matrix([center_x, center_z, ending_bound_y + CAMERA_DISTANCE_PADDING])

    return translation