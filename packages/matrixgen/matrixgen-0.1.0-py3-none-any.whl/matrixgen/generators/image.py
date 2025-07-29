import os
import tempfile

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sp
from PIL import Image
from scipy.sparse import csr_matrix


def create_heatmap(matrix: sp.spmatrix, output_file: str) -> None:
    """Create a heat-map PNG from a sparse or dense matrix."""
    # dense copy
    if hasattr(matrix, "toarray"):
        matrix = matrix.toarray()
    matrix = np.asarray(matrix)

    rows, cols = matrix.shape
    mask = matrix != 0

    if np.any(mask):
        vmin = matrix[mask].min()
        vmax = matrix[mask].max()
    else:
        vmin, vmax = 0, 1

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.viridis

    rgba = cmap(norm(matrix))
    rgba[~mask] = [1, 1, 1, 1]  # white for zeros

    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
    img = Image.fromarray(rgb)
    img.save(output_file, format="PNG")


def convert_grayscale(input_image_path: str, output_image_path: str) -> None:
    """Convert an image to grayscale."""
    with Image.open(input_image_path) as img:
        grayscale_img = img.convert("L")
        grayscale_img.save(output_image_path)


def expand_image(
    input_image_path: str,
    new_size: int,
    output_image_path: str,
    resize_method: int = Image.Resampling.BOX,
) -> None:
    """
    Resize an image to the specified size using the chosen resizing method.

    Args:
        input_image_path: Path to the input image
        new_size: Desired size of the output image
        output_image_path: Path to save the resized image
        resize_method: Image resizing method (Image.Resampling.NEAREST, Image.Resampling.BILINEAR,
                     Image.Resampling.BICUBIC, Image.Resampling.LANCZOS, Image.Resampling.BOX)
    """
    with Image.open(input_image_path) as img:
        resized_img = img.resize((new_size, new_size), resize_method)
        resized_img.save(output_image_path)


def image_to_sparse_matrix(input_image_path: str) -> sp.csr_matrix:
    """Convert a grayscale image to a sparse matrix."""
    with Image.open(input_image_path) as img:
        grayscale_img = img.convert("L")
        arr = np.array(grayscale_img)

    # Compute normalized values: white (255) becomes 0, non-white pixels become (255 - pixel)/255
    normalized = (255 - arr) / 255.0

    # Create sparse matrix
    return csr_matrix(normalized)


def scale_sparse_matrix_image(
    original_matrix: sp.csr_matrix,
    new_size: int,
    resize_method: int = Image.Resampling.BOX,
) -> sp.csr_matrix:
    """
    Scale a sparse matrix using an image-based approach.
    Converts the matrix to a heatmap image, resizes it, and converts back to a sparse matrix.

    Args:
        original_matrix: The input sparse matrix
        new_size: Desired size of the output matrix
        resize_method: Image resizing method (Image.Resampling.NEAREST, Image.Resampling.BILINEAR,
                     Image.Resampling.BICUBIC, Image.Resampling.LANCZOS, Image.Resampling.BOX)
    """
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Convert matrix to heatmap image
        heatmap_path = os.path.join(temp_dir, "heatmap.png")
        create_heatmap(original_matrix, heatmap_path)

        # Convert to grayscale
        grayscale_path = os.path.join(temp_dir, "heatmap_grayscale.png")
        convert_grayscale(heatmap_path, grayscale_path)

        # Expand the image
        expanded_path = os.path.join(temp_dir, "expanded_heatmap.png")
        expand_image(grayscale_path, new_size, expanded_path, resize_method)

        # Convert back to sparse matrix
        scaled_matrix = image_to_sparse_matrix(expanded_path)

        return scaled_matrix
