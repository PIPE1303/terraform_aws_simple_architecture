variable "region" {
  description = "AWS Region"
  type        = string
 # default     = "us-east-1"
}

variable "bucket_name" {
  description = "Nombre del S3 bucket"
  type        = string
  # default     = "terraform-nu-db-pg"
}

variable "db_username" {
  description = "Usuario de la base de datos PostgreSQL"
  type        = string
}

variable "db_password" {
  description = "Contraseña de la base de datos PostgreSQL"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Nombre de la base de datos PostgreSQL"
  type        = string
}