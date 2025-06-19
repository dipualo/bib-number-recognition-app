# Visión Artificial aplicada a la detección y reconocimiento de dorsales en competiciones deportivas

Este proyecto está basado en un TFG de infórmatica de la univerisidad de Valladolid.

## Resumen del proyecto

A partir de este proyecto, se busca desarrollar un sistema de reconocimiento de dorsales, junto con una aplicación web que permita comprobar su funcionamiento. Dicha aplicación permitirá enviar imágenes al sistema de reconocimiento, buscar imágenes por número de dorsal y visualizar las predicciones realizadas por el reconocedor.

## Uso de la aplicación

Al iniciar la aplicación, se muestra una pantalla desde la cual se pueden enviar imágenes al sistema de reconocimiento de dorsales. Además, es posible navegar hacia otras secciones para buscar imágenes por número de dorsal y visualizar las predicciones realizadas por el modelo.

![Enviar imagenes](img_README/app_cargar_imagenes.png)

En la pantalla de búsqueda, se pueden localizar imágenes filtrándolas por los dorsales que contengan.

![Busqueda por dorsal](img_README/app_buscar_imagenes.png)

En la pantalla de visualización, se muestran las predicciones generadas por el modelo, lo que permite evaluar su rendimiento sobre imágenes específicas. También se ofrece la opción de borrar imágenes del sistema.

![Ver predicciones](img_README/app_ver_prediciones.png)


## Resultados

Para la creación del modelo de reconocimiento de dorsales se utilizaron 904 imágenes que contenían un total de 1.518 dorsales. El modelo fue desarrollado empleando YOLOv11n junto con PaddleOCR. En las pruebas realizadas con un esquema de validación cruzada de 3 particiones (3-fold), se obtuvo un valor de F1-score de 0,839 en los conjuntos de prueba.

## Requisitos

- Tener [Docker](https://www.docker.com/) instalado.

## Instalar aplicación

Sigue los siguientes pasos para clonar el repositorio, construir la imagen de Docker y ejecutar la aplicación:

```bash
git clone https://github.com/dipualo/app_reconocimiento_dorsales.git
cd app_reconocimiento_dorsales
docker build -t app_reconocedor_dorsales .
docker run -it --rm -p 5000:5000 app_reconocedor_dorsales
```

## Autor y contacto

**Autor:** Diego de la Puente Alonso  
**Correo electrónico:** [diego@delapuente.es](mailto:diego@delapuente.es)
