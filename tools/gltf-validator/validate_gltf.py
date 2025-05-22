import os
import re
import sys
import numpy as np
from pygltflib import GLTF2
import trimesh
import pyrender
import sys
from PIL import Image, ImageDraw
from pyrender.constants import RenderFlags
from trimesh.transformations import euler_matrix, translation_matrix
import yaml
from spec_image_tools import draw_facing_direction

GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
GITHUB_BRANCH_NAME = os.getenv("GITHUB_REF_NAME")
THICK_GRID_COLOR = (100, 100, 100, 255)
THIN_GRID_COLOR = (200, 200, 200, 255)
THICK_GRID_THICKNESS = 2
THIN_GRID_THICKNESS = 1
CAMERA_DISTANCE_PADDING = 1.0
SPEC_EXTENSION = ".spec.yaml"
image_width, image_height = 256, 256

def get_raw_url(repo, branch, filepath):
    # Construct the raw URL for the file in the GitHub repository
    # Example raw URL: https://github.com/Screwloose-Games/tiny-pet/blob/assets/uploaded-assets/example_character_front_4404.png?raw=true
    print(f"get_raw_url: repo={repo}, branch={branch}, filepath={filepath}")
    return f"https://github.com/{repo}/blob/{branch}/{filepath}?raw=true"

def create_3d_preview_url(gltf_filepth: str, gltf: GLTF2) -> str:
    """
    Create a 3D preview URL for the assets.
    """
    assets: list[str] = []
    assets.append(gltf_filepth)
    if gltf_filepth.endswith(".gltf"):
        bin_file = os.path.splitext(gltf_filepth)[0] + ".bin"
        if os.path.exists(bin_file):
            assets.append(bin_file)
        else:
            print(f"Warning: {bin_file} not found.")
        gltf_basepath = os.path.dirname(gltf_filepth)
        for image in gltf.images:
            if hasattr(image, 'uri') and image.uri:
                assets.append(os.path.join(gltf_basepath, image.uri))

    comma_separated_assets = ",".join([get_raw_url(GITHUB_REPOSITORY, GITHUB_BRANCH_NAME, asset) for asset in assets])
    complete_url = f"https://3dviewer.net/#model={comma_separated_assets}"
    print(f"3D preview URL: {complete_url}")
    return complete_url

def get_bounding_box(mesh, accessors, buffer_views, buffers):
    min_coords = np.array([np.inf, np.inf, np.inf])
    max_coords = np.array([-np.inf, -np.inf, -np.inf])
    for prim in mesh.primitives:
        pos_accessor_idx = getattr(prim.attributes, 'POSITION', None)
        if pos_accessor_idx is None:
            continue
        accessor = accessors[pos_accessor_idx]
        bv = buffer_views[accessor.bufferView]
        buffer = buffers[bv.buffer]
        data = buffer.data
        offset = bv.byteOffset + accessor.byteOffset
        count = accessor.count
        dtype = np.float32
        arr = np.frombuffer(data, dtype=dtype, count=count*3, offset=offset)
        arr = arr.reshape((count, 3))
        min_coords = np.minimum(min_coords, arr.min(axis=0))
        max_coords = np.maximum(max_coords, arr.max(axis=0))
    return min_coords, max_coords

def has_animations(gltf_path: str):
    gltf = GLTF2().load(gltf_path)
    return bool(gltf.animations)


def load_gltf_with_trimesh(filepath: str) -> trimesh.Scene:
    # Trimesh can load glTF directly
    scene = trimesh.load_scene(filepath)
    return scene



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

def get_top_down_camera_pose(scene: trimesh.Scene) -> np.ndarray:
    """
    Returns a camera pose for a top-down view of the scene.
    The camera looks down the -Z axis from above the model.
    """

    bounds = scene.bounds
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


