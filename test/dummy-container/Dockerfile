FROM python:3.5

RUN pip install pyramid
RUN pip install httpie
ADD . /src
WORKDIR /src
CMD python pyramid_app.py

EXPOSE 8080
