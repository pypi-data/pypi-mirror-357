from pathlib import Path

import torch
import torchvision

try:
    from mmcv.utils import Config
except ImportError:
    from mmengine import Config


def metric3d_vit_large(metric3d_path, ckpt_path):
    """
    Return a Metric3D model with ViT-Large backbone and RAFT-8iter head.
    Returns:
      model (nn.Module): a Metric3D model.
    """
    from mono.model.monodepth_model import get_configured_monodepth_model

    cfg_file = f"{metric3d_path}/mono/configs/HourglassDecoder/vit.raft5.large.py"
    cfg = Config.fromfile(cfg_file)
    model = get_configured_monodepth_model(cfg)
    model.load_state_dict(
        torch.load(ckpt_path)["model_state_dict"],
        strict=False,
    )
    return model


def load_model(metric3d_path, ckpt_path, device="cuda"):
    if not Path(metric3d_path).exists():
        raise RuntimeError(f"Metric3dv2 repo not found at: {metric3d_path}")
    import sys

    sys.path.append(str(metric3d_path))
    model = metric3d_vit_large(metric3d_path, ckpt_path).to(device).eval()
    return model


@torch.no_grad()
def get_depth_batch(model, images, fx, fy, cx, cy, resize_to_orig_size=True):
    device = next(model.parameters()).device
    # clearing buffer between runs!
    model.depth_model.decoder._buffers = {}

    images = images.to(device)
    # image is now BxCxHxW tensor with values in [0, 1]
    B, C, H, W = images.shape

    assert images.min() >= 0 and images.max() <= 1

    #### ajust input size to fit pretrained model
    # keep ratio resize
    input_size = (616, 1064)  # for vit model
    # input_size = (544, 1216) # for convnext model
    scale = min(input_size[0] / H, input_size[1] / W)
    # rgb = cv2.resize(image, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_LINEAR)
    rgb = torchvision.transforms.functional.resize(
        images,
        (int(H * scale), int(W * scale)),
        interpolation=torchvision.transforms.InterpolationMode.BILINEAR,
    )
    # remember to scale intrinsic, hold depth
    intrinsic = [fx * scale, fy * scale, cx * scale, cy * scale]

    # padding to input_size
    padding = [123.675, 116.28, 103.53]
    h, w = rgb.shape[-2:]
    pad_h = input_size[0] - h
    pad_w = input_size[1] - w
    pad_h_half = pad_h // 2
    pad_w_half = pad_w // 2
    # rgb = cv2.copyMakeBorder(rgb, pad_h_half, pad_h - pad_h_half, pad_w_half, pad_w - pad_w_half, cv2.BORDER_CONSTANT, value=padding)
    border = (
        pad_w_half,
        pad_h_half,
        pad_w - pad_w_half,
        pad_h - pad_h_half,
    )  # left top right bottom
    pad_value = (
        -1
    )  # overwrite afterwards since pad does not support tuple input for tensors
    rgb = torchvision.transforms.functional.pad(
        rgb, border, padding_mode="constant", fill=pad_value
    )
    pad_tensor = torch.stack(
        [torch.full_like(rgb[:, 0], fill_value=padding[i]) for i in range(3)], 1
    )
    rgb = torch.where(
        rgb == pad_value, pad_tensor, rgb * 255
    )  # change rgb value range to [0, 255]
    pad_info = [pad_h_half, pad_h - pad_h_half, pad_w_half, pad_w - pad_w_half]

    #### normalize
    mean = (
        torch.tensor([123.675, 116.28, 103.53]).float()[None, :, None, None].to(device)
    )
    std = torch.tensor([58.395, 57.12, 57.375]).float()[None, :, None, None].to(device)
    rgb = torch.div((rgb - mean), std)

    ###################### canonical camera space ######################
    # inference
    model.eval()
    with torch.no_grad():
        pred_depth, confidence, output_dict = model.inference({"input": rgb})

    # un pad
    pred_depth = pred_depth.squeeze(1)
    pred_depth = pred_depth[
        :,
        pad_info[0] : pred_depth.shape[1] - pad_info[1],
        pad_info[2] : pred_depth.shape[2] - pad_info[3],
    ]

    confidence = confidence.squeeze(1)
    confidence = confidence[
        :,
        pad_info[0] : confidence.shape[1] - pad_info[1],
        pad_info[2] : confidence.shape[2] - pad_info[3],
    ]

    # upsample to original size
    if resize_to_orig_size:  # changed upsampling mode to nearest for depth
        pred_depth = torch.nn.functional.interpolate(
            pred_depth[:, None, :, :], (H, W), mode="nearest"
        ).squeeze(1)
        confidence = torch.nn.functional.interpolate(
            confidence[:, None, :, :], (H, W), mode="nearest"
        ).squeeze(1)
    ###################### canonical camera space ######################

    #### de-canonical transform
    canonical_to_real_scale = (
        intrinsic[0].to(device) / 1000.0
    )  # 1000.0 is the focal length of canonical camera
    pred_depth = pred_depth * canonical_to_real_scale.view(
        -1, 1, 1
    )  # now the depth is metric
    pred_depth = torch.clamp(pred_depth, 0, 300)

    #### normal are also available
    # if 'prediction_normal' in output_dict: # only available for Metric3Dv2, i.e. vit model
    pred_normal = output_dict["prediction_normal"][:, :3, :, :]
    normal_confidence = output_dict["prediction_normal"][
        :, 3, :, :
    ]  # see https://arxiv.org/abs/2109.09881 for details
    # un pad and resize to some size if needed
    pred_normal = pred_normal[
        :,
        :,
        pad_info[0] : pred_normal.shape[2] - pad_info[1],
        pad_info[2] : pred_normal.shape[3] - pad_info[3],
    ]
    normal_confidence = normal_confidence[
        :,
        pad_info[0] : normal_confidence.shape[1] - pad_info[1],
        pad_info[2] : normal_confidence.shape[2] - pad_info[3],
    ]

    if resize_to_orig_size:
        pred_normal = torch.nn.functional.interpolate(
            pred_normal, (H, W), mode="bilinear"
        )
        normal_confidence = torch.nn.functional.interpolate(
            normal_confidence[:, None, :, :], (H, W), mode="bilinear"
        ).squeeze(1)

    return pred_depth, confidence, pred_normal, normal_confidence
