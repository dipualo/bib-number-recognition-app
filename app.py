# Imports necesarios
from flask import Flask, render_template, request, redirect, url_for, Response
import os
import shutil
from reconocedor_dorsales import *
import cv2
from flask_sqlalchemy import SQLAlchemy
from models import db, Image_bib

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.drop_all() 
    db.create_all()

# Ruta a donde se almacenan las imagenes que se cargan
ruta_imagenes_enviadas='static/carpetas_imagenes/enviadas'

for filename in os.listdir(ruta_imagenes_enviadas):
    if filename == ".gitkeep":
        continue  # Saltar este archivo

    file_path = os.path.join(ruta_imagenes_enviadas, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # Borra archivos o enlaces simbólicos
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # Borra carpetas y su contenido
    except Exception as e:
        print(f'Error eliminando {file_path}: {e}')

reconocedor_dorsales = ReconocedorDorsales()

# Ruta a donde se almacenan las imagenes resultado
ruta_imagenes_anotadas='static/carpetas_imagenes/anotadas'

for filename in os.listdir(ruta_imagenes_anotadas):
    if filename == ".gitkeep":
        continue  # Saltar este archivo

    file_path = os.path.join(ruta_imagenes_anotadas, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # Borra archivos o enlaces simbólicos
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # Borra carpetas y su contenido
    except Exception as e:
        print(f'Error eliminando {file_path}: {e}')

# Si no existe ese path lo crea
if(not os.path.exists(ruta_imagenes_enviadas)):
    os.mkdir(ruta_imagenes_enviadas)

if(not os.path.exists(ruta_imagenes_anotadas)):
    os.mkdir(ruta_imagenes_anotadas)

@app.route('/')
def index():
    return redirect(url_for('enviar_imagenes'))

@app.route('/buscar_imagenes')
def buscar_imagenes():
    images_bibs = Image_bib.query.all()
    query = request.args.get('query', '')
    if query:
        images_with_that_bib = Image_bib.query.filter(Image_bib.bib_number==query).all()
    else:
        images_with_that_bib = None
    return render_template('buscar_imagenes.html', images_bibs=images_bibs, images_with_that_bib = images_with_that_bib, query = query)

@app.route('/ver_imagenes')
def ver_imagenes():
    imagenes = os.listdir(ruta_imagenes_anotadas)
    return render_template('ver_imagenes.html', imagenes=imagenes)

@app.route('/borrar', methods=['POST'])
def borrar():
    seleccionadas = request.form.getlist('imagenes_a_borrar')
    for imagen in seleccionadas:
        ruta = os.path.join(ruta_imagenes_anotadas, imagen)
        if os.path.exists(ruta):
            os.remove(ruta)

        # Elimino el prediction_ de la imagen
        nombre_imagen = imagen[11:]
        print(nombre_imagen)
        Image_bib.query.filter_by(image=nombre_imagen).delete()
        db.session.commit()

    return redirect(url_for('ver_imagenes'))


@app.route('/enviar_imagenes', methods=['GET', 'POST'])
def enviar_imagenes():

    if request.method == 'POST':

        # Deberia de ir todo bien
        archivos = request.files.getlist('images')
        nums_dorsales_imgs = []

        for archivo in archivos:
            
            # Leer imagen como numpy array
            npimg = np.frombuffer(archivo.read(), np.uint8)
            imagen = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

            filename = archivo.filename
            try:
                cv2.imwrite("./static/carpetas_imagenes/enviadas/"+filename, imagen)
            except Exception as e:
                print(f'Ocurrió un error al guardar la imagen: {e}')
            
            # Pasarla al reconocedor de dorsales
            img_anotada, nums_dorsales = reconocedor_dorsales.get_anotaciones_dorsales(imagen)

            for num in nums_dorsales:
                nums_dorsales_imgs.append(num)
                new_image_bib = Image_bib(image = filename, bib_number = num)

                # Add to session and commit to DB
                db.session.add(new_image_bib)

            db.session.commit()

            resultado_filename = f'prediction_{filename}'
            try:
                cv2.imwrite("./static/carpetas_imagenes/anotadas/"+resultado_filename, img_anotada)
            except Exception as e:
                print(f'Ocurrió un error al guardar la imagen: {e}')
        
        return redirect(url_for('buscar_imagenes'))
        
    return render_template('enviar_imagenes.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)