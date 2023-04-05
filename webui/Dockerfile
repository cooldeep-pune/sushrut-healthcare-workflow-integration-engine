FROM php:7.0-apache

RUN apt-get update && apt-get install -y libpq-dev && docker-php-ext-install pdo pdo_pgsql pgsql
 
# Install Composer
# RUN curl -k -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
#RUN chmod +x /usr/local/bin/
#RUN composer require symfony/yaml

COPY app /var/www/html/
