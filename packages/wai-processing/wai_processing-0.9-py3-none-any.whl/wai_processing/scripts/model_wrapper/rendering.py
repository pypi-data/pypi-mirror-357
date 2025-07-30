import numpy as np
import torch
import trimesh
from torch.nn import functional as F
from wai.ops import to_dtype_device, to_torch_device_contiguous


def prepare_scene_rendering(mesh_data, camera_params):
    """Creates a pyrender scene to be rendered with pyrender"""

    import os

    # needed for pyrender scene rendering
    os.environ["PYOPENGL_PLATFORM"] = "egl"

    import pyrender

    # init dict to store rendering data
    rendering_data = {}

    # initialize renderer
    renderer = pyrender.OffscreenRenderer(
        viewport_width=camera_params["w"], viewport_height=camera_params["h"]
    )
    rendering_data["renderer"] = renderer

    # load or create a pyrender scene
    if isinstance(mesh_data, trimesh.Trimesh):
        scene = pyrender.Scene()
        mesh = pyrender.Mesh.from_trimesh(mesh_data)
        scene.add(mesh)
    elif isinstance(mesh_data, trimesh.Scene):
        scene = pyrender.Scene.from_trimesh_scene(mesh_data)
    else:
        raise ValueError(
            "Scene rendering currently supports only trimesh.Trimesh or trimesh.Scene meshes."
        )

    # add camera
    camera = pyrender.IntrinsicsCamera(
        fx=camera_params["fl_x"],
        fy=camera_params["fl_y"],
        cx=camera_params["cx"],
        cy=camera_params["cy"],
    )
    camera_node = scene.add(camera)
    rendering_data["camera_node"] = camera_node

    # add scene
    rendering_data["scene"] = scene

    return rendering_data


def render_scene(rendering_data, c2w_gl):
    """Renders a pyrender scene using pyrender"""
    from pyrender.constants import RenderFlags

    rendering_data["scene"].set_pose(
        rendering_data["camera_node"],
        pose=to_dtype_device(c2w_gl, device=np.ndarray, dtype=np.float32),
    )

    color, depth = rendering_data["renderer"].render(
        rendering_data["scene"], flags=RenderFlags.FLAT
    )
    color = color / 255.0  # rgb in [0,1]
    return color, depth


def prepare_mesh_rendering(mesh_data, camera_data, device="cuda"):
    """Prepares the rendering data for rendering with nvdiffrast"""
    import nvdiffrast.torch as dr

    # check if the mesh data is a wai labeled mesh
    if (
        isinstance(mesh_data, dict)
        and "is_labeled_mesh" in mesh_data
        and mesh_data["is_labeled_mesh"]
    ):
        # mesh is a wai labeled mesh, copy its contents
        rendering_data = mesh_data.copy()
        # normalize color to [0,1]
        rendering_data["vertices_color"] = rendering_data["vertices_color"] / 255.0

    elif isinstance(mesh_data, trimesh.Trimesh):
        # init dict to store rendering data
        rendering_data = {}

        # get mesh vertices and faces
        vertices = np.asarray(mesh_data.vertices, dtype=np.float32)
        faces = np.asarray(mesh_data.faces, dtype=np.int32)
        rendering_data["vertices"] = vertices
        rendering_data["faces"] = faces

        # get vertices color if available
        if (
            hasattr(mesh_data, "visual")
            and hasattr(mesh_data.visual, "vertex_colors")
            and mesh_data.visual.vertex_colors is not None
        ):
            vertices_color = np.asarray(
                mesh_data.visual.vertex_colors, dtype=np.float32
            )[:, :3]  # discard alpha channel
            rendering_data["vertices_color"] = vertices_color / 255.0

        # get texture if available
        if (
            hasattr(mesh_data, "visual")
            and hasattr(mesh_data.visual, "material")
            and mesh_data.visual.material.image is not None
        ):
            texture_image = np.array(mesh_data.visual.material.image, dtype=np.float32)
            vertices_uvs = np.asarray(mesh_data.visual.uv, dtype=np.float32)

            # normalize color in [0,1]
            texture_image = texture_image / 255.0

            # add texture data to rendering data
            rendering_data["texture"] = {
                "image": texture_image,
                "vertices_uvs": vertices_uvs,
            }

    # sanity check
    if not any(k in rendering_data for k in ["texture", "vertices_color"]):
        raise ValueError(
            "Rendering requires mesh data to have texture and/or vertices color."
        )

    # convert data to torch and load on device
    rendering_data = to_torch_device_contiguous(rendering_data, device, contiguous=True)

    # add nvdiffrast rasterizer (OpenGL)
    rasterizer = dr.RasterizeGLContext()
    rendering_data["rasterizer"] = rasterizer

    # add image size and camera intrinsics
    rendering_data["w"] = camera_data["w"]
    rendering_data["h"] = camera_data["h"]
    rendering_data["fl_x"] = camera_data["fl_x"]
    rendering_data["fl_y"] = camera_data["fl_y"]
    rendering_data["cx"] = camera_data["cx"]
    rendering_data["cy"] = camera_data["cy"]

    return rendering_data


