FROM jupyter/datascience-notebook:latest

RUN conda install requests

ENV JUPYTER_ENABLE_LAB=yes