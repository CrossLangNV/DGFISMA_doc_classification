FROM ubuntu:18.04

MAINTAINER arne <arnedefauw@gmail.com>

#ARG MODEL_PATH

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
 && rm -rf /var/lib/apt/lists/*


ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh
RUN bash Miniconda3-py37_4.8.2-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-py37_4.8.2-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

RUN conda install -y python=3.7.3
RUN conda install flask==1.1.1
#RUN conda install --name base scikit-learn=0.20.0
RUN conda install pandas=1.0.1

#Install Cython
RUN apt-get update
RUN apt-get -y install --reinstall build-essential
RUN apt-get -y install gcc

RUN pip install Cython==0.29.19 bs4==0.0.1 beautifulsoup4==4.5.3 numpy==1.16.0 scikit-learn==0.20.0 ipython jupyter jupyterlab

EXPOSE 8888

VOLUME /notebook
WORKDIR /notebook

CMD ["jupyter", "notebook", "--no-browser", "--allow-root", "--ip='0.0.0.0'"]

#WORKDIR /work
#COPY cleaning.py /work
#COPY app.py /work

#COPY $MODEL_PATH /work/models/model.p

#WORKDIR /work

#CMD python /work/app.py


