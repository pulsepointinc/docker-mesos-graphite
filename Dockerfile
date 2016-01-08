FROM centos:7

CMD ["/metrics.py"]

RUN \
  curl -s -L "https://raw.github.com/pypa/pip/master/contrib/get-pip.py" | python && \
  pip install requests

ADD ./metrics.py /metrics.py
