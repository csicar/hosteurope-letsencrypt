FROM mcr.microsoft.com/playwright:v1.27.0-focal

RUN apt-get update && apt-get install --yes pipenv python3
COPY ./ /app
WORKDIR /app
RUN pipenv install --python 3.8

