resource "aws_vpc" "main" {
  cidr_block           = "10.1.0.0/16"     # the practice VPC uses 10.0.0.0/16, so this one stays separate
  enable_dns_support   = true              # lets resources inside look up DNS names
  enable_dns_hostnames = true              # gives resources DNS names (RDS needs this later)

  tags = {
    Name = "tech-news-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id                 # attach it to the VPC above

  tags = {
    Name = "tech-news-igw"
  }
}
