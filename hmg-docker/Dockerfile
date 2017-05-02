FROM alpine:edge

# Set build variables
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN echo http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories && \
    apk add --no-cache python libstdc++ lapack-dev libxml2-dev libxslt-dev \
    libjpeg-turbo-dev zlib-dev libpng-dev freetype-dev cython py-numpy-dev \
    py-lxml py-scipy py-pillow uwsgi-python shadow && \
    python -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    apk add --no-cache \
        --virtual=.build-dependencies \
        g++ gfortran musl-dev python-dev && \
    pip install --upgrade pip setuptools && \
    ln -s locale.h /usr/include/xlocale.h && \
    pip install matplotlib && \
    pip install pandas && \
    pip install scikit-learn && \
    pip uninstall --yes cython && \
    rm /usr/include/xlocale.h && \
    rm -r /root/.cache && \
    apk del .build-dependencies && \
    groupadd -f -g $GROUP_ID ub && \
    useradd -o -u $USER_ID -g $GROUP_ID -m ub && \
    mkdir /tests /images && chown -R $USER_ID:$GROUP_ID /tests /images

COPY ./hmg /hmg/
COPY ./default.ini /etc/uwsgi/

RUN chown -R $USER_ID:$GROUP_ID /hmg

# Set a new user
USER ub
WORKDIR /hmg

#CMD [ "/usr/sbin/uwsgi", "--plugins", "python", "--socket",":9090", "--wsgi-file", "/hmg/start.py" ]
CMD [ "/usr/sbin/uwsgi", "--ini", "/etc/uwsgi/default.ini" ]