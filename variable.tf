variable "aws_region" {
  description = "AWS region"
  default     = "ap-south-1"
}

variable "bucket_name" {
  description = "S3 bucket name for the coffee shop data lake"
  default     = "coffeeinventory"
}

variable "my_ip" {
  description = "Your IP address for security group rules"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.medium"
}

variable "ami_id" {
  description = "Amazon Linux 2023 AMI ID for ap-south-1"
  default     = "ami-0f5ee92e2d63afc18"
}

variable "key_pair_name" {
  description = "Name of your EC2 key pair"
  type        = string
}

variable "snowflake_iam_user" {
  description = "Snowflake IAM user ARN from DESC INTEGRATION"
  type        = string
}

variable "snowflake_external_id" {
  description = "Snowflake external ID from DESC INTEGRATION"
  type        = string
}
