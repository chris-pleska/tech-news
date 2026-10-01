terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"        # any 6.x version, but not a future 7.0 that could break things
    }
  }

  backend "s3" {
    bucket       = "tech-news-tfstate-718896642278"   # the bucket you just created
    key          = "tech-news/terraform.tfstate"      # the file path inside the bucket
    region       = "us-east-1"
    use_lockfile = true                               # stops two applies from running at the same time
  }
}