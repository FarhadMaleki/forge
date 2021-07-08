import itertools
import os
from typing import Union

import numpy as np
import SimpleITK as sitk


def refrence_free_3D_resample(image, transformation=None,
                              interpolator=sitk.sitkBSpline,
                              default_value=0,
                              image_voxel_type=None,
                              spacing=None,
                              direction=None):
    """Do resampling without reference.

    Args:
        image: A SimpleITK image.
        transformation: A transformation to be applied to the image. If None,
            The identity transformation is used.
        interpolator: he interpolator used for image interpolation after
            applying transformation. The default is ``sitk.sitkBSpline``.
        default_value: The default values used for voxel values. The default is
            ``0``.
        image_voxel_type: The data type used for casting the resampled image.
            f None, the voxel type of the ``image`` is used.
        spacing: The spacing of the image after resampling.
        direction: The direction of the image after resampling.

    Returns:

    """
    if transformation is None:
        # The default is the identity transformation
        transformation = sitk.Transform(image.GetDimension(), sitk.sitkIdentity)
    if image_voxel_type is None:
        image_voxel_type = image.GetPixelIDValue()
    if spacing is None:
        spacing = image.GetSpacing()
    if direction is None:
        direction = image.GetDirection()
    extreme_indecies = list(itertools.product(*zip([0, 0, 0], image.GetSize())))
    extreme_points = [image.TransformIndexToPhysicalPoint(idx)
                      for idx in extreme_indecies]
    inv_transform = transformation.GetInverse()
    # Calculate the coordinates of the inversed extream points
    extreme_points_transformed = [inv_transform.TransformPoint(point)
                                  for point in extreme_points]
    min_values = np.array(extreme_points_transformed).min(axis=0)
    max_values = np.array(extreme_points_transformed).max(axis=0)
    # Minimal x,y, and coordinates are the new origin.
    origin = min_values.tolist()
    # Compute grid size based on the physical size and spacing.
    size = [int((max_val - min_val) / s)
            for min_val, max_val, s in zip(min_values, max_values, spacing)]
    return sitk.Resample(image, size, transformation, interpolator,
                         outputOrigin=origin,
                         outputSpacing=spacing,
                         outputDirection=direction,
                         defaultPixelValue=default_value,
                         outputPixelType=image_voxel_type)


def referenced_3D_resample(image,
                           transformation=None,
                           interpolator=sitk.sitkBSpline,
                           default_value=0,
                           image_voxel_type=None,
                           reference=None):
    """Do resampling using a given reference.

    Args:
        image: A simpleITK image.
        transformation: A transformation to be applied to the image. The
            default is None, representing the identity transformation.
        interpolator: The interpolator used for image interpolation after
            applying transformation. If None, the default value is used. The
            default value is ``sitk.sitkBSpline``.
        default_value: The default value used for voxel values. The default
            value is ``0``.
        image_voxel_type: The data type used for casting the resampled image.
            If None, the voxel type of the ``image`` is used as the voxel
            type of the result.
        reference: The image used as the reference for resampling. If None,
            the image itself is used as the reference.

    Returns:
        sitk.Image: The resampled image.

    """
    if reference is None:
        reference = image
    if transformation is None:
        # The default is the identity transformation
        transformation = sitk.Transform(image.GetDimension(), sitk.sitkIdentity)
    if image_voxel_type is None:
        image_voxel_type = image.GetPixelIDValue()
    return sitk.Resample(image, reference, transformation, interpolator,
                         default_value, image_voxel_type)


def image_equal(image1: sitk.Image, image2: sitk.Image, type_check=True,
                tolerance=1e-6):
    """Check if two images are equal.

    Data type, size, and content are used for comparison. Two image with the
    L2 distance less than a tolerance value are considered equal.

    Args:
        image1: A SimpleITK image.
        image2: A SimpleITK image.
        type_check: True is data type is used for comparison.
        tolerance: The threshold used for the acceptable deviation between the
            euclidean distance of voxel values between the two images.

    Returns:
        bool: True if two images are equal; otherwise, False.

    """
    if type_check is True:
        # Check for equality of voxel types
        if image1.GetPixelIDValue() != image2.GetPixelIDValue():
            return False
    if image1.GetDimension() != image2.GetDimension():
        return False
    if image1.GetSize() != image2.GetSize():
        return False
    # Check the equality of image spacings
    if np.linalg.norm(np.array(image1.GetSpacing()) -
                      np.array(image2.GetSpacing())) > tolerance:
        return False
    # Check the equality of image origins
    if np.linalg.norm(np.array(image1.GetOrigin()) -
                      np.array(image2.GetOrigin())) > tolerance:
        return False
    # Check the array equality
    arry1 = sitk.GetArrayFromImage(image1)
    arry2 = sitk.GetArrayFromImage(image2)
    if np.linalg.norm(arry1 - arry2) > tolerance:
        return False
    return True


