FROM python:3.10.8-bullseye

WORKDIR /app
COPY requirements.txt requirements.txt 

RUN apt update

RUN apt install g++ 
RUN yes | apt install cmake

RUN apt-get install sed

RUN pip install --upgrade pip

RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY . .

ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
  && apt-get install -y --no-install-recommends openssh-server \
  && echo "$SSH_PASSWD" | chpasswd

RUN sed -i -e's/^from keras.engine.topology import get_source_inputs/from keras.utils.layer_utils import get_source_inputs/' /usr/local/lib/python3.10/site-packages/keras_vggface/models.py
ENV APP_CONN "DefaultEndpointsProtocol=https;AccountName=optikaimages;AccountKey=nrYz2nK08cwrcAD3m+7OCxk0ZGLALyVJHECVkdGJlpIpvkaQxIw3E/4iO3CxO01plBfdHcv1Mofq+AStcq9kMg==;EndpointSuffix=core.windows.net"
ENV DEVICE_CONN "HostName=Optika.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=xTjzv3NGMOmWJpNdeumidky+Jk2bCNaU+poEGHnA0rs="



EXPOSE 8000 2222

RUN pip install pytz

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
