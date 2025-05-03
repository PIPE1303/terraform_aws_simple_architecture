provider "aws" {
  region = var.region
}

data "http" "my_ip" {
  url = "https://checkip.amazonaws.com"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "MainVPC"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "subnet" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "subnet_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.subnet_b.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_security_group" "rds_sg" {
  name        = "rds_sg_allow_my_ip"
  description = "Allow PostgreSQL access from my IP"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["${trimspace(data.http.my_ip.response_body)}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "default" {
  name       = "default-subnet-group"
  subnet_ids = [
    aws_subnet.subnet.id,
    aws_subnet.subnet_b.id
  ]
}

resource "aws_db_instance" "mydb" {
  identifier             = "mydb-instance"
  engine                 = "postgres"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  username               = var.db_username
  password               = var.db_password
  db_name                = var.db_name
  publicly_accessible    = true
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.default.name
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "${var.bucket_name}-${random_id.suffix.hex}"

  tags = {
    Name        = "DataBucket"
    Environment = "Dev"
  }
}

resource "null_resource" "generate_env_file" {
  depends_on = [aws_s3_bucket.data_bucket, aws_db_instance.mydb]

  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "echo BUCKET_NAME=${aws_s3_bucket.data_bucket.bucket} > ../.env && echo DB_HOST=${aws_db_instance.mydb.address} >> ../.env && echo DB_NAME=${var.db_name} >> ../.env && echo DB_USER=${var.db_username} >> ../.env && echo DB_PASSWORD=${var.db_password} >> ../.env && echo DB_PORT=${aws_db_instance.mydb.port} >> ../.env"
  }
}
