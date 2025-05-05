output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.data_bucket.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.data_bucket.arn
}