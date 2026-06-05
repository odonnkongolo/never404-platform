terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # --- TELL TERRAFORM TO USE THE CLOUD VAULT ---
  backend "s3" {
    bucket         = "exacq-tf-state-odon-2026"
    key            = "never404-platform/terraform.tfstate"
    region         = "eu-west-1"
    use_lockfile   = true
    encrypt        = true
  }
}

# 1. The Cloud Provider
provider "aws" {
  region = "eu-west-1" # Dublin (Closest to Belfast for lowest latency)
}

# 2. The Cloud Firewall (Security Group)
resource "aws_security_group" "never404_sg" {
  name        = "never404_platform_sg"
  description = "Allow Web, HTTPS, and SSH traffic"

  # Allow standard web traffic (HTTP)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow secure web traffic (HTTPS) - Crucial for our SSL padlock!
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow SSH traffic so we can debug
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic (so the server can download packages)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Find the latest Ubuntu OS automatically
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Official Canonical Ubuntu

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# 4. The Virtual Server (100% Free Tier Eligible)
resource "aws_instance" "never404_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = "never404-key" # <---  Added KEY PAIR NAME
  vpc_security_group_ids = [aws_security_group.never404_sg.id]

  # ---> CLAIM 20GB OF FREE TIER STORAGE <---
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  # 5. The Bootstrap Automation (Runs once on boot)
  user_data = <<-EOF
              #!/bin/bash

              # --- 1. Install the k3s Orchestrator ---
              curl -sfL https://get.k3s.io | sh -
              sleep 15 # Wait for cluster to wake up
              
              EOF

  tags = {
    Name = "Never404-Market-Tracker-Cluster"
  }
}

# 6. Output the Public IP address to your terminal.
output "server_public_ip" {
  value       = aws_instance.never404_server.public_ip
  description = "Point your Hostinger A Record to this IP address!"
}