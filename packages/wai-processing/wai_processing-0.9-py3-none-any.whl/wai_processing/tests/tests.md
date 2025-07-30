# Tests

## Using nerfstudio
To run a nerfstudio reconstruction, just add `--camera-convention opencv` since we nerfstudio uses `opengl`:
```
ns-train nerfacto --pipeline.model.camera-optimizer.mode off nerfstudio-data --data=/fsx/snpp_wai/00777c41d4/scene_meta.json --camera-convention opencv
```
<p>
    <img src="nerfstudio_test.png">
</p>

## Metric alignment
Visual test if colmap+mono depth yields ~ metric scale:
```
python test/test_metric_aligment.py
```
<p>
    <img src="metric_alignment.jpg">
</p>

## Mesh rendering
Visual test of rendered mesh (color + depth)
```
python test/test_mesh_render.py
```
<p>
    <img src="mesh_render.png">
</p>
