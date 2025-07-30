import logging
import os
from pathlib import Path

import numpy as np
import scipy.cluster.hierarchy as sch
import torch
from matplotlib import pyplot as pl
from tqdm import tqdm

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# TODO: Proposal to remove these tests from the current script and add them in a separate one.
# here we should only import tests, not define them:
# https://ghe.oculus-rep.com/mb-research/wai/pull/6#discussion_r30881
def load_mast3r(module_path, ckpt_path, device):
    """
    Load MAST3R model from a given module path and checkpoint path.
    Args:
        module_path (str): Path to the MAST3R module.
        ckpt_path (str): Path to the model checkpoint.
        device (torch.device): Device to load the model on.
    Returns:
        AsymmetricMASt3R: Loaded MAST3R model.
    """

    if not Path(module_path).exists():
        raise ImportError("Error: the mast3r folder was not found.")
    else:
        import sys

        sys.path.insert(0, module_path)

    from mast3r.model import AsymmetricMASt3R

    # monkey patch from_pretrained model. More info: https://github.com/pytorch/pytorch/releases/tag/v2.6.0
    AsymmetricMASt3R.from_pretrained = from_pretrained
    return AsymmetricMASt3R.from_pretrained(ckpt_path).to(device)


def get_scene_and_corres(
    filelist,
    model,
    cache_dir,
    scene_graph,
    lr1,
    niter1,
    lr2,
    niter2,
    device,
    optim_level,
    shared_intrinsics,
    matching_conf_thr,
    save_correspondences,
):
    """
    Get the scene (SparseGA) and correspondences using MAST3R.
    Args:
        filelist (list): List of image file paths.
        model: MAST3R model to use.
        cache_dir (str): Directory to store cached data.
        scene_graph: Scene graph to use for creating pairs either complete or swin-1
        lr1 (float): Learning rate for the first optimization step.
        niter1 (int): Number of iterations for the first optimization step.
        lr2 (float): Learning rate for the second optimization step.
        niter2 (int): Number of iterations for the second optimization step.
        device (torch.device): Device to run the model on.
        optim_level (str): Optimization level to use.
        shared_intrinsics (bool): Whether to share intrinsics between cameras.
        matching_conf_thr (float): Threshold for matching confidence.
        save_correspondences (bool): Whether to save correspondences to vizualise (only for debug).
    Returns:
        tuple: Scene and correspondences.
    """

    import mast3r.utils.path_to_dust3r  # noqa
    from mast3r.image_pairs import make_pairs
    from dust3r.utils.image import load_images  # noqa

    images = load_images(filelist, size=512, verbose=True)
    # first we create the pairs. default wai is swin1 non-cyclic, non symetrical [(0,1),(1,2), (2,3)...]
    pairs = make_pairs(
        imgs=images,
        scene_graph=scene_graph,
        prefilter=None,
        symmetrize=True,
    )

    os.makedirs(cache_dir, exist_ok=True)
    # Sparse GA: forward mast3r
    scene, corres = sparse_global_alignment(
        filelist,
        pairs,
        cache_dir,
        model,
        lr1=lr1,
        niter1=niter1,
        lr2=lr2,
        niter2=niter2,
        device=device,
        opt_depth="depth" in optim_level,
        shared_intrinsics=shared_intrinsics,
        matching_conf_thr=matching_conf_thr,
        save_correspondences=save_correspondences,
    )
    return scene, corres


