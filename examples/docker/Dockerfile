FROM python:3.10

ARG COMMAND
ARG REPO_DIR
ENV env_command $COMMAND

COPY requirements.txt requirements.txt
RUN pip install AutoTransform
RUN pip install -r requirements.txt

WORKDIR $REPO_DIR

CMD ./autotransform/docker_autotransform.sh $env_command