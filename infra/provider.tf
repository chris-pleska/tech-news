provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project = "tech-news"     # added to every resource automatically
    }
  }
}