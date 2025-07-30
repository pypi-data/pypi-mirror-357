# Profiling results

## Format/lib for loading scene meta data
<p>
    <img src="plots/meta_loading_all.png">
     <img src="plots/meta_loading.png">
</p>

### Conclusion: Use `orjson`

## Depth
<p>
    <img src="plots/depth_sizes.png">
</p>

### Conclusion: Use `png` with scale factor for simplicity

## Scene parsing
Comparing different ways to parse dataset to look for specific properties
<p>
    <img src="plots/scene_parsing.png">
</p>

### Conclusion: Use file system check when possible instead of opening jsons.
