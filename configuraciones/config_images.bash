REGION=us-central1
PROJECT=alpespartner
REPO=alp-repo

gcloud artifacts repositories create $REPO \
  --repository-format=docker --location=$REGION

gcloud auth configure-docker $REGION-docker.pkg.dev -q

# Build & push
docker build -f ../deploy/docker/alpespartners.Dockerfile \
  -t $REGION-docker.pkg.dev/$PROJECT/$REPO/cliente:v1 \
  ..
docker push  $REGION-docker.pkg.dev/$PROJECT/$REPO/cliente:v1

docker build -f ../deploy/docker/alpespartners.Dockerfile \
   -t $REGION-docker.pkg.dev/$PROJECT/$REPO/campanias:v1 \
  ..
docker push  $REGION-docker.pkg.dev/$PROJECT/$REPO/campanias:v1

docker build -f ../deploy/docker/alpespartners.Dockerfile \
  -t $REGION-docker.pkg.dev/$PROJECT/$REPO/pagos:v1 \
  ..
docker push  $REGION-docker.pkg.dev/$PROJECT/$REPO/pagos:v1

docker build -f ../deploy/docker/alpespartners.Dockerfile \
  -t $REGION-docker.pkg.dev/$PROJECT/$REPO/bff:v1 \
  ..
docker push  $REGION-docker.pkg.dev/$PROJECT/$REPO/bff:v1