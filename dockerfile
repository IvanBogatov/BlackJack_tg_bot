FROM python:slim
ENV TOKEN='5304168272:AAG7YX1-SVpWvBYiuWONCsXT70nMncDlN_4'
COPY . .
RUN pip install -r requirements.txt
CMD python bot.py