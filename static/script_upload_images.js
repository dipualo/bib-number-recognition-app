const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
const previewContainer = document.getElementById('preview-container');
const files = document.getElementById('files');
const input = document.getElementById('input');
const botonEnviar = document.getElementById('enviar');
const cajagrande = document.getElementById('cajagrande');
const loadingScreen = document.getElementById('loading-screen');
let allImages = [];

// Se activa cuando se pasa el raton por el dragover cambiando el color
function allowDrop(ev) {
    ev.preventDefault();
    files.classList.add('dragover');
}

// Se queda con los elementos soltados
function drop(ev) {

    ev.preventDefault();
    files.classList.remove('dragover');
    
    const files = ev.dataTransfer.files;
    
    if (files.length > 0) {
        input.files = files;
        handleFile(files);   
    }
}

//Comprueba con los ficheros son imagenes y se queda con la primera imagen
function handleFile(files) {

    let hayfilesValido = false;

    for (const file of files) {
        if (!validTypes.includes(file.type)) {
            continue;
        }

        hayfilesValido = true;
        allImages.push(file); // Agregar a la lista acumulada
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.classList.add('preview-item');
            previewContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
    if(hayfilesValido){
        document.getElementById('mensaje').textContent = "Images uploaded successfully";
        document.getElementById('mensaje').style.color = "green";
    }
    else{
        document.getElementById('mensaje').textContent = "Please upload files in PNG, JPG, or JPEG format.";
        document.getElementById('mensaje').style.color = "red";
    }
}


document.getElementById('files').addEventListener('dragleave', function() {
    this.classList.remove('dragover');
});

botonEnviar.addEventListener("click",enviarContenido);

function enviarContenido(ev) {


    if (allImages.length == 0) {
        ev.preventDefault();
    }
    else{
        document.getElementById('estado-mensaje').style.display = 'block';
    
        cajagrande.style.display = 'none';
        loadingScreen.style.display = 'block';
      
        const formData = new FormData();
        allImages.forEach((file) => {
            formData.append('images',file);
        });
    
        console.log("Enviando imágenes:", allImages.map(file => file.name));
    
        fetch('/upload_images', {
            method: 'POST',
            body: formData
        }).then(() => {
            // Redirige cuando termine
            window.location.href = '/search_images';
          }).catch(err => {
            alert("Error al enviar imágenes");
            console.error(err);
            // Restaurar vista en caso de error
            loadingScreen.style.display = 'none';
            mainContent.style.display = 'block';
          });
    
        allImages=[];   
    }
}