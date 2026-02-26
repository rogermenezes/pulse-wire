# Codex Prompt: Terraform-Based GCP Deployment for News Aggregator

You are building the infrastructure layer for a production-grade deployment of a news aggregator application on Google Cloud Platform.

The application stack is:
- Frontend: Next.js
- Backend API: FastAPI
- Database: PostgreSQL
- Cache and queue support: Redis
- Container deployment target: Google Cloud Run
- Infrastructure as Code: Terraform

Your task is to generate a Terraform-based deployment setup that provisions and documents the cloud infrastructure for this application.

## Primary goal

Create a clean, production-oriented Terraform project that provisions the following on GCP:

1. A Cloud Run service for the Next.js frontend
2. A Cloud Run service for the FastAPI backend
3. A Cloud SQL for PostgreSQL instance and database
4. A Memorystore for Redis instance
5. Artifact Registry repositories for container images
6. Service accounts and IAM bindings with least privilege
7. Secret Manager integration points for sensitive configuration
8. Networking required for Cloud Run to communicate with Cloud SQL and Memorystore
9. Optional Cloud Run Job(s) for background workers / crawlers
10. Outputs and documentation so a developer can deploy this from a fresh GCP project

## Important implementation constraints

Design this as a real-world starter kit, not a toy example.

- Use Terraform with the Google and Google-beta providers where needed.
- Keep the Terraform modular and readable.
- Use variables for project ID, region, environment name, database sizing, container image names, and secrets.
- Assume separate environments such as dev, staging, and prod can be supported later.
- Prefer a structure that can be extended, but keep the first version practical and easy to run.
- Use ASCII only in generated files.
- Add comments explaining non-obvious Terraform decisions.
- Default region should be `us-central1`, but make it configurable.
- Assume images are already built and pushed separately; Terraform should reference image URLs as variables.
- Do not hardcode secrets into Terraform.
- Do not use deprecated resources unless absolutely necessary.

## Desired repository layout

Generate a Terraform project with a structure similar to:

```text
infra/
  terraform/
    main.tf
    providers.tf
    variables.tf
    outputs.tf
    versions.tf
    terraform.tfvars.example
    README.md
    modules/
      artifact_registry/
        main.tf
        variables.tf
        outputs.tf
      service_accounts/
        main.tf
        variables.tf
        outputs.tf
      cloud_sql/
        main.tf
        variables.tf
        outputs.tf
      memorystore/
        main.tf
        variables.tf
        outputs.tf
      networking/
        main.tf
        variables.tf
        outputs.tf
      cloud_run_service/
        main.tf
        variables.tf
        outputs.tf
      cloud_run_job/
        main.tf
        variables.tf
        outputs.tf
      secret_manager/
        main.tf
        variables.tf
        outputs.tf
```

If you think a slightly different structure is better, use it, but keep it modular.

## Infrastructure requirements in detail

### 1) Project and providers

Set up:
- Terraform version constraints
- Required providers
- `google` provider
- `google-beta` provider if needed for specific resources

Use variables for:
- `project_id`
- `region`
- `environment`

## 2) Artifact Registry

Provision Artifact Registry repositories for:
- frontend images
- backend images
- worker images (optional)

Make repository names environment-aware where appropriate.

## 3) Service accounts and IAM

Create dedicated service accounts for:
- frontend Cloud Run service
- backend Cloud Run service
- worker Cloud Run job (if included)

Grant only the IAM roles needed, such as:
- Secret Manager access for runtime secrets
- Cloud SQL client role for services that connect to Postgres
- logging / monitoring write roles if appropriate

Do not over-grant broad editor or owner roles.

## 4) Cloud SQL for PostgreSQL

Provision:
- a Cloud SQL PostgreSQL instance
- a database for the app
- optional database user resource if appropriate

Requirements:
- configurable machine tier / sizing
- backups enabled for production-ready posture
- deletion protection configurable
- private IP preferred if networking setup supports it; otherwise document the chosen approach
- outputs for connection name, database name, and instance details

The Terraform should make it clear how the FastAPI service connects to Cloud SQL.

## 5) Memorystore for Redis

Provision a Redis instance suitable for:
- caching hot story feeds
- queue coordination / lightweight background task state

Requirements:
- configurable memory size / tier
- region-aware
- expose host and port via outputs
- document how Cloud Run reaches it

## 6) Networking

Provision the networking needed so Cloud Run services can reach private resources where required.

