from ultralytics import YOLO
import supervision as sv
from paddleocr import PaddleOCR
import numpy as np
import logging

logging.getLogger('ppocr').setLevel(logging.ERROR)  # ppocr es el módulo principal


class ReconocedorDorsales:
    def __init__(self):
        self.ocr_ch = PaddleOCR(lang = 'ch', det = False)
        self.ocr_en = PaddleOCR(lang='en', det = False)
        self.modelo_yolo = YOLO('./modelo/YOLO/yolov11n_best.pt')

    def get_anotaciones_dorsales(self, image):
        """
        Devuelve la imagen con los numeros de los dorsales anotados y los numeros
        Args
            ruta_image
        Returns
            imagen_anotada
        """

        results = self.modelo_yolo(image, verbose = False, conf=0.1)[0]
        pred_bounding_boxes = sv.Detections.from_ultralytics(results).with_nms()

        pred_numeros_dorsales= self.get_numeros_dorsales(pred_bounding_boxes.xyxy, image)

        dorsales_no_reconocidos = []
        for i ,pred_numeros_dorsal in enumerate(pred_numeros_dorsales):
            if(pred_numeros_dorsal == "No reconocido"):
                dorsales_no_reconocidos.append(i)


        pred_numeros_dorsales = np.delete(pred_numeros_dorsales, dorsales_no_reconocidos)   

        # Eliminar esos índices en todos los atributos relevantes
        pred_bounding_boxes = sv.Detections(
            xyxy=np.delete(pred_bounding_boxes.xyxy, dorsales_no_reconocidos, axis=0),
            confidence=np.delete(pred_bounding_boxes.confidence, dorsales_no_reconocidos, axis=0),
            class_id=np.delete(pred_bounding_boxes.class_id, dorsales_no_reconocidos, axis=0),
            tracker_id=np.delete(pred_bounding_boxes.tracker_id, dorsales_no_reconocidos, axis=0) if pred_bounding_boxes.tracker_id is not None else None,
            data={k: np.delete(v, dorsales_no_reconocidos, axis=0) for k, v in pred_bounding_boxes.data.items()}
        )
        pred_bounding_boxes.data = {'class_name': pred_numeros_dorsales}

        height, width, _ = image.shape

        size = (height+width)/2

        text_scale = 0.6*size/640
        text_padding = 5*int(size/640)
        text_thickness= 2*int(size/640)


        pred_box_annotator = sv.BoxAnnotator(thickness=text_thickness)
        pred_label_annotator = sv.LabelAnnotator(text_scale = text_scale, text_padding = text_padding, text_thickness=text_thickness)

        imagen_anotada = image.copy()

        imagen_anotada = pred_box_annotator.annotate(scene=imagen_anotada, detections = pred_bounding_boxes)
        imagen_anotada = pred_label_annotator.annotate(scene=imagen_anotada, detections = pred_bounding_boxes)

        # cv2.imwrite(name_image, imagen_anotada)
        # sv.plot_image(imagen_anotada)
        return(imagen_anotada, pred_numeros_dorsales)

    def get_numeros_dorsales(self, cajas_dorsales, img):
        """
        Dado las cajas de los dorsales devuelve sus numeros
        Args
            bounding boxes dorsales
            imagen de los dorsales    
            OCRs a usar para reconocer los dorsales
        Returns
            Lista con los numeros de los dorsales
        """
        numeros_dorsales = []
        if len(cajas_dorsales) > 0:
            for caja_dorsal in cajas_dorsales:
                # crop out detected bib
                (x_min, y_min, x_max, y_max) = [round(num) for num in caja_dorsal]
                img_dorsal = img[y_min:y_max, x_min:x_max]
                
                # detect numbers on bib
                #bib_number = pytesseract.image_to_string(crop_img, config=r"--oem 3 --psm 7 outputbase digits")
                rbn_pred_ch = self.ocr_ch.ocr(img_dorsal, det = False, cls = False)
                rbn_pred_en = self.ocr_en.ocr(img_dorsal, det = False, cls = False)
            
                if(rbn_pred_en[0][0][1]>rbn_pred_ch[0][0][1]):
                    bib_number = rbn_pred_en[0][0][0]
                    conf = rbn_pred_en[0][0][1]
                else:
                    bib_number = rbn_pred_ch[0][0][0]
                    conf = rbn_pred_ch[0][0][1]
                    
                bib_number = "".join([c for c in bib_number if c.isdigit()])

                if(len(bib_number)>0 and conf>0.4):
                    bib_number = bib_number
                else:
                    bib_number = "No reconocido"

                numeros_dorsales.append(bib_number)
                
        return numeros_dorsales