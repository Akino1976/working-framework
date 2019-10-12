FROM akino1976/rocker-rbase-ext:latest

COPY . /usr/src

WORKDIR /usr/src/analysis

EXPOSE 1433

RUN install2.r --error \
    jsonlite


#RUN Rscript /usr/src/analysis/main.R
ENTRYPOINT [ "R" ]
CMD [ "/usr/src/analysis/main.R" ]
