output "ec2_public_ip" {
  description = "Public IP of the Kafka EC2 instance"
  value       = aws_instance.kafka_ec2.public_ip
}

output "s3_bucket_name" {
  description = "S3 data lake bucket name"
  value       = aws_s3_bucket.coffee_lake.id
}

output "snowflake_role_arn" {
  description = "IAM role ARN for Snowflake"
  value       = aws_iam_role.snowflake_s3_role.arn
}
