variable "region" {
  description = "AWS Region"
  type        = string
  # default     = "us-east-1"
}

variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
  # default     = "terraform-nu-db-pg"
}

variable "db_username" {
  description = "PostgreSQL database username"
  type        = string
}

variable "db_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
}