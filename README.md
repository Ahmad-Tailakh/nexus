# Nexus

Nexus is a production-grade Python backend platform for managing
application projects, environments, services, and deployment history.

The project is being developed as a practical engineering laboratory
for backend, cloud-native, DevOps, Kubernetes, and MLOps engineering.

## Current Status

🚧 Early development

Nexus is currently in the initial MVP architecture and domain-design phase.

## Goals

Nexus is designed to demonstrate:

- Clean and maintainable Python architecture
- REST API development
- PostgreSQL database design
- Comprehensive testing
- Containerization
- Kubernetes deployment
- CI/CD
- Observability
- Infrastructure as Code
- AWS cloud deployment
- Security and reliability engineering

## Architecture

Nexus starts as a modular monolith and will evolve incrementally
as new requirements are introduced.

Initial architecture:

Presentation → Application → Domain
                         ↑
                   Infrastructure

## Technology

### Current

- Python
- Flask
- PostgreSQL
- SQLAlchemy
- pytest

### Planned

- Docker
- Kubernetes
- GitHub Actions
- Prometheus
- Grafana
- OpenTelemetry
- Redis
- Terraform
- AWS

## Project Structure

```text
src/
tests/
docs/
migrations/
scripts/
