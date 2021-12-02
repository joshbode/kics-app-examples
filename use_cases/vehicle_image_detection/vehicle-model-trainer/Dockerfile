FROM gw000/keras
WORKDIR /opt/kelvin/app
COPY . /opt/kelvin/app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["/opt/kelvin/app/trainer.py"]