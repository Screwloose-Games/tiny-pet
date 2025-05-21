import os
import glob
import json
import pytest
import subprocess
import trimesh
from pygltflib import GLTF2

VERTICES_LIMIT = 40000
TRIANGLE_LIMIT = 15000

from typing import List, TypedDict, Optional

class GLTF2Dict(TypedDict, total=False):
    accessors: List['Accessor']
    animations: List['Animation']
    asset: 'Asset'  # required if you want to enforce that manually
    bufferViews: List['BufferView']
    buffers: List['Buffer']
    cameras: List['Camera']
    extensionsUsed: List[str]
    extensionsRequired: List[str]
    images: List['Image']
    materials: List['Material']
    meshes: List['Mesh']
    nodes: List['Node']
    samplers: List['Sampler']
    scene: Optional[int]
    scenes: List['Scene']
    skins: List['Skin']
    textures: List['Texture']


def get_gltf_root_nodes(gltf: GLTF2Dict) -> list[dict]:
    """
    Returns the root node (as a dict) of the glTF model, or None if not found.
    """
    scenes = gltf.get('scenes', [])
    if not scenes:
        return []
    scene_index = gltf.get('scene', 0)
    if scene_index >= len(scenes):
        return []
    scene = scenes[scene_index]
    nodes = scene.get('nodes', [])
    if not nodes:
        return []
    nodes_list = gltf.get('nodes', [])
    node_indecies = nodes
    if not nodes_list:
        return []
    print(node_indecies)
    print(nodes_list)
    node_list = [nodes_list[node_index] for node_index in node_indecies]
    return node_list