def sparse_global_alignment(
    imgs,
    pairs_in,
    cache_path,
    model,
    subsample=8,
    desc_conf="desc_conf",
    kinematic_mode="hclust-ward",
    device="cuda",
    dtype=torch.float32,
    shared_intrinsics=False,
    save_correspondences=False,
    **kw,
):
    """Sparse alignment with MASt3R
    imgs: list of image paths
    cache_path: path where to dump temporary files (str)

    lr1, niter1: learning rate and #iterations for coarse global alignment (3D matching)
    lr2, niter2: learning rate and #iterations for refinement (2D reproj error)

    lora_depth: smart dimensionality reduction with depthmaps
    """
    from mast3r.cloud_opt.sparse_ga import (
        compute_min_spanning_tree,
        condense_data,
        convert_dust3r_pairs_naming,
        prepare_canonical_data,
        sparse_scene_optimizer,
        SparseGA,
        to_numpy,
    )

    # Convert pair naming convention from dust3r to mast3r
    pairs_in = convert_dust3r_pairs_naming(imgs, pairs_in)
    # forward pass
    pairs, cache_path, track_corres = forward_mast3r(
        pairs_in,
        model,
        cache_path=cache_path,
        subsample=subsample,
        desc_conf=desc_conf,
        device=device,
        save_correspondences=save_correspondences,
    )

    # extract canonical pointmaps
    tmp_pairs, pairwise_scores, canonical_views, canonical_paths, preds_21 = (
        prepare_canonical_data(
            imgs,
            pairs,
            subsample,
            cache_path=cache_path,
            mode="avg-angle",
            device=device,
        )
    )

    # smartly combine all useful data
    imsizes, pps, base_focals, core_depth, anchors, corres, corres2d, preds_21 = (
        condense_data(imgs, tmp_pairs, canonical_views, preds_21, dtype)
    )

    # Build kinematic chain
    if kinematic_mode == "mst":
        # compute minimal spanning tree
        mst = compute_min_spanning_tree(pairwise_scores)

    elif kinematic_mode.startswith("hclust"):
        mode, linkage = kinematic_mode.split("-")

        # Convert the affinity matrix to a distance matrix (if needed)
        n_patches = (imsizes // subsample).prod(dim=1)
        max_n_corres = 3 * torch.minimum(n_patches[:, None], n_patches[None, :])
        pws = (pairwise_scores.clone() / max_n_corres).clip(max=1)
        pws.fill_diagonal_(1)
        pws = to_numpy(pws)
        distance_matrix = np.where(pws, 1 - pws, 2)

        # Compute the condensed distance matrix
        condensed_distance_matrix = sch.distance.squareform(distance_matrix)

        # Perform hierarchical clustering using the linkage method
        Z = sch.linkage(condensed_distance_matrix, method=linkage)
        # dendrogram = sch.dendrogram(Z)

        tree = np.eye(len(imgs))
        new_to_old_nodes = {i: i for i in range(len(imgs))}
        for i, (a, b) in enumerate(Z[:, :2].astype(int)):
            # given two nodes to be merged, we choose which one is the best representant
            a = new_to_old_nodes[a]
            b = new_to_old_nodes[b]
            tree[a, b] = tree[b, a] = 1
            best = a if pws[a].sum() > pws[b].sum() else b
            new_to_old_nodes[len(imgs) + i] = best
            pws[best] = np.maximum(pws[a], pws[b])  # update the node

        pairwise_scores = torch.from_numpy(
            tree
        )  # this output just gives 1s for connected edges and zeros for other, i.e. no scores or priority
        mst = compute_min_spanning_tree(pairwise_scores)

    else:
        raise ValueError(f"bad {kinematic_mode=}")

    # remove all edges not in the spanning tree?
    # min_spanning_tree = {(imgs[i],imgs[j]) for i,j in mst[1]}
    # tmp_pairs = {(a,b):v for (a,b),v in tmp_pairs.items() if {(a,b),(b,a)} & min_spanning_tree}

    imgs, res_coarse, res_fine = sparse_scene_optimizer(
        imgs,
        subsample,
        imsizes,
        pps,
        base_focals,
        core_depth,
        anchors,
        corres,
        corres2d,
        preds_21,
        canonical_paths,
        mst,
        shared_intrinsics=shared_intrinsics,
        cache_path=cache_path,
        device=device,
        dtype=dtype,
        **kw,
    )
    scene = SparseGA(imgs, pairs_in, res_fine or res_coarse, anchors, canonical_paths)

    return scene, track_corres


@torch.no_grad()
def forward_mast3r(
    pairs,
    model,
    cache_path,
    desc_conf="desc_conf",
    device="cuda",
    subsample=8,
    save_correspondences=False,
    **matching_kw,
):
    """
    Forward pass through MAST3R.
    Args:
        pairs (list): List of image pairs.
        model: MAST3R model to use.
        cache_path (str): Path to store cached data.
        desc_conf (str, optional): Descriptor confidence. Defaults to "desc_conf".
        device (str, optional): Device to run the model on. Defaults to "cuda".
        subsample (int, optional): Subsample factor. Defaults to 8.
        save_correspondences (bool, optional): Whether to save correspondences. Defaults to False.
        **matching_kw: Additional keyword arguments for matching.
    Returns:
        tuple: Result paths, cache path, and tracked correspondences (in the sense that pairs order are saved, not that points are tracked).
    """
    from mast3r.cloud_opt.sparse_ga import (
        extract_correspondences,
        symmetric_inference,
        to_cpu,
    )
    from mast3r.utils.misc import hash_md5, mkdir_for

    res_paths = {}
    track_corres = []
    for img1, img2 in tqdm(pairs):
        idx1 = hash_md5(img1["instance"])
        idx2 = hash_md5(img2["instance"])

        path1 = cache_path + f"/forward/{idx1}/{idx2}.pth"
        path2 = cache_path + f"/forward/{idx2}/{idx1}.pth"
        path_corres = (
            cache_path + f"/corres_conf={desc_conf}_{subsample=}/{idx1}-{idx2}.pth"
        )
        path_corres2 = (
            cache_path + f"/corres_conf={desc_conf}_{subsample=}/{idx2}-{idx1}.pth"
        )

        if os.path.isfile(path_corres2) and not os.path.isfile(path_corres):
            score, (xy1, xy2, confs) = torch.load(path_corres2)
            torch.save((score, (xy2, xy1, confs)), path_corres)

        if not all(os.path.isfile(p) for p in (path1, path2, path_corres)):
            if model is None:
                continue
            res = symmetric_inference(model, img1, img2, device=device)
            X11, X21, X22, X12 = [r["pts3d"][0] for r in res]
            C11, C21, C22, C12 = [r["conf"][0] for r in res]
            descs = [r["desc"][0] for r in res]
            qonfs = [r[desc_conf][0] for r in res]

            # save
            torch.save(to_cpu((X11, C11, X21, C21)), mkdir_for(path1))
            torch.save(to_cpu((X22, C22, X12, C12)), mkdir_for(path2))

            # perform reciprocal matching
            corres = extract_correspondences(
                descs, qonfs, device=device, subsample=subsample
            )

            track_corres.append((corres, (img1["instance"], img2["instance"])))

            # TODO: add this in separate script.
            if save_correspondences:
                logger.info(f"saving plot for {img1['idx']} and {img2['idx']}")
                save_to_vizualise_matches(
                    img1,
                    img2,
                    corres[0],
                    corres[1],
                    filename=f"{img1['idx']}_{img2['idx']}",
                    num_viz=20,
                    save_path="/fsx/nelsonantunes/misc/",
                )

            conf_score = (
                (C11.mean() * C12.mean() * C21.mean() * C22.mean()).sqrt().sqrt()
            )
            matching_score = (float(conf_score), float(corres[2].sum()), len(corres[2]))
            if cache_path is not None:
                torch.save((matching_score, corres), mkdir_for(path_corres))

        res_paths[img1["instance"], img2["instance"]] = (path1, path2), path_corres

    del model
    torch.cuda.empty_cache()

    return res_paths, cache_path, track_corres


def save_to_vizualise_matches(
    view1,
    view2,
    matches_im0,
    matches_im1,
    filename,
    num_viz=20,
    save_path="/fsx/nelsonantunes/misc/",
):
    """
    method that saves the plot of the correspondences (by stitching the two images together and diplaying the correspondences)
    for debug purposes, to save elsewhere
    """
    num_matches = matches_im0.shape[0]
    match_idx_to_viz = np.round(np.linspace(0, num_matches - 1, num_viz)).astype(int)
    viz_matches_im0, viz_matches_im1 = (
        matches_im0[match_idx_to_viz],
        matches_im1[match_idx_to_viz],
    )

    image_mean = torch.as_tensor([0.5, 0.5, 0.5], device="cpu").reshape(1, 3, 1, 1)
    image_std = torch.as_tensor([0.5, 0.5, 0.5], device="cpu").reshape(1, 3, 1, 1)

    viz_imgs = []

    for i, view in enumerate([view1, view2]):
        rgb_tensor = view["img"] * image_std + image_mean
        viz_imgs.append(rgb_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy())

    H0, W0, H1, _ = *viz_imgs[0].shape[:2], *viz_imgs[1].shape[:2]
    img0 = np.pad(
        viz_imgs[0],
        ((0, max(H1 - H0, 0)), (0, 0), (0, 0)),
        "constant",
        constant_values=0,
    )
    img1 = np.pad(
        viz_imgs[1],
        ((0, max(H0 - H1, 0)), (0, 0), (0, 0)),
        "constant",
        constant_values=0,
    )
    img = np.concatenate((img0, img1), axis=1)
    pl.figure()
    pl.imshow(img)
    cmap = pl.get_cmap("jet")
    for i in range(num_viz):
        (x0, y0), (x1, y1) = viz_matches_im0[i].cpu().T, viz_matches_im1[i].cpu().T
        pl.plot(
            [x0, x1 + W0],
            [y0, y1],
            "-+",
            color=cmap(i / (num_viz - 1)),
            scalex=False,
            scaley=False,
        )
    # save the plot
    output_file = os.path.join(save_path, filename)
    pl.savefig(output_file)
    pl.close()


@classmethod
def from_pretrained(cls, pretrained_model_name_or_path, **kw):
    """
    Monkey patched version of from_pretrained method to fix broken behavior
    due to PyTorch 2.6 upgrade.
    The original method expected weights_only=False by default, but PyTorch 2.6
    changed the default value to True. This patch sets weights_only=False to
    restore the original behavior.

    More info: https://github.com/pytorch/pytorch/releases/tag/v2.6.0
               and https://github.com/suno-ai/bark/issues/626

    WARNING: monkey patching should be used with caution, as it can lead to unexpected behavior and make debugging more difficult.
    """
    from mast3r.model import AsymmetricMASt3R

    def load_model(model_path, device, verbose=True):
        inf = float("inf")  # noqa: F841
        if verbose:
            logger.info("... loading model from {model_path}")
        ckpt = torch.load(model_path, map_location="cpu", weights_only=False)
        args = ckpt["args"].model.replace("ManyAR_PatchEmbed", "PatchEmbedDust3R")
        if "landscape_only" not in args:
            args = args[:-1] + ", landscape_only=False)"
        else:
            args = args.replace(" ", "").replace(
                "landscape_only=True", "landscape_only=False"
            )
        assert "landscape_only=False" in args
        if verbose:
            logger.info(f"instantiating : {args}")
        # needed for patch
        from mast3r.model import AsymmetricMASt3R  # noqa: I001, F401

        net = eval(args)
        s = net.load_state_dict(ckpt["model"], strict=False)
        if verbose:
            logger.info(s)
        return net.to(device)

    if os.path.isfile(pretrained_model_name_or_path):
        return load_model(pretrained_model_name_or_path, device="cpu")
    else:
        return super(AsymmetricMASt3R, cls).from_pretrained(
            pretrained_model_name_or_path, **kw
        )
