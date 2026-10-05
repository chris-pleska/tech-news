# Security group for the Lambda: nothing connects in, it only reaches out
resource "aws_security_group" "lambda" {
  name        = "tech-news-lambda-sg"
  description = "Tech news Lambda: outbound only"
  vpc_id      = aws_vpc.main.id

  # No ingress block: EventBridge starts the Lambda through AWS itself, not through a port

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tech-news-lambda-sg"
  }
}
