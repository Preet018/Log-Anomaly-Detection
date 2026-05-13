FROM mongo:6.0

# Default environment variables for MongoDB authentication
# These can be overridden in docker-compose.yml or Kubernetes manifests
ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=admin
ENV MONGO_INITDB_DATABASE=logs_db

# If you have initialization scripts (e.g., JS scripts to create collections/indexes),
# you can copy them into the container
COPY init.js /docker-entrypoint-initdb.d/

EXPOSE 27017
