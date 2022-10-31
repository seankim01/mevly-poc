resource "aws_s3_bucket" "test-s3-tf-state" {

  bucket = "mevly-s3-test-tf"

  tags = {
    "Name" = "mevly-s3-test-tf"
  }
  
}