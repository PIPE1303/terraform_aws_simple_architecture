# AWS Data Ingestion Project

Este proyecto implementa una arquitectura simple para ingestar datos en AWS usando Terraform, Lambda Functions y PostgreSQL.

## Estructura

- `terraform/`: Infraestructura como código.
- `lambda_functions/`: Funciones Lambda para crear tablas y cargar datos.
- `dbml/`: Esquema de base de datos en formato DBML.
- `sample_data/`: Datos de ejemplo (mock).
- `scripts/`: Scripts para empaquetar Lambdas.

## Requisitos

- Terraform instalado (`>=1.0`)
- AWS CLI configurado
- Python 3.9 o superior
- Acceso a una cuenta AWS (idealmente usando la capa gratuita)

## Pasos principales

1. Clona este repositorio
2. Crea tu archivo `terraform/terraform.tfvars` basado en `terraform.tfvars.example`
3. Inicializa Terraform:

   ```bash
   cd terraform
   terraform init
   terraform apply
