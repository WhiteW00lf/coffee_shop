terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket
resource "aws_s3_bucket" "coffee_lake" {
  bucket = var.bucket_name

  tags = {
    Project     = "coffee-shop"
    Environment = "learning"
    ManagedBy   = "terraform"
  }
}

# S3 folder structure
resource "aws_s3_object" "raw_zone" {
  bucket = aws_s3_bucket.coffee_lake.id
  key    = "raw/coffee_orders/"
}

resource "aws_s3_object" "curated_zone" {
  bucket = aws_s3_bucket.coffee_lake.id
  key    = "curated/coffee_orders/"
}

resource "aws_s3_object" "archive_zone" {
  bucket = aws_s3_bucket.coffee_lake.id
  key    = "archive/coffee_orders/"
}

# Security group for Kafka EC2
resource "aws_security_group" "kafka_sg" {
  name        = "kafka-sg"
  description = "Security group for coffee shop Kafka EC2"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "SSH"
  }

  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Kafka plaintext"
  }

  ingress {
    from_port   = 29092
    to_port     = 29092
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Kafka host listener"
  }

  ingress {
    from_port   = 8081
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Schema Registry"
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Airflow webserver"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project   = "coffee-shop"
    ManagedBy = "terraform"
  }
}

# IAM role for Snowflake S3 access
resource "aws_iam_role" "snowflake_s3_role" {
  name = "snowflake-s3-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.snowflake_iam_user
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.snowflake_external_id
          }
        }
      }
    ]
  })

  tags = {
    Project   = "coffee-shop"
    ManagedBy = "terraform"
  }
}

# IAM policy for Snowflake to read S3
resource "aws_iam_role_policy" "snowflake_s3_policy" {
  name = "snowflake-s3-policy"
  role = aws_iam_role.snowflake_s3_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.bucket_name}",
          "arn:aws:s3:::${var.bucket_name}/*"
        ]
      }
    ]
  })
}

# EC2 instance
resource "aws_instance" "kafka_ec2" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.kafka_sg.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name      = "coffee-shop-kafka"
    Project   = "coffee-shop"
    ManagedBy = "terraform"
  }
}