def generate_orthographic_image(scene: trimesh.Scene, camera: pyrender.OrthographicCamera, camera_pose = np.eye(4), render_flags = RenderFlags.RGBA, ) -> Image:
    """
    Renders an orthographic top view (looking down -Z axis) of the scene with transparent background.
    No grid is drawn.
    """
    pyrender_scene = pyrender.Scene.from_trimesh_scene(scene)
    print("Rendering scene")
    pyrender_scene.bg_color = [0, 0, 0, 0]

    pyrender_scene.add(camera, pose=camera_pose)
    light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
    pyrender_scene.add(light, pose=camera_pose)

    print("preparing renderer")
    r = pyrender.OffscreenRenderer(viewport_width=image_width, viewport_height=image_height)
    print("Rendering image")
    color, _ = r.render(pyrender_scene, flags=render_flags)
    print("Generating image from data")
    model_img = Image.fromarray(color, mode="RGBA")
    print("Image generated")
    return model_img

def generate_grid_image(height: int = 1024, width: int = 1024, largest_dist:  float = 2.0) -> Image:
    grid_img = Image.new("RGBA", (width, height), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(grid_img)

    width_world = largest_dist
    width_px = width 
    px_per_unit = width_px / width_world
    dm_size_px = int(px_per_unit * 0.1)
    dm_size_px = max(dm_size_px, 1)  # Ensure at least 1px

    meter_size_px = int(px_per_unit * 1.0)

    # Draw vertical grid lines: center and every dm to left/right
    center_x = width // 2

    is_space_between_thick_lines = dm_size_px > THICK_GRID_THICKNESS * 2

    for x in range(center_x, width, dm_size_px):
        if (x - center_x) % (meter_size_px) == 0:
            # Thicker line each meter

            draw.line([(x, 0), (x, height)], fill=THICK_GRID_COLOR, width=THICK_GRID_THICKNESS)
        elif is_space_between_thick_lines:
            draw.line([(x, 0), (x, height)], fill=(200, 200, 200, 255), width=THIN_GRID_THICKNESS)
    for x in range(center_x, -1, -dm_size_px):
        if (x - center_x) % (meter_size_px) == 0:
            # Thicker line each meter

            draw.line([(x, 0), (x, height)], fill=THICK_GRID_COLOR, width=THICK_GRID_THICKNESS)
        elif is_space_between_thick_lines:
            draw.line([(x, 0), (x, height)], fill=(200, 200, 200, 255), width=THIN_GRID_THICKNESS)

    # Draw horizontal grid lines: start at bottom and go up every dm
    for y in range(height - 1, -1, -dm_size_px):
        if (height - y -1) % (meter_size_px) == 0:
            # Thicker line each meter
            draw.line([(0, y), (width, y)], fill=THICK_GRID_COLOR, width=THICK_GRID_THICKNESS)
        elif is_space_between_thick_lines:
            draw.line([(0, y), (width, y)], fill=(200, 200, 200, 255), width=THIN_GRID_THICKNESS)
    return grid_img

def list_animations(gltf: GLTF2) -> list[str]:
    """
    Lists all animations in the scene.
    """
    animations = []
    if not gltf.animations:
        print("No animations found.")
        return animations
    for animation in gltf.animations:
        animations.append(animation.name)
    return animations

def list_textures(gltf: GLTF2) -> list[str]:
    """
    Lists all textures in the scene.
    """
    textures = []
    if not gltf.textures:
        print("No textures found.")
        return textures
    for texture in gltf.textures:
        texture_strs = []
        if hasattr(texture, 'source') and texture.source is not None:
            image_str = list_images(gltf)[texture.source]
            texture_strs.append(f"Image: {image_str}")
        if hasattr(texture, 'name') and texture.name:
            texture_strs.append(f"Name: {texture.name}")
        textures.append("| ".join(texture_strs))
    return textures

def list_images(gltf: GLTF2) -> list[str]:
    """
    Lists all images in the scene.
    """
    images = []
    if not gltf.images:
        print("No images found.")
        return images
    for image in gltf.images:
        if hasattr(image, 'uri') and image.uri:
            images.append(image.uri)
        elif hasattr(image, 'name') and image.name:
            images.append(image.name)
        elif hasattr(image, 'bufferView') and image.bufferView:
            images.append(f"BufferView id: {image.bufferView}")
        else:
            images.append("Unknown image")
    return images

def list_bones(gltf: GLTF2) -> list[str]:
    """
    Lists all bones in the scene.
    """
    bones = []
    if not gltf.skins:
        print("No bones found.")
        return bones
    for skin in gltf.skins:
        # bones.append(skin.name)
        for joint_node_id in skin.joints:
            bones.append(gltf.nodes[joint_node_id].name)
    return bones

def list_materials(gltf: GLTF2) -> list[str]:
    """
    Lists all materials in the scene.
    """
    materials = []
    if not gltf.materials:
        print("No materials found.")
        return materials
    for material in gltf.materials:
        materials.append(material.name)
    return materials

def get_gltf_scale(gltf: GLTF2) -> float:
    """
    Returns the scale of the glTF model.
    """
    if not gltf.scenes:
        print("No scenes found.")
        return 1.0
    scene = gltf.scenes[gltf.scene]
    if not scene.nodes:
        print("No nodes found in the scene.")
        return 1.0
    node = gltf.nodes[scene.nodes[0]]
    if not node.scale:
        print("No scale found in the node.")
        return 1.0
    return node.scale[0]  # Assuming uniform scaling

def get_poly_count(scene: trimesh.Scene) -> int:
    """
    Returns the total number of polygons in the scene.
    """
    total_polygons = 0
    for mesh in scene.geometry.values():
        if isinstance(mesh, trimesh.Trimesh):
            total_polygons += mesh.faces.shape[0]
    return total_polygons

def read_spec_file(spec_file: str) -> dict:
    """
    Read the yaml spec file and return a dictionary with the contents.
    """
    if not os.path.exists(spec_file):
        print(f"Spec file '{spec_file}' not found.")
        return {}
    with open(spec_file, "r") as f:
        spec = yaml.safe_load(f)
    return spec

def evaluate_model_against_spec(
    gltf: GLTF2,
    spec: dict,
    scene_bounds_size: np.ndarray,
    poly_count: int,
) -> dict:
    """
    Evaluates the model against the provided spec dictionary.
    Returns a dictionary with results for each spec item.
    """
    results = {}

    # Size checks
    width, height, depth = scene_bounds_size[0], scene_bounds_size[1], scene_bounds_size[2]
    results["width"] = abs(width - spec.get("width", width)) / spec.get("width", width) <= 0.10
    results["height"] = abs(height - spec.get("height", height)) / spec.get("height", height) <= 0.10
    results["depth"] = abs(depth - spec.get("depth", depth)) / spec.get("depth", depth) <= 0.10

    # Up direction
    up_dir = spec.get("up_direction", None)
    # This is a simple check, you may want to improve it for more robust axis detection
    if up_dir:
        up_dir = up_dir.strip().upper()
        # Assume +Y means [0,1,0], +Z means [0,0,1], etc.
        # Here we just check if the up direction matches the convention
        # For most glTF, +Y is up by default
        results["up_direction"] = (up_dir == "+Y")

    # Facing direction
    facing_dir = spec.get("facing_direction", None)
    if facing_dir:
        facing_dir = facing_dir.strip().upper()
        # model_facing = get_model_facing_direction(gltf)
        # results["facing_direction"] = (model_facing.replace("+", "") == facing_dir.replace("+", ""))

    # Poly count
    poly_budget = spec.get("poly_count_budget", None)
    if poly_budget is not None:
        results["poly_count_budget"] = poly_count <= poly_budget

    # Root node name
    root_node_name = spec.get("root_node_name", None)
    if root_node_name:
        found = False
        for node in gltf.nodes or []:
            if getattr(node, "name", None) == root_node_name:
                found = True
                break
        results["root_node_name"] = found

    # Collision expected
    if "collision_expected" in spec:
        found = False
        for node in gltf.nodes or []:
            name = getattr(node, "name", "").lower()

            has_collision = name.endswith("-colonly") or name.endswith("-col")\
                  or name.endswith("-convcol") or name.endswith("-convcolonly")

            if has_collision:
                found = True
                break
        results["collision_expected"] = found == bool(spec["collision_expected"])

    # Navigation expected
    if "navigation_expected" in spec:
        found = False
        for node in gltf.nodes or []:
            if getattr(node, "name", "").lower().endswith("-navmesh"):
                found = True
                break
        results["navigation_expected"] = found == bool(spec["navigation_expected"])

    # Minimum material count
    min_material_count = spec.get("min_material_count", None)
    if min_material_count is not None:
        mat_count = len(gltf.materials) if gltf.materials else 0
        results["min_material_count"] = mat_count >= min_material_count

    # Textures expected
    if "textures_expected" in spec:
        image_uris = set(list_images(gltf))
        textures_ok = True
        for tex in spec["textures_expected"]:
            expected = tex.get("expected", True)
            name = tex.get("name", "")
            found = any(name in uri for uri in image_uris)
            if expected and not found:
                textures_ok = False
                print(f"Texture '{name}' not found in the model.")
        results["textures_expected"] = textures_ok
        if not textures_ok:
            print("Textures found in the model:", image_uris)

    # Animations expected
    if "animations_expected" in spec:
        anim_names = set(list_animations(gltf))
        anims_ok = True
        for anim in spec["animations_expected"]:
            name = anim.get("name", "")
            if name and name not in anim_names:
                anims_ok = False
                print(f"Animation '{name}' not found in the model.")
        results["animations_expected"] = anims_ok
        if not anims_ok:
            print("Animations found in the model:", anim_names)
    
    for key, value in results.items():
        if value == False:
            results[key] = "FAIL"
        elif value == True:
            results[key] = "OK"
        elif isinstance(value, str):
            results[key] = value
        else:
            results[key] = "FAIL"

    return results

def render_and_save_view(scene, camera, camera_pose, grid_img, output_path, render_flags=RenderFlags.RGBA, model_facing_direction: str = None) -> str:
    """
    Renders a view of the scene with the given camera pose, overlays the grid, and saves the image.
    """
    print(f"Generating image for {output_path}")
    model_img = generate_orthographic_image(scene, camera, camera_pose, render_flags)
    print(f"Rendering image for {output_path}")
    final_img = Image.alpha_composite(grid_img, model_img)
    print(f"Overlaying grid on image for {output_path}")
    draw = ImageDraw.Draw(final_img)
    if model_facing_direction:
        draw_facing_direction(draw, model_facing_direction)
    print(f"Saving image to {output_path}")
    final_img.convert("RGB").save(output_path)
    return output_path

def create_markdown_report(poly_count: int, width: float, depth: float, height: float, animations: list[str], textures: list[str], images: list[str], materials: list[str], bones: list[str], scale: float, rendered_images: dict, preview_3d_url: str = None) -> str:
    """
    Creates a markdown report of the model.
    """
    report = f"""
### [Model Preview]({preview_3d_url})""" + '{:target="_blank"}' + f"""

### Model Report
#### Model Statistics
- **Total Polygons**: {poly_count}

#### Size
- **Width (X)**: {width:.4f}
- **Height (Y)**: {height:.4f}
- **Depth (Z)**: {depth:.4f}
- **Scale**: {scale}
- **Animations**: {animations}
- **Textures**: {textures}
- **Images**: {images}
- **Materials**: {materials}
- **Total Bones found**: {len(bones)}
"""

    if len(bones) > 0:
        report += f"- **Bones**: {bones}\n"

    recommended_poly_max = 20000
    has_too_many_polys = poly_count > recommended_poly_max
    is_scaled = scale != 1.0

    has_issues = has_too_many_polys or is_scaled
    if has_issues:
        report += "\n# Warnings\n"

    if is_scaled:
        report += f"\nThe model is not at 1:1 scale. scale is: {scale}\nPlease check the model.\n"
    if has_too_many_polys:
        report += f"\nThe model has a high polygon count. This may affect performance. Max recommended poly count: {recommended_poly_max}\n"

    report += "#### Images\n\n"

    for image_name, image_path in rendered_images.items():
        report += f"![{image_name}]({image_path})"

    return report

def create_png_filename(gltf_file: str, view: str) -> str:
    """
    Create a PNG filename based on the GLTF file name and view.
    """
    base_name = os.path.splitext(os.path.basename(gltf_file))[0]
    return f"{base_name}_{view}.png"


def process_gltf_file(gltf_file: str, output_dir: str) -> dict:
    """
    Process a single GLTF file and return results.
    """
    try:
        # First check if the file exists
        if not os.path.exists(gltf_file):
            print(f"File not found: {gltf_file}")
            return {
                "file": gltf_file,
                "error": f"File not found: {gltf_file}",
                "success": False
            }

        # Check if the file is a GLTF file
        if not gltf_file.lower().endswith(('.gltf', '.glb')):
            print(f"Not a GLTF file: {gltf_file}")
            return {
                "file": gltf_file,
                "error": f"Not a GLTF file: {gltf_file}",
                "success": False
            }

        # Check for missing resources
        gltf: GLTF2 = GLTF2().load(gltf_file)
        base_dir = os.path.dirname(gltf_file)
        missing_resources = []

        # Check images
        if gltf.images:
            for image in gltf.images:
                if hasattr(image, 'uri') and image.uri:
                    image_path = os.path.join(base_dir, image.uri)
                    if not os.path.exists(image_path):
                        missing_resources.append(f"Image: {image.uri}")

        # Check buffers
        if gltf.buffers:
            for buffer in gltf.buffers:
                if hasattr(buffer, 'uri') and buffer.uri:
                    buffer_path = os.path.join(base_dir, buffer.uri)
                    if not os.path.exists(buffer_path):
                        missing_resources.append(f"Buffer: {buffer.uri}")

        if missing_resources:
            print(f"Missing resources:\n" + "\n".join(f"- {r}" for r in missing_resources))
            return {
                "file": gltf_file,
                "error": f"Missing resources:\n" + "\n".join(f"- {r}" for r in missing_resources),
                "success": False
            }

        try:
            scene = load_gltf_with_trimesh(gltf_file)
        except Exception as e:
            print(f"Failed to load GLTF file: {str(e)}")
            return {
                "file": gltf_file,
                "error": f"Failed to load GLTF file: {str(e)}",
                "success": False
            }

        scene_bounds_size: np.ndarray[np.float64] = scene.bounds[1] - scene.bounds[0]
        SCENE_BOUNDS_PADDING_PERCENTAGE = 0.1
        padded_scene_bounds_size = scene_bounds_size * (1 + SCENE_BOUNDS_PADDING_PERCENTAGE)  # add some padding to the bounds in all directions

        largest_dim = max(padded_scene_bounds_size)
        camera = pyrender.OrthographicCamera(xmag=largest_dim / 2, ymag=largest_dim / 2)
        grid_img = generate_grid_image(height=image_height, width=image_width, largest_dist=largest_dim)
        wireframe_render_flags = RenderFlags.RGBA + RenderFlags.ALL_WIREFRAME

        spec = read_spec_file(gltf_file + SPEC_EXTENSION)
        
        poly_count = get_poly_count(scene)
        print(f"Evaluating model against spec for {gltf_file}")
        validation_results = evaluate_model_against_spec(
            gltf=gltf,
            spec=spec,
            scene_bounds_size=scene_bounds_size,
            poly_count=poly_count
        )

        # Create output directory for this file
        file_output_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(gltf_file))[0])
        os.makedirs(file_output_dir, exist_ok=True)

        # Render and save views
        print(f"Rendering and saving views for {gltf_file}")
        print(f"Output directory: {file_output_dir}")

        rendered_images = {
            "front": render_and_save_view(scene, camera, get_front_camera_pose(scene), grid_img, create_png_filename(gltf_file, "front")),
            "top": render_and_save_view(scene, camera, get_top_down_camera_pose(scene), grid_img, create_png_filename(gltf_file, "top"), model_facing_direction="down"),
            "right": render_and_save_view(scene, camera, get_right_side_camera_pose(scene), grid_img, create_png_filename(gltf_file, "right"), model_facing_direction="right"),
            "front_wireframe": render_and_save_view(scene, camera, get_front_camera_pose(scene), grid_img, create_png_filename(gltf_file, "front_wireframe"), render_flags=wireframe_render_flags),
            "top_wireframe": render_and_save_view(scene, camera, get_top_down_camera_pose(scene), grid_img, create_png_filename(gltf_file, "top_wireframe"), render_flags=wireframe_render_flags),
            "right_wireframe": render_and_save_view(scene, camera, get_right_side_camera_pose(scene), grid_img, create_png_filename(gltf_file, "right_wireframe"), render_flags=wireframe_render_flags),
            "front_normals": render_and_save_view(scene, camera, get_front_camera_pose(scene), grid_img, create_png_filename(gltf_file, "front_normals"), render_flags=RenderFlags.RGBA + RenderFlags.OFFSCREEN + RenderFlags.FACE_NORMALS),
            "top_normals": render_and_save_view(scene, camera, get_top_down_camera_pose(scene), grid_img, create_png_filename(gltf_file, "top_normals"), render_flags=RenderFlags.RGBA + RenderFlags.OFFSCREEN + RenderFlags.FACE_NORMALS),
            "right_normals": render_and_save_view(scene, camera, get_right_side_camera_pose(scene), grid_img, create_png_filename(gltf_file, "right_normals"), render_flags=RenderFlags.RGBA + RenderFlags.OFFSCREEN + RenderFlags.FACE_NORMALS),
        }

        # Create 3D preview URL

        preview_3d_url = create_3d_preview_url(gltf_file, gltf)
        
        # Create markdown report
        print(f"Creating markdown report for {gltf_file}")
        report = create_markdown_report(
            poly_count=get_poly_count(scene),
            width=scene_bounds_size[0],
            depth=scene_bounds_size[2],
            height=scene_bounds_size[1],
            animations=list_animations(gltf),
            textures=list_textures(gltf),
            images=list_images(gltf),
            materials=list_materials(gltf),
            bones=list_bones(gltf),
            scale=get_gltf_scale(gltf),
            rendered_images=rendered_images,
            preview_3d_url=preview_3d_url,
        )

        REPORT_FILEPATH = os.path.join(file_output_dir, "report.md")
        with open(REPORT_FILEPATH, "w") as f:
            f.write(report)

        print(f"Report saved to: {REPORT_FILEPATH}")

        return {
            "file": gltf_file,
            "report": report,
            "validation_results": validation_results,
            "report_filepath": REPORT_FILEPATH,
            "file_output_dir": file_output_dir,
            "success": True
        }
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return {
            "file": gltf_file,
            "error": f"Error processing file: {str(e)}",
            "success": False
        }

