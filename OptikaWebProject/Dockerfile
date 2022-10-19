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


EXPOSE 8000 2222

RUN pip install pytz

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
