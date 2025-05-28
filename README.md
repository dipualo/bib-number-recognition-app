# Visión Artificial aplicada a la detección y reconocimiento de dorsales en competiciones deportivas

Este proyecto está basado en un TFG de infórmatica de la univerisidad de Valladolid.

## Resumen del proyecto

Los dorsales en competiciones deportivas están compuestos por un rectángulo de distintos
tamaños y colores, con un número identificativo y con formato variado que se utiliza para identificar
a los participantes en eventos deportivos, especialmente en carreras. Todo esto con el objetivo de
saber que el deportista está inscrito en la competición y facilitar la creación de clasificaciones de
los participantes.
En este trabajo, mediante Visión por Computadora, se buscará detectar y reconocer dorsales.
Esto se hará explorando modelos de detección de objetos como YOLO y distintos OCR para
reconocer la información alfanumérica del dorsal.
El objetivo principal de este trabajo es desarrollar una aplicación capaz de clasificar imágenes de
competiciones deportivas, facilitando así la localización de fotografías dentro de grandes álbumes.
Así mismo, al disponer de la fecha y hora de la foto, se puede usar para confeccionar clasificaciones
parciales.

## Resultados

Se ha utilizado utiliza para crear el modelo de reconocimiento de dorsales 935 imágenes con 1627 dorsales. Este modelo se ha creado usando YOLOv11n y paddleOCR y
se alcanza un valor de F1-score de 0.828 en los conjuntos de test de un 3 k-fold. 

## Requisitos

- Tener [Docker](https://www.docker.com/) instalado.

## Uso

Sigue los siguientes pasos para clonar el repositorio, construir la imagen de Docker y ejecutar la aplicación:

```bash
git clone https://github.com/dipualo/app_reconocimiento_dorsales.git
cd app_reconocimiento_dorsales
docker build -t app_reconocedor_dorsales .
docker run -it --rm app_reconocedor_dorsales

## Autor y contacto

**Autor:** Diego de la Puente Alonso  
**Correo electrónico:** [diego@delapuente.es](mailto:diego@delapuente.es)
