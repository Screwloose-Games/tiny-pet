import os
import pyrender
import sys
import trimesh



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
    pyrender.Viewer(scene, use_raymond_lighting=True, run_in_thread=False)
    while True:
        # Keep the viewer running
        pass
    # The viewer will block until the window is closed


if __name__ == "__main__":
    main()
