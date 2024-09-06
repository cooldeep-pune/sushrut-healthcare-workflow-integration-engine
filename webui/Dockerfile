FROM php:7.0.33-apache
#COPY config/php.ini /usr/local/etc/php/

RUN docker-php-ext-install mysqli && docker-php-ext-install pdo_mysql
 
# Install Composer
# RUN curl -k -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
#RUN chmod +x /usr/local/bin/
#RUN composer require symfony/yaml

COPY app /var/www/html/
