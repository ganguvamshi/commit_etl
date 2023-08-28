FROM postgres:latest

ARG DB_USER
ARG DB_PASSWD
ARG DB_NAME

# Set environment variables for PostgreSQL
ENV POSTGRES_USER=$DB_USER
ENV POSTGRES_PASSWORD=$DB_PASSWD
ENV POSTGRES_DB=$DB_NAME

# Copy the SQL script containing DDL statements to the container
COPY setup.sql /docker-entrypoint-initdb.d/init.sql

# Expose the default PostgreSQL port (5432)
EXPOSE 5432