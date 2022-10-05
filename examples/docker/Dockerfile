FROM python:3.10

RUN pip install AutoTransform
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR repo

CMD ./autotransform/docker_autotransform.sh