def create_github_comment(results: list[dict]) -> str:
    """
    Create a GitHub comment from the validation results.
    """
    comment = ""

    # Result:
    # {
    #     "file": gltf_file,
    #     "report": report,
    #     "validation_results": validation_results,
    #     "report_filepath": REPORT_FILEPATH,
    #     "images_dir": file_output_dir,
    #     "success": True
    # }

    
    for result in results:
        
        if not result["success"]:
            comment += f"## ❌ {os.path.basename(result['file'])}\n"
            comment += f"Error: {result['error']}\n\n"
            continue

        comment += f"## ✅ {os.path.basename(result['file'])}\n"
        
        # Add validation results
        comment += "### Validation Results:\n"
        for key, value in result["validation_results"].items():
            status = "✅" if value == "OK" else "❌"
            comment += f"- {key}: {status} {value}\n"
        
        # Add report content
        # with open(result["report_filepath"], "r") as f:
        #     report_content = f.read()
        #     comment += f"\n#### Model Report:\n{report_content}\n"

        report = result.get("report", None)
        if report:
            comment += f"### Model Report:\n{report}\n\n"
        
        # # Add images
        # comment += "\n#### Model Views:\n"
        # for view in ["front", "top", "right"]:
        #     image_path = os.path.join(result["images_dir"], f"{view}.png")
        #     if os.path.exists(image_path):
        #         comment += f"![{view} view]({image_path})\n"
        
        comment += "\n---\n\n"
    
    return comment

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_gltf.py <output_dir> [gltf_file1] [gltf_file2] ...")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    gltf_files = sys.argv[2:]
    print(f"Output directory: {output_dir}")
    print(f"GLTF files: {gltf_files}")
    
    if not gltf_files:
        print("No GLTF files provided")
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    for gltf_file in gltf_files:
        result = process_gltf_file(gltf_file, output_dir)
        results.append(result)
    
    # Create GitHub comment
    comment = create_github_comment(results)
    
    # Save comment to file for GitHub Action to use
    with open(os.path.join(output_dir, "github_comment.md"), "w") as f:
        f.write(comment)
    
    # Print summary
    success_count = sum(1 for r in results if r["success"])
    print(f"Processed {len(results)} files: {success_count} successful, {len(results) - success_count} failed")
