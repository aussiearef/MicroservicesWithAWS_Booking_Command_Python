FROM python

COPY . /

RUN pip3 install boto3
RUN pip3 install pyjwt
RUN pip3 install fastapi
RUN pip3 install uvicorn

# Download CURL for Health Check
RUN apt update -y
RUN apt upgrade -y
RUN apt install -y curl 

ENV tableName=Booking
EXPOSE 80
ENTRYPOINT [ "python", "Booking-Command.py"]


