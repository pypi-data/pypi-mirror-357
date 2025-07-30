import logging
import os
from pathlib import Path

import numpy as np
import scipy.cluster.hierarchy as sch
import torch
from tqdm import tqdm

## Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

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


def load_retrieval_model(retrieval_model, backbone, device):
    from mast3r.retrieval.processor import Retriever

    Retriever.__init__ = retriever_init
    return Retriever(retrieval_model, backbone=backbone, device=device)


def get_scene_and_corres(
    filelist,
    model,
    sim_matrix,
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
    ret_nb_anchors,
    ret_knn,
):
    """
    Get the scene (SparseGA) and correspondences using MAST3R.
    Args:
        filelist (list): List of image file paths.
        model: MAST3R model to use.
        cache_dir (str): Directory to store cached data.
        sim_matrix: similarity matrix from retreival model.
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
        ret_nb_anchors (int): number of anchors used by the retrieval model
        knn (int): k-nearest-neighbors value used by the retrieval model
    Returns:
        tuple: Scene and correspondences.
    """

    import mast3r.utils.path_to_dust3r  # noqa
    from mast3r.image_pairs import make_pairs
    from dust3r.utils.image import load_images  # noqa

    images = load_images(filelist, size=512, verbose=True)

    if "retrieval" in scene_graph:
        num_key_images = min(len(images), ret_nb_anchors)
        num_neighbors = min(len(images) // 2, ret_knn)
        scene_graph = f"{scene_graph}-{num_key_images}-{num_neighbors}"

    pairs = make_pairs(
        imgs=images,
        scene_graph=scene_graph,
        prefilter=None,
        symmetrize=True,
        sim_mat=sim_matrix,
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
            logger.info(f"... loading model from {model_path}")
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
            print(f"instantiating : {args}")
        # needed for patch
        from mast3r.model import AsymmetricMASt3R  # noqa: I001, F401

        net = eval(args)
        s = net.load_state_dict(ckpt["model"], strict=False)
        if verbose:
            print(s)
        return net.to(device)

    if os.path.isfile(pretrained_model_name_or_path):
        return load_model(pretrained_model_name_or_path, device="cpu")
    else:
        return super(AsymmetricMASt3R, cls).from_pretrained(
            pretrained_model_name_or_path, **kw
        )


def retriever_init(self, modelname, backbone, device="cuda"):
    from asmk import asmk_method  # noqa
    from mast3r.retrieval.model import RetrievalModel

    # load the model
    assert os.path.isfile(modelname), modelname
    print(f"Loading retrieval model from {modelname}")
    ckpt = torch.load(modelname, "cpu", weights_only=False)
    ckpt_args = ckpt["args"]
    self.model = RetrievalModel(
        backbone,
        freeze_backbone=ckpt_args.freeze_backbone,
        prewhiten=ckpt_args.prewhiten,
        hdims=list(map(int, ckpt_args.hdims.split("_")))
        if len(ckpt_args.hdims) > 0
        else "",
        residual=getattr(ckpt_args, "residual", False),
        postwhiten=ckpt_args.postwhiten,
        featweights=ckpt_args.featweights,
        nfeat=ckpt_args.nfeat,
    ).to(device)
    self.device = device
    msg = self.model.load_state_dict(ckpt["model"], strict=False)
    assert all(k.startswith("backbone") for k in msg.missing_keys)
    assert len(msg.unexpected_keys) == 0
    self.imsize = ckpt_args.imsize

    # load the asmk codebook
    dname, bname = os.path.split(
        modelname
    )  # TODO they should both be in the same file ?
    bname_splits = bname.split("_")
    cache_codebook_fname = os.path.join(
        dname, "_".join(bname_splits[:-1]) + "_codebook.pkl"
    )
    assert os.path.isfile(cache_codebook_fname), cache_codebook_fname
    asmk_params = {
        "index": {"gpu_id": 0},
        "train_codebook": {"codebook": {"size": "64k"}},
        "build_ivf": {
            "kernel": {"binary": True},
            "ivf": {"use_idf": False},
            "quantize": {"multiple_assignment": 1},
            "aggregate": {},
        },
        "query_ivf": {
            "quantize": {"multiple_assignment": 5},
            "aggregate": {},
            "search": {"topk": None},
            "similarity": {"similarity_threshold": 0.0, "alpha": 3.0},
        },
    }
    asmk_params["train_codebook"]["codebook"]["size"] = ckpt_args.nclusters
    self.asmk = asmk_method.ASMKMethod.initialize_untrained(asmk_params)
    self.asmk = self.asmk.train_codebook(None, cache_path=cache_codebook_fname)
