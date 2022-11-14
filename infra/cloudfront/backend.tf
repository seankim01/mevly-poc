terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket         = "mevly-s3-test-tf"
    key            = "terraform.tfstate"
    region         = "ap-northeast-2"
    encrypt        = true    
  }
}
