FROM nginx:1.27-alpine

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY . /app

EXPOSE 5000

CMD ["nginx", "-g", "daemon off;"]
