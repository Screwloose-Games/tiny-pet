import os
import numpy as np
import pyrender
import sys
import trimesh

# from pyrender.constants import RenderFlags
from pyrender import Viewer



def main():
    if len(sys.argv) < 2:
        print("Usage: python preview_3d_asset.py <path_to_gltf_file>")
        sys.exit(1)

    gltf_path = sys.argv[1]
    if not os.path.isfile(gltf_path):
        print(f"File not found: {gltf_path}")
        sys.exit(1)

    # Load the GLTF file
    scene = pyrender.Scene.from_trimesh_scene(trimesh.load(gltf_path))

    # Create a viewer to display the scene
    pyrender.Viewer(scene, render_flags={
        'face_normals': True,
        'all_solid': True
        }, 
        viewer_flags={
        'show_world_axis': True, 
        'show_mesh_axes': True, 
        'use_raymond_lighting': True,
        'rotate_axis': np.array([0.0, 0.0, 1.0]),
        'view_center': [0,0,0]
        }, 
        run_in_thread=False)
    while True:
        # Keep the viewer running
        pass
    # The viewer will block until the window is closed


if __name__ == "__main__":
    main()