def get_changed_gltf_files():
    """
    Return a list of .gltf files to check:
    - If CHANGED_GLTF_FILES env var is set, use those files (filtered for .gltf).
    - Otherwise, return all .gltf files tracked by git (not gitignored) with .gltf extension.
    """
    changed = os.environ.get('CHANGED_GLTF_FILES', '')
    if changed:
        # Accept comma or os.pathsep separated list
        if os.pathsep in changed:
            files = changed.split(os.pathsep)
        else:
            files = changed.split(',')
        gltf_files = [f for f in files if f.endswith('.gltf')]
        return gltf_files

    # Use git to list all tracked .gltf files (not gitignored)
    try:
        result = subprocess.run(
            ['git', 'ls-files', '*.gltf'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding='utf-8'
        )
        gltf_files = result.stdout.strip().split('\n') if result.stdout else []
        return [f for f in gltf_files if f]
    except Exception:
        # Fallback: all .gltf files anywhere
        return [os.path.relpath(f) for f in glob.glob('**/*.gltf', recursive=True)]

changed_gltf_files = get_changed_gltf_files()

if changed_gltf_files:
    gltf_files = changed_gltf_files
else:
    gltf_files = [
        os.path.relpath(f) for f in glob.glob('**/*.gltf', recursive=True)
    ]

@pytest.mark.parametrize('gltf_path', gltf_files)
def test_gltf_parse(gltf_path):
    """Test that each .gltf file can be parsed as JSON without error."""
    with open(gltf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, dict)

@pytest.mark.parametrize('gltf_path', gltf_files)
def test_gltf_no_camera(gltf_path):
    """Test that each .gltf file does NOT have a camera in the scene."""
    with open(gltf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cameras = data.get('cameras', [])
    camera_count = len(cameras)
    assert camera_count == 0, f"File {gltf_path} contains cameras: {','.join(camera.get('name') for camera in cameras)}"

@pytest.mark.parametrize('gltf_path', gltf_files)
def test_gltf_no_lights(gltf_path):
    """Test that each .gltf file does NOT have lights in the KHR_lights_punctual extension."""
    with open(gltf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    extensions = data.get('extensions', {})
    khr_lights = extensions.get('KHR_lights_punctual', {})
    lights = khr_lights.get('lights', [])
    light_count = len(lights)
    assert light_count == 0, f"File {gltf_path} contains lights: {','.join(light.get('name', '') for light in lights)}"

@pytest.mark.parametrize('gltf_path', gltf_files)
def test_gltf_vertex_count(gltf_path):
    """Test that each .gltf file does NOT have more than VERTICES_LIMIT vertices."""
    with open(gltf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    meshes = data.get('meshes', [])
    vertex_count = 0
    for mesh in meshes:
        primitives = mesh.get('primitives', [])
        for primitive in primitives:
            attributes = primitive.get('attributes', {})
            for attribute in attributes.values():
                accessor_index = attribute
                accessor = data['accessors'][accessor_index]
                count = accessor.get('count', 0)
                vertex_count += count
    assert vertex_count <= VERTICES_LIMIT, f"File {gltf_path} has more than {VERTICES_LIMIT} vertices: {vertex_count}"


@pytest.mark.parametrize('gltf_path', gltf_files)
def test_gltf_no_scale(gltf_path):
    """Test that each .gltf file does NOT have a scale on root level nodes."""
    with open(gltf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    root_nodes = get_gltf_root_nodes(data)
    scale = 1.0
    for root_node in root_nodes:
        scale_list = root_node.get('scale', [1.0, 1.0, 1.0])
        # if any scale is not 1.0, then the model is scaled
        for s in scale_list:
            if s != 1.0:
                scale = s
                break
        if s != 1.0:
                break
    assert scale == 1.0, f"File {gltf_path} has a top-level node with scale: {scale}"

@pytest.mark.parametrize('gltf_path', gltf_files)
def test_gltf_no_rotation(gltf_path):
    """Test that each .gltf file does NOT have a rotation on root level nodes."""
    with open(gltf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    root_nodes = get_gltf_root_nodes(data)
    rotation = [0.0, 0.0, 0.0, 1.0]
    for root_node in root_nodes:
        rotation_list = root_node.get('rotation', [0.0, 0.0, 0.0, 1.0])
        # if any rotation is not 0.0 or 1.0, then the model is rotated
        for r in rotation_list:
            if r != 1.0 and r != 0.0:
                rotation = r
                break
        if r != 1.0 and r != 0.0:
                break
    warning_message = f"""File {gltf_path} has a top-level node with rotation: {rotation}.
This may cause issues with the model's orientation.
Pre-export Fix (Best Practice):

In Blender, select the mesh, Ctrl+A → Apply Rotation (and Scale, if needed).

Ensure your model faces the intended forward axis before exporting (usually +Z forward in GLTF, +Y up).

Export Settings:

Use axis conversion in the GLTF exporter (e.g., Blender GLTF exporter has forward and up axis options).

"""
    assert rotation == [0.0, 0.0, 0.0, 1.0], warning_message

@pytest.mark.parametrize('gltf_path', gltf_files)
def test_gltf_no_translation(gltf_path):
    """Test that each .gltf file does NOT have a translation on root level nodes."""
    with open(gltf_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    root_nodes = get_gltf_root_nodes(data)
    translation = [0.0, 0.0, 0.0]
    for root_node in root_nodes:
        translation_list = root_node.get('translation', [0.0, 0.0, 0.0])
        # if any translation is not 0.0, then the model is translated
        for t in translation_list:
            if t != 0.0:
                translation = t
                break
        if t != 0.0:
                break
    assert translation == [0.0, 0.0, 0.0], f"File {gltf_path} has a top-level node with translation: {translation}"


# Test that each .gltf file does NOT have more than TRIANGLE_LIMIT triangles
@pytest.mark.parametrize('gltf_path', gltf_files)
def test_gltf_triangle_count(gltf_path):
    """Test that each .gltf file does NOT have more than TRIANGLE_LIMIT triangles."""
    # Try loading as mesh or scene using trimesh
    try:
        mesh = trimesh.load(gltf_path, force='scene')
    except Exception as e:
        pytest.fail(f"Failed to load {gltf_path} with trimesh: {e}")

    if isinstance(mesh, trimesh.Scene):
        total_tris = sum(len(g.faces) for g in mesh.geometry.values())
    else:
        total_tris = len(mesh.faces)
    if total_tris > TRIANGLE_LIMIT:
        # ANSI escape code for red text
        red = "\033[91m"
        reset = "\033[0m"
        msg = f"File {gltf_path} has more than {TRIANGLE_LIMIT} triangles: {total_tris}"
        pytest.fail(f"{red}{msg}{reset}")
    assert total_tris <= TRIANGLE_LIMIT


