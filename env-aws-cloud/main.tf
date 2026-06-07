terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "exacq-tf-state-odon-2026"
    key            = "never404-platform/terraform.tfstate"
    region         = "eu-west-1"
    use_lockfile   = true
    encrypt        = true
  }
}

provider "aws" {
  region = "eu-west-1"
}

resource "aws_security_group" "never404_sg" {
  name        = "never404_platform_sg"
  description = "Allow Web, HTTPS, and SSH traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Kubernetes API Access"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "ICMP for Ping and MTU Discovery"
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "never404_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.small" # MUST be t3.small for K3s memory requirements
  key_name               = "never404-key"
  vpc_security_group_ids = [aws_security_group.never404_sg.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }
  
}

output "server_public_ip" {
  value       = aws_instance.never404_server.public_ip
  description = "Point your Hostinger A Record to this IP address!"
}