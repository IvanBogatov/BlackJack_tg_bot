FROM python:slim
ENV TOKEN='<YOUR TOKEN>'
COPY . .
RUN pip install -r requirements.txt
CMD python bot.py