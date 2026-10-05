# Subnet group: tells RDS which subnets it may use (AWS requires at least 2 AZs)
resource "aws_db_subnet_group" "main" {
  name       = "tech-news-db-subnets"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id] # us-east-1a and us-east-1b

  tags = {
    Name = "tech-news-db-subnets"
  }
}

# Security group: only lets Postgres traffic in from the Lambda
resource "aws_security_group" "db" {
  name        = "tech-news-db-sg"
  description = "Postgres access from inside the VPC" # left as is: changing it would replace the group
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Postgres from the Lambda only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id] # anything wearing the Lambda's security group
  }

  tags = {
    Name = "tech-news-db-sg"
  }
}

resource "aws_db_instance" "main" {
  identifier     = "tech-news-db"
  engine         = "postgres"
  engine_version = "16"          # latest 16.x minor version
  instance_class = "db.t3.micro" # t4g.micro had no capacity in us-east-1a/b

  allocated_storage = 20 # GB
  storage_type      = "gp3"
  storage_encrypted = true

  db_name                     = "tech_news" # same name as your local database
  username                    = "tech_news"
  manage_master_user_password = true # AWS generates the password and keeps it in Secrets Manager

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false # no public IP, only reachable from inside the VPC
  multi_az               = false # one instance; set true for a standby copy in the other AZ (doubles the cost)

  backup_retention_period = 7    # days of automatic backups
  skip_final_snapshot     = true # practice project: don't keep a snapshot on destroy
  deletion_protection     = false

  tags = {
    Name = "tech-news-db"
  }
}

output "db_endpoint" {
  value = aws_db_instance.main.address # the host name to put in DATABASE_URL
}

output "db_secret_arn" {
  value = aws_db_instance.main.master_user_secret[0].secret_arn # where to find the password
}
