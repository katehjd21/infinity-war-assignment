terraform {
  backend "s3" {
    bucket         = "kd-infinity-war-assignment-s3-bucket"
    key            = "infinity-war-assignment/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "kd-terraform-state-lock"
    encrypt        = true
  }
}
