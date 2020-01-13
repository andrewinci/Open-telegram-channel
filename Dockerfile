FROM python:3.7.6-alpine3.10
ENV LOCAL=LOCAL
ADD scraper.py scraper.py

RUN apk add --update --no-cache g++ gcc libxslt-dev
RUN pip3 install lxml boto3

CMD watch -n 180 "python3 scraper.py"