from flask import Flask, render_template, request, redirect, url_for, Response
import os
import shutil
from bib_number_recognizer import *
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

ruta_imagenes_uploaded='static/image_folders/uploaded'

for filename in os.listdir(ruta_imagenes_uploaded):
    
    file_path = os.path.join(ruta_imagenes_uploaded, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  
    except Exception as e:
        print(f'Error eliminando {file_path}: {e}')

bib_number_recognizer = BibNumberRecognizer()

ruta_imagenes_anotated='static/image_folders/anotated'

for filename in os.listdir(ruta_imagenes_anotated):

    file_path = os.path.join(ruta_imagenes_anotated, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  
    except Exception as e:
        print(f'Error eliminando {file_path}: {e}')

if(not os.path.exists(ruta_imagenes_uploaded)):
    os.mkdir(ruta_imagenes_uploaded)

if(not os.path.exists(ruta_imagenes_anotated)):
    os.mkdir(ruta_imagenes_anotated)

@app.route('/')
def index():
    return redirect(url_for('upload_images'))

@app.route('/search_images')
def search_images():
    images_bibs = Image_bib.query.all()
    query = request.args.get('query', '')
    if query:
        images_with_that_bib = Image_bib.query.filter(Image_bib.bib_number==query).all()
    else:
        images_with_that_bib = None
    return render_template('search_images.html', images_bibs=images_bibs, images_with_that_bib = images_with_that_bib, query = query)

@app.route('/view_images')
def view_images():
    imagenes = os.listdir(ruta_imagenes_anotated)
    return render_template('view_images.html', imagenes=imagenes)

@app.route('/borrar', methods=['POST'])
def borrar():
    seleccionadas = request.form.getlist('images_to_delete')
    for imagen in seleccionadas:
        ruta = os.path.join(ruta_imagenes_anotated, imagen)
        if os.path.exists(ruta):
            os.remove(ruta)

        nombre_imagen = imagen[11:]
        Image_bib.query.filter_by(image=nombre_imagen).delete()
        db.session.commit()

    return redirect(url_for('view_images'))


@app.route('/upload_images', methods=['GET', 'POST'])
def upload_images():

    if request.method == 'POST':

        filess = request.files.getlist('images')
        nums_dorsales_imgs = []

        for files in filess:
            
            # Leer imagen como numpy array
            npimg = np.frombuffer(files.read(), np.uint8)
            imagen = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

            filename = files.filename
            try:
                cv2.imwrite("./static/image_folders/uploaded/"+filename, imagen)
            except Exception as e:
                print(f'Ocurrió un error al guardar la imagen: {e}')
            
            img_anotada, nums_dorsales = bib_number_recognizer.get_bib_number_annotations(imagen)

            for num in nums_dorsales:
                nums_dorsales_imgs.append(num)
                new_image_bib = Image_bib(image = filename, bib_number = num)

                db.session.add(new_image_bib)

            db.session.commit()

            resultado_filename = f'prediction_{filename}'
            try:
                cv2.imwrite("./static/image_folders/anotated/"+resultado_filename, img_anotada)
            except Exception as e:
                print(f'Ocurrió un error al guardar la imagen: {e}')
        
        return redirect(url_for('search_images'))
        
    return render_template('upload_images.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)