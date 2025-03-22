data "aws_secretsmanager_secret" "db_password" {
  name = "chatbot-secrets"
}

data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = data.aws_secretsmanager_secret.db_password.id
}

resource "aws_db_instance" "default" {
  allocated_storage      = 20
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  db_name                = "chatbot_db"
  identifier             = "chatbot-db"
  password               = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string).DB_PASSWORD
  port                   = 10086
  publicly_accessible    = true
  skip_final_snapshot    = true
  username               = "chatbot_user"
  vpc_security_group_ids = [aws_security_group.allow_tls.id]
}

resource "aws_security_group" "allow_tls" {
  name        = "allow_tls"
  description = "Allow TLS inbound traffic"

  ingress {
    description = "TLS from VPC"
    from_port   = 10086
    to_port     = 10086
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}