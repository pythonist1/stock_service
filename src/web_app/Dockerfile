FROM nginx:alpine


# Копируем основной конфигурационный файл nginx
COPY ./nginx.conf /etc/nginx/nginx.conf

# Копируем дополнительные конфигурации
COPY ./conf.d /etc/nginx/conf.d

# Копируем статические файлы веб-приложения
COPY ./ /usr/share/nginx/html
