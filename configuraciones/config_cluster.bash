gcloud services enable container.googleapis.com artifactregistry.googleapis.com

gcloud container clusters create-auto alpes-gke --region us-central1

gcloud container clusters get-credentials alpes-gke --region us-central1