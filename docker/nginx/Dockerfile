FROM nginx:stable-alpine

COPY ./docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/nginx/prod/conf.d/ /etc/nginx/conf.d/

RUN chown -R nginx:nginx /etc/nginx/

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]