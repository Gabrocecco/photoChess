from ultralytics import YOLO

starting_image_link = "test_images/553dbf7c-f1a24b6bb778ee11ba33687415aa84f2_jpg.rf.6e35192bbbb13f887540067e07d5d660.jpg"
#detect pieces with otiginal yolo model 
model_pieces = YOLO("best_piecies.pt")
results_pieces_original = model_pieces.predict(starting_image_link, save=True, iou=0.2, show=False, project="yolo_output_final_warped", name="on_original_perspective", exist_ok=True)