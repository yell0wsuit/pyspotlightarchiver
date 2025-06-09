"""Helper for computing perceptual hash (phash) of images using imagededup."""

from imagededup.methods import PHash

# Create a single PHash instance for reuse
_phasher = PHash()


def compute_phash(image_path):
    """
    Compute the perceptual hash (phash) of an image file.
    """
    return _phasher.encode_image(image_file=image_path)
