resource "aws_s3_bucket" "banners" {
  bucket = var.s3_bucket_name

  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }

}
