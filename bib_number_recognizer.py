from ultralytics import YOLO
import supervision as sv
from paddleocr import PaddleOCR
import numpy as np
import logging

logging.getLogger('ppocr').setLevel(logging.ERROR)  # ppocr is the main module


class BibNumberRecognizer:
    def __init__(self):
        self.ocr_ch = PaddleOCR(lang='ch', det=False)
        self.ocr_en = PaddleOCR(lang='en', det=False)
        self.yolo_model = YOLO('./modelo/YOLO/yolov11n_best.pt')

    def get_bib_number_annotations(self, image):
        """
        Returns the image with bib numbers annotated and the detected numbers
        Args:
            image
        Returns:
            annotated_image, bib_numbers
        """

        results = self.yolo_model(image, verbose=False, conf=0.1)[0]
        pred_bounding_boxes = sv.Detections.from_ultralytics(results).with_nms()

        pred_bib_numbers = self.get_bib_numbers(pred_bounding_boxes.xyxy, image)

        unrecognized_bibs = []
        for i, pred_bib_number in enumerate(pred_bib_numbers):
            if pred_bib_number == "Not recognized":
                unrecognized_bibs.append(i)

        pred_bib_numbers = np.delete(pred_bib_numbers, unrecognized_bibs)

        # Remove those indices from all relevant attributes
        pred_bounding_boxes = sv.Detections(
            xyxy=np.delete(pred_bounding_boxes.xyxy, unrecognized_bibs, axis=0),
            confidence=np.delete(pred_bounding_boxes.confidence, unrecognized_bibs, axis=0),
            class_id=np.delete(pred_bounding_boxes.class_id, unrecognized_bibs, axis=0),
            tracker_id=np.delete(pred_bounding_boxes.tracker_id, unrecognized_bibs, axis=0) if pred_bounding_boxes.tracker_id is not None else None,
            data={k: np.delete(v, unrecognized_bibs, axis=0) for k, v in pred_bounding_boxes.data.items()}
        )
        pred_bounding_boxes.data = {'class_name': pred_bib_numbers}

        height, width, _ = image.shape
        size = (height + width) / 2

        text_scale = 0.6 * size / 640
        text_padding = 5 * int(size / 640)
        text_thickness = 2 * int(size / 640)

        box_annotator = sv.BoxAnnotator(thickness=text_thickness)
        label_annotator = sv.LabelAnnotator(text_scale=text_scale, text_padding=text_padding, text_thickness=text_thickness)

        annotated_image = image.copy()
        annotated_image = box_annotator.annotate(scene=annotated_image, detections=pred_bounding_boxes)
        annotated_image = label_annotator.annotate(scene=annotated_image, detections=pred_bounding_boxes)

        # cv2.imwrite(name_image, annotated_image)
        # sv.plot_image(annotated_image)
        return annotated_image, pred_bib_numbers

    def get_bib_numbers(self, bib_boxes, img):
        """
        Given the bib bounding boxes, returns their detected numbers
        Args:
            bib_boxes: bounding boxes of bibs
            img: image containing bibs
        Returns:
            List of detected bib numbers
        """
        bib_numbers = []
        if len(bib_boxes) > 0:
            for bib_box in bib_boxes:
                # Crop out detected bib
                (x_min, y_min, x_max, y_max) = [round(num) for num in bib_box]
                bib_img = img[y_min:y_max, x_min:x_max]

                # Detect numbers on bib using OCR
                pred_ch = self.ocr_ch.ocr(bib_img, det=False, cls=False)
                pred_en = self.ocr_en.ocr(bib_img, det=False, cls=False)

                if pred_en[0][0][1] > pred_ch[0][0][1]:
                    bib_number = pred_en[0][0][0]
                    conf = pred_en[0][0][1]
                else:
                    bib_number = pred_ch[0][0][0]
                    conf = pred_ch[0][0][1]

                bib_number = "".join([c for c in bib_number if c.isdigit()])

                if len(bib_number) > 0 and conf > 0.7:
                    bib_number = bib_number
                else:
                    bib_number = "Not recognized"

                bib_numbers.append(bib_number)

        return bib_numbers