provider "aws" {
  region = var.aws_region
}

module "s3_bucket" {
  source         = "terraform-aws-modules/s3-bucket/aws"
  bucket         = var.bucket_name
  acl            = var.bucket_acl
  force_destroy  = var.force_destroy

  versioning = {
    enabled = var.versioning_enabled
  }

  tags = var.tags
}

# Enable Server-Side Encryption for the S3 Bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = module.s3_bucket.this_s3_bucket_id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Enable Bucket Logging
resource "aws_s3_bucket_logging" "app_logging" {
  bucket = module.s3_bucket.this_s3_bucket_id
  target_bucket = var.logging_target_bucket
  target_prefix = var.logging_target_prefix
}

# Enable Bucket Policy
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = module.s3_bucket.this_s3_bucket_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${module.s3_bucket.this_s3_bucket_arn}/*"
      }
    ]
  })
}

# Enable Lifecycle Rules
resource "aws_s3_bucket_lifecycle_configuration" "bucket_lifecycle" {
  bucket = module.s3_bucket.this_s3_bucket_id

  rule {
    id     = "ExpireObjects"
    status = "Enabled"

    expiration {
      days = var.expiration_days
    }

    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }
  }

  rule {
    id     = "AbortIncompleteMultipartUploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = var.abort_multipart_days
    }
  }
}

# IAM policy for the S3 bucket access
resource "aws_iam_policy" "s3_bucket_access_policy" {
  name        = "s3-bucket-access-policy"
  description = "IAM policy to allow read/write access to the S3 bucket"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          module.s3_bucket.this_s3_bucket_arn,
          "${module.s3_bucket.this_s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Attach the IAM policy to an IAM role
resource "aws_iam_role_policy_attachment" "s3_bucket_access_policy_attachment" {
  role       = aws_iam_role.some_role.name
  policy_arn = aws_iam_policy.s3_bucket_access_policy.arn
}

# Outputs
output "bucket_name" {
  description = "The name of the S3 bucket"
  value       = module.s3_bucket.this_s3_bucket_id
}

output "bucket_arn" {
  description = "The ARN of the S3 bucket"
  value       = module.s3_bucket.this_s3_bucket_arn
}

output "bucket_domain_name" {
  description = "The domain name of the S3 bucket"
  value       = module.s3_bucket.this_s3_bucket_domain_name
}

variable "aws_region" {
  description = "The AWS region to create resources in"
  type        = string
  default     = "us-west-1"
}

variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
}

variable "bucket_acl" {
  description = "The ACL for the bucket"
  type        = string
  default     = "private"
}

variable "force_destroy" {
  description = "Whether to force the destruction of the bucket"
  type        = bool
  default     = false
}

variable "versioning_enabled" {
  description = "Enable versioning for the S3 bucket"
  type        = bool
  default     = false
}

variable "logging_target_bucket" {
  description = "The target bucket for S3 access logs"
  type        = string
  default     = ""
}

variable "logging_target_prefix" {
  description = "The prefix for S3 access logs"
  type        = string
  default     = ""
}

variable "expiration_days" {
  description = "Number of days before objects are deleted"
  type        = number
  default     = 90
}

variable "noncurrent_version_expiration_days" {
  description = "Number of days before non-current object versions expire"
  type        = number
  default     = 30
}

variable "abort_multipart_days" {
  description = "Number of days to abort incomplete multipart uploads"
  type        = number
  default     = 7
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {
    Project = "StripeClone"
    Owner   = "Team"
  }
}

resource "aws_iam_role" "some_role" {
  name               = "some-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}
