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

# Public subnets: for the load balancer and NAT gateway
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.1.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true           # anything launched here gets a public IP

  tags = {
    Name = "tech-news-public-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.1.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "tech-news-public-b"
  }
}

# Private subnets: for the database, Lambda, and app servers
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.1.11.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "tech-news-private-a"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.1.12.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "tech-news-private-b"
  }
}

# Public route table: sends internet traffic out through the internet gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"               # anywhere on the internet
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "tech-news-public-rt"
  }
}

# Connect each public subnet to the public route table
resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

# Private route table
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block       = "0.0.0.0/0"
    nat_gateway_id   = aws_nat_gateway.main.id
  }
  
  tags = {
    Name = "tech-news-private-rt"
  }
}

# Connect each private subnet to the private route table
resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}

# A fixed public IP address for the NAT gateway
resource "aws_eip" "nat" {
  domain = "vpc"                            # an IP for use inside a VPC

  tags = {
    Name = "tech-news-nat-ip"
  }
}

# NAT gateway: lets the private subnets reach out to the internet, nothing can reach in
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id            # use the IP from above
  subnet_id     = aws_subnet.public_a.id    # must live in a PUBLIC subnet

  tags = {
    Name = "tech-news-nat"
  }

  depends_on = [aws_internet_gateway.main]  # build the internet gateway first
}