# Chess Pieces > 416x416_aug
https://universe.roboflow.com/joseph-nelson/chess-pieces-new

Provided by [Roboflow](https://roboflow.ai)
License: Public Domain

# Overview

This is a dataset of Chess board photos and various pieces. All photos were captured from a constant angle, a tripod to the left of the board. The bounding boxes of all pieces are annotated as follows: `white-king`, `white-queen`, `white-bishop`, `white-knight`, `white-rook`, `white-pawn`, `black-king`, `black-queen`, `black-bishop`, `black-knight`, `black-rook`, `black-pawn`. There are 2894 labels across 292 images.

![Chess Example](https://i.imgur.com/nkjobw1.png)

**Follow [this tutorial](https://blog.roboflow.ai/training-a-yolov3-object-detection-model-with-a-custom-dataset/) to see an example of training an object detection model using this dataset or jump straight to the [Colab notebook](https://colab.research.google.com/drive/1ByRi9d6_Yzu0nrEKArmLMLuMaZjYfygO#scrollTo=WgHANbxqWJPa).**

# Use Cases

At Roboflow, we built a chess piece object detection model using this dataset.

![ChessBoss](https://blog.roboflow.ai/content/images/2020/01/chess-detection-longer.gif)

You can see a video demo of that [here](https://www.youtube.com/watch?v=XLispu-Yb_0). (We did struggle with pieces that were occluded, i.e. the state of the board at the very beginning of a game has many pieces obscured - let us know how your results fare!)

# Using this Dataset

We're releasing the data free on a public license.

# About Roboflow

[Roboflow](https://roboflow.ai) makes managing, preprocessing, augmenting, and versioning datasets for computer vision seamless.

Developers reduce 50% of their boilerplate code when using Roboflow's workflow, save training time, and increase model reproducibility.

#### [![Roboflow Workmark](https://i.imgur.com/WHFqYSJ.png =350x)](https://roboflow.ai)