def read_image(image_path: Union[str, None]):
    """ Read an image.

    Args:
        image_path: The path to the image file or the folder containing a DICOM image.

    Returns:
        sitk.Image: A SimpleITK Image.

    Raises:
        ValueError: if there exist more than one image series or if there is no
            DICOM file in the provided ``path``.

    """
    if not os.path.exists(image_path):
        raise ValueError(f'Path does not exist: {image_path}')
    if os.path.isdir(image_path):
        reader = sitk.ImageSeriesReader()
        series_IDs = reader.GetGDCMSeriesIDs(image_path)
        if len(series_IDs) > 1:
            msg = ('Only One image is allowed in a directory. There are '
                   f'{len(series_IDs)} Series IDs (images) in {image_path}.')
            raise ValueError(msg)
        if len(series_IDs) == 0:
            msg = f'There are not dicom files in {image_path}.'
            raise ValueError(msg)
        series_id = series_IDs[0]
        dicom_names = reader.GetGDCMSeriesFileNames(image_path, series_id)
        reader.SetFileNames(dicom_names)
        image = reader.Execute()
    elif os.path.isfile(image_path):
        image = sitk.ReadImage(image_path)
    else:
        raise ValueError(f'Invalid path: {image_path}')
    return image


def get_stats(image):
    """Computes minimum, maximum, sum, mean, variance, and standard deviation of
        an image.
    Args:
        image: A sitk.Image object.

    Returns:
        returns statistical values of type dictionary include keys 'min',
            'max', 'mean', 'std', and 'var'.
    """
    stat_fileter = sitk.StatisticsImageFilter()
    stat_fileter.Execute(image)
    image_info = {}
    image_info.update({'min': stat_fileter.GetMinimum()})
    image_info.update({'max': stat_fileter.GetMaximum()})
    image_info.update({'mean': stat_fileter.GetMean()})
    image_info.update({'std': stat_fileter.GetSigma()})
    image_info.update({'var': stat_fileter.GetVariance()})
    return image_info


def check_dimensions(image, mask):
    """Check if the size of the image and mask are equal.

    Args:
        image: A sitk.Image.
        mask: A sitk.Image.

    Raises:
        ValueError: If image and mask are not None and their dimension are
            not the same.
    """
    if (mask is not None) and (image is not None):
        if image.GetSize() != mask.GetSize():
            img_size_message = ', '.join([str(x) for x in image.GetSize()])
            msk_size_message = ', '.join([str(x) for x in mask.GetSize()])
            msg = ('image and mask size should be equal,'
                   ' but ({}) != ({}).'.format(img_size_message,
                                               msk_size_message))
            raise ValueError(msg)


class Label(object):
    """Label a binary image.

    Each distinct connected component (segment) is assigned a unique label. The
        segment labels start from 1 and are consecutive. The order of
        label assignment is based on the the raster position of the
        segments in the binary image.

    Args:
        fully_connected:
        input_foreground_value:
        output_background_value:
        dtype: The data type for the label map. Options include:
            * sitk.sitkUInt8
            * sitk.sitkUInt16
            * sitk.sitkUInt32
            * sitk.sitkUInt64

    """
    def __init__(self, fully_connected: bool = False,
                 input_foreground_value: int = 1,
                 output_background_value: int = 0,
                 dtype=sitk.sitkUInt8):
        self.input_foreground_value = input_foreground_value
        self.output_background_value = output_background_value
        self.fully_connected = fully_connected
        self.dtype = dtype

    def __call__(self, binary_image):
        mask = sitk.BinaryImageToLabelMap(
            binary_image,
            fullyConnected=self.fully_connected,
            inputForegroundValue=self.input_foreground_value,
            outputBackgroundValue=self.output_background_value)

        mask = sitk.Cast(mask, pixelID=self.dtype)
        return mask

    def __repr__(self):
        msg = ('{} (fully_connected={}, input_foreground_value={}, '
               'output_background_value={}, dtype={}')
        return msg.format(self.__class__.__name__,
                          self.fully_connected,
                          self.input_foreground_value,
                          self.output_background_value,
                          self.dtype)
