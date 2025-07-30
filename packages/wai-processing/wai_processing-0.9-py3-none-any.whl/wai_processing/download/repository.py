from subprocess import call


def git_clone(url, target_path=".", recursive=True):
    """Clone a git repository.
    """
    cmd = ["git", "clone", url]
    if recursive:
        cmd.append("--recursive")
    if target_path is not None:
        cmd.append(target_path)
    call(cmd)
    return target_path

def download_mast3r(target_path):
    """Download mast3r repository.
    """
    return git_clone("https://github.com/naver/mast3r.git", target_path)

def download_asmk(target_path):
    """Download asmk repository.
    """
    return git_clone("https://github.com/jenicek/asmk.git", target_path)

def download_metric3dv2(target_path):
    """Download metric3dv2 repository.
    """
    return git_clone("https://github.com/YvanYin/Metric3D", target_path)
