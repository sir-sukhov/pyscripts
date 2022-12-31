# Image Streamer
## Watches tags in registry and update local "latest" tag once new (not "latest") tag appears
### This script might be helpful in corporate registry where tag rewrite is prohibited, but auto-update is still required.

# How it works

1. Endless loop ensures that local image with "latest" tag points to highest image version.
    1. Fetch tags from remote registry, filter by regexp, take the highest version.
    1. Digest of highest remote tag is compared with digest of local "latest" tag.
    1. If local digest does not match remote, image is pulled from registry, local "latest" tag is updated.
