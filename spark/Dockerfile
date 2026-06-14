ARG BASE_IMAGE
FROM ${BASE_IMAGE}
USER root
WORKDIR /opt/spark/work
COPY analysis.py /opt/spark/work/analysis.py
COPY data/douban_movies.csv /opt/spark/work/data/douban_movies.csv
