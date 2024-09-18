# pull python base image
FROM python:3.12.6-slim

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

# install packages specified in requirements.txt
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x entrypoint.sh

# copy local project directory to the container
COPY . .

# run entrypoint
ENTRYPOINT [ "/app/entrypoint.sh" ]