FROM coolq/wine-coolq:latest

COPY vncmain.sh /app/vncmain.sh
RUN chmod +x /app/vncmain.sh
COPY get-http-api-plugin.py /home/user/get-http-api-plugin.py
RUN echo "\n\n/usr/bin/python3 /home/user/get-http-api-plugin.py" >> /etc/cont-init.d/110-get-coolq

EXPOSE 5700

VOLUME ["/home/user/coolq"]