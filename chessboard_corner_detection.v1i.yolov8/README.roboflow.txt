
chessboard corner detection - v1 2023-05-02 12:22am
==============================

This dataset was exported via roboflow.com on May 1, 2023 at 9:28 PM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand and search unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

For state of the art Computer Vision training notebooks you can use with this dataset,
visit https://github.com/roboflow/notebooks

To find over 100k other datasets and pre-trained models, visit https://universe.roboflow.com

The dataset includes 279 images.
Corner are annotated in YOLOv8 format.

The following pre-processing was applied to each image:
* Auto-orientation of pixel data (with EXIF-orientation stripping)
* Resize to 640x640 (Stretch)

The following augmentation was applied to create 3 versions of each source image:
* Random exposure adjustment of between -27 and +27 percent
* Random Gaussian blur of between 0 and 2.75 pixels
* Salt and pepper noise was applied to 3 percent of pixels

The following transformations were applied to the bounding boxes of each image:
* Random shear of between -15° to +15° horizontally and -15° to +15° vertically