def render_mesh(rendering_data, c2w_gl, invalid_face_id, near, far, device="cuda"):
    """Renders a mesh using nvdiffrast, producing color, depth and face_ids"""
    import nvdiffrast.torch as dr

    # initialize rasterization
    x = rendering_data["w"] / (2.0 * rendering_data["fl_x"])
    y = rendering_data["h"] / (2.0 * rendering_data["fl_y"])
    projection = np.array(
        [
            [1 / x, 0, 0, 0],
            [0, -1 / y, 0, 0],
            [0, 0, -(far + near) / (far - near), -(2 * far * near) / (far - near)],
            [0, 0, -1, 0],
        ],
        dtype=np.float32,
    )
    projection = torch.from_numpy(projection).to(device)
    c2w_gl = torch.from_numpy(c2w_gl).to(device)
    view_matrix = projection @ torch.inverse(c2w_gl)

    # rasterize mesh (get face id for each pixel)
    vertices_h = F.pad(
        rendering_data["vertices"], pad=(0, 1), mode="constant", value=1.0
    )
    vertices_clip = torch.matmul(
        vertices_h, torch.transpose(view_matrix, 0, 1)
    ).unsqueeze(0)  # [1, num_vertices, 4]
    rasterization, _ = dr.rasterize(
        rendering_data["rasterizer"],
        vertices_clip,
        rendering_data["faces"],
        (rendering_data["h"], rendering_data["w"]),
    )  # [1, h, w, 4]
    unbatched_rasterization = rasterization.squeeze(0)  # [h, w, 4]

    # render color (priority to texture over vertices color)
    if "texture" in rendering_data:
        vertices_uvs = rendering_data["texture"]["vertices_uvs"]

        # invert v coordinate (for nvdiffrast)
        vertices_uvs[:, 1] = 1.0 - vertices_uvs[:, 1]

        # interpolate UVs
        uv_interp, _ = dr.interpolate(
            vertices_uvs,
            rasterization,
            rendering_data["faces"],
        )

        # render texture
        color = dr.texture(
            rendering_data["texture"]["image"].unsqueeze(0),
            uv_interp,
            filter_mode="linear",
        )

    elif "vertices_color" in rendering_data:
        # interpolate vertices color
        color, _ = dr.interpolate(
            rendering_data["vertices_color"].float(),
            rasterization,
            rendering_data["faces"],
        )
    else:
        raise ValueError("Rendering requires texture and/or vertices color.")

    # postprocess faces ids (rasterized faces ids have an offset of +1, valid faces ids are >= 1)
    rasterized_face_id = unbatched_rasterization[..., 3].int()
    valid_faces = rasterized_face_id >= 1

    # initialize output faces ids as INVALID_FACE_ID
    output_face_id = torch.full_like(rasterized_face_id, fill_value=invalid_face_id)

    # fill valid faces ids in the output, removing the offset
    output_face_id[valid_faces] = rasterized_face_id[valid_faces] - 1

    # get depth (rasterized depth is in clip space z/w, [-1, 1] range)
    clip_depth = unbatched_rasterization[..., 2]

    # convert clip_depth to metric depth (initialize as invalid depth = 0)
    depth = torch.zeros_like(clip_depth)

    # avoid numerical issues around far plane
    valid_depth = clip_depth < 0.999

    # compute metric depth
    valid_pixels = valid_faces & valid_depth
    depth[valid_pixels] = (2.0 * near * far) / (
        far + near - clip_depth[valid_pixels] * (far - near)
    )

    # ouput data as numpy arrays
    color = color.squeeze(0).cpu().numpy()
    depth = depth.squeeze(0).cpu().numpy()
    output_face_id = output_face_id.squeeze(0).cpu().numpy()

    return color, depth, output_face_id