This may include:
- VPC network
- subnetwork
- Serverless VPC Access connector
- private service access configuration if needed for Cloud SQL private IP

The generated code should make pragmatic choices and explain them. If there are tradeoffs, note them in comments and README.

## 7) Cloud Run services

Create a reusable module for Cloud Run services, then instantiate it for:
- Next.js frontend service
- FastAPI backend service

Requirements for both services:
- configurable service name
- configurable container image
- configurable CPU and memory
- autoscaling knobs (min/max instances)
- port configuration
- environment variables support
- secret-based environment variable support through Secret Manager references
- ingress configuration
- optional unauthenticated access for public endpoints

### Frontend Cloud Run service

The frontend service should be configured for:
- public access
- environment variables that point to the backend API base URL
- typical Next.js runtime container behavior

### Backend Cloud Run service

The backend service should be configured for:
- public or restricted ingress based on variable
- environment variables for database and Redis connectivity
- Cloud SQL connectivity
- Secret Manager references for API keys and sensitive values
- support for outbound network access through the VPC connector if needed

## 8) Cloud Run jobs (optional but recommended)

Create an optional reusable module for Cloud Run Jobs to support:
- crawlers
- feed fetchers
- clustering / summarization workers

Include:
- image reference
- task timeout
- retry controls
- env vars and secrets
- VPC connector support if the job needs private resource access

## 9) Secret Manager

Provision placeholder secrets or references for:
- `DATABASE_URL` (or components if you prefer not to store a full URL)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `DISCORD_BOT_TOKEN`
- any other clearly relevant runtime secrets

Notes:
- It is acceptable to create secret containers without populating real values.
- Show how Cloud Run binds these secrets into runtime env vars.
- Make clear where a human must manually add secret versions.

## 10) Variables and outputs

Create a thoughtful set of variables and outputs.

Variables should cover:
- project and region config
- environment
- container image URLs
- resource sizing
- service names
- database name
- Redis memory size
- whether frontend and backend are public
- deletion protection toggle

Outputs should include:
- frontend service URL
- backend service URL
- Cloud SQL connection name
- Cloud SQL instance name
- database name
- Redis host and port
- Artifact Registry repository names / URLs
- service account emails

## 11) README

Generate a detailed `README.md` inside the Terraform folder that explains:

- what this infrastructure provisions
- prerequisites (Terraform installed, gcloud authenticated, billing enabled, APIs enabled)
- which GCP APIs need to be enabled
- how to set variables
- how to initialize Terraform
- how to run `terraform plan`
- how to run `terraform apply`
- how to destroy resources safely
- which manual steps are still required after provisioning (for example, pushing images, setting secret versions, running migrations)
- how the app services connect to Cloud SQL and Redis
- how to adapt this for dev vs prod

Include a section called `Operational Notes` describing common gotchas such as:
- Cloud Run service image updates are separate from Terraform infra provisioning
- Secret values may require manual version creation
- Cloud SQL migrations are an app deployment concern, not pure infra
- Some private networking choices may increase cost and complexity

## 12) Quality bar

The generated Terraform should:
- be reasonably valid and internally consistent
- avoid placeholder nonsense
- include practical defaults
- be easy for a developer to understand and customize
- favor clarity over over-engineering

## 13) Optional extras

If there is room, include optional but useful additions such as:
- Cloud Scheduler job to trigger Cloud Run Jobs on a cadence
- basic logging / monitoring notes
- labels for cost tracking
- environment-specific naming conventions

## Output format

Generate:
1. The full Terraform file contents for the repo structure
2. A `terraform.tfvars.example`
3. A `README.md`
4. Brief notes on any assumptions made

Where appropriate, include inline comments in the Terraform.

## Architecture assumptions

Assume the application architecture is:
- Users hit the Next.js frontend on Cloud Run
- The frontend talks to the FastAPI backend over HTTPS
- The backend reads and writes to Cloud SQL PostgreSQL
- The backend uses Redis for cache / queue coordination
- Background workers run as Cloud Run Jobs and may also use Cloud SQL and Redis
- Secrets are stored in Secret Manager
- Container images are stored in Artifact Registry

## Coding style preferences

- Keep modules focused and not overly abstract.
- Favor explicit variables over magic locals.
- Use descriptive resource names.
- Add comments where GCP behavior is tricky.
- Prefer copy-pasteable, implementation-ready output.

Produce the Terraform starter kit now.
