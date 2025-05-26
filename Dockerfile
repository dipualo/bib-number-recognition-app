# start by pulling the python image
FROM python:3.12-slim

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# Install opencv dependencies and paddleOCR pre-download
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1 libgomp1 wget unzip \
    && rm -rf /var/lib/apt/lists/*

# First install ultralytics without dependencies and CUDA drivers
RUN pip install ultralytics --no-deps
RUN pip install paddlepaddle==3.0.0 -f https://www.paddlepaddle.org.cn/whl/paddlecpu.html
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# Pre-download English and Chinese OCR models to the PaddleOCR default cache directory
RUN python -c "\
from paddleocr import PaddleOCR;\
ocr_en = PaddleOCR(lang='en', use_angle_cls=False, det=False);\
ocr_ch = PaddleOCR(lang='ch', use_angle_cls=False, det=False);"

# copy every content from the local file to the image quitar .venv
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["app.py" ]