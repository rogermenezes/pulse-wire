# PulseWire Terraform (GCP)

This Terraform stack provisions production-ready starter infrastructure for PulseWire on Google Cloud.

## What It Provisions

- Artifact Registry repositories for frontend, backend, and worker images
- VPC networking and subnetwork
- Serverless VPC Access connector (Cloud Run -> private resources)
- Private Service Access for managed services
- Cloud SQL for PostgreSQL (private IP)
- Memorystore for Redis (private IP)
- Secret Manager secret containers (no secret values)
- Runtime service accounts and least-privilege IAM bindings
- Cloud Run service for frontend
- Cloud Run service for backend
- Optional Cloud Run Job for worker tasks

## Folder Layout

- `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`, `versions.tf`
- `terraform.tfvars.example`
- `modules/`
  - `artifact_registry`
  - `service_accounts`
  - `networking`
  - `cloud_sql`
  - `memorystore`
  - `secret_manager`
  - `cloud_run_service`
  - `cloud_run_job`

## Prerequisites

- Terraform `>= 1.6`
- `gcloud` CLI authenticated to target project
- Billing enabled on project
- Permissions to create Cloud Run, Cloud SQL, VPC, Redis, IAM, Artifact Registry, Secret Manager resources

## Required GCP APIs

The stack enables these APIs automatically:

- `artifactregistry.googleapis.com`
- `run.googleapis.com`
- `compute.googleapis.com`
- `vpcaccess.googleapis.com`
- `servicenetworking.googleapis.com`
- `sqladmin.googleapis.com`
- `redis.googleapis.com`
- `secretmanager.googleapis.com`
- `iam.googleapis.com`
- `cloudbuild.googleapis.com`

## Configure Variables

1. Copy example vars:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
```

2. Edit values in `terraform.tfvars`:

- `project_id`, `region`, `environment`
- `frontend_image`, `backend_image`, `worker_image`
- optional sizing and scaling settings
- env/secret mappings per service

## Terraform Workflow

From `infra/terraform`:

```bash
terraform init
terraform validate
terraform plan -out tfplan
terraform apply tfplan
```

Destroy (careful in prod):

```bash
terraform destroy
```

## Outputs

After apply, key outputs include:

- `frontend_service_url`
- `backend_service_url`
- `cloud_sql_connection_name`
- `cloud_sql_private_ip`
- `database_name`
- `redis_host`, `redis_port`
- `artifact_registry_repositories`
- `service_accounts`
- `worker_job_name`

## Manual Steps After Provisioning

1. Build and push images to Artifact Registry (Terraform references image URLs; it does not build images).
2. Add Secret Manager versions for each created secret container.
3. Ensure Cloud Run services use appropriate secret env bindings (`*_secret_env` vars).
4. Run DB migrations from your app deployment workflow.

## Cloud SQL and Redis Connectivity Notes

- Cloud Run backend/job use a Serverless VPC connector with `ALL_TRAFFIC` egress.
- Cloud SQL is private IP and also mounted through Cloud Run Cloud SQL integration.
- Memorystore is private IP inside the same VPC.

## Dev/Stage/Prod Strategy

Recommended approach:

- Keep this module layout shared
- Use separate var files and state backends per environment
- Prefix names by `environment` (already built into resource naming)

## Operational Notes

- Cloud Run image updates are a separate deployment concern from Terraform infrastructure creation.
- Secret containers are created here, but values (versions) must be added manually or via CI/CD.
- Schema migrations are application deployment steps, not pure infra provisioning.
- Private networking (VPC connector + private services) improves security but adds cost and complexity.
- `DATABASE_URL` should come from secrets or env injection at deploy time; avoid hardcoding credentials in Terraform.
