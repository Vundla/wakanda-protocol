terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC
resource "aws_vpc" "wakanda_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "wakanda-vpc"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "wakanda_igw" {
  vpc_id = aws_vpc.wakanda_vpc.id

  tags = {
    Name        = "wakanda-igw"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

# Public Subnets
resource "aws_subnet" "public_subnets" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.wakanda_vpc.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "wakanda-public-subnet-${count.index + 1}"
    Environment = var.environment
    Project     = "wakanda-protocol"
    Type        = "public"
  }
}

# Private Subnets
resource "aws_subnet" "private_subnets" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.wakanda_vpc.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "wakanda-private-subnet-${count.index + 1}"
    Environment = var.environment
    Project     = "wakanda-protocol"
    Type        = "private"
  }
}

# NAT Gateway
resource "aws_eip" "nat_eip" {
  count  = length(var.public_subnet_cidrs)
  domain = "vpc"

  tags = {
    Name        = "wakanda-nat-eip-${count.index + 1}"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

resource "aws_nat_gateway" "nat_gateway" {
  count = length(var.public_subnet_cidrs)

  allocation_id = aws_eip.nat_eip[count.index].id
  subnet_id     = aws_subnet.public_subnets[count.index].id

  tags = {
    Name        = "wakanda-nat-gateway-${count.index + 1}"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }

  depends_on = [aws_internet_gateway.wakanda_igw]
}

# Route Tables
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.wakanda_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.wakanda_igw.id
  }

  tags = {
    Name        = "wakanda-public-rt"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

resource "aws_route_table" "private_rt" {
  count  = length(var.private_subnet_cidrs)
  vpc_id = aws_vpc.wakanda_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gateway[count.index].id
  }

  tags = {
    Name        = "wakanda-private-rt-${count.index + 1}"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public_rta" {
  count = length(var.public_subnet_cidrs)

  subnet_id      = aws_subnet.public_subnets[count.index].id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "private_rta" {
  count = length(var.private_subnet_cidrs)

  subnet_id      = aws_subnet.private_subnets[count.index].id
  route_table_id = aws_route_table.private_rt[count.index].id
}

# Security Groups
resource "aws_security_group" "eks_cluster_sg" {
  name_prefix = "wakanda-eks-cluster-"
  vpc_id      = aws_vpc.wakanda_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "wakanda-eks-cluster-sg"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

resource "aws_security_group" "eks_node_sg" {
  name_prefix = "wakanda-eks-node-"
  vpc_id      = aws_vpc.wakanda_vpc.id

  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
  }

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "wakanda-eks-node-sg"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "wakanda_cluster" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = concat(aws_subnet.public_subnets[*].id, aws_subnet.private_subnets[*].id)
    security_group_ids      = [aws_security_group.eks_cluster_sg.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  tags = {
    Name        = var.cluster_name
    Environment = var.environment
    Project     = "wakanda-protocol"
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller_policy,
  ]
}

# EKS Node Group
resource "aws_eks_node_group" "wakanda_nodes" {
  cluster_name    = aws_eks_cluster.wakanda_cluster.name
  node_group_name = "wakanda-nodes"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = aws_subnet.private_subnets[*].id

  capacity_type  = "ON_DEMAND"
  instance_types = var.node_instance_types

  scaling_config {
    desired_size = var.node_desired_size
    max_size     = var.node_max_size
    min_size     = var.node_min_size
  }

  update_config {
    max_unavailable = 1
  }

  tags = {
    Name        = "wakanda-node-group"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]
}

# RDS Subnet Group
resource "aws_db_subnet_group" "wakanda_db_subnet_group" {
  name       = "wakanda-db-subnet-group"
  subnet_ids = aws_subnet.private_subnets[*].id

  tags = {
    Name        = "wakanda-db-subnet-group"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

# RDS Instance
resource "aws_db_instance" "wakanda_db" {
  identifier = "wakanda-postgres"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "wakanda"
  username = "wakanda_user"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.wakanda_db_subnet_group.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"

  skip_final_snapshot = true

  tags = {
    Name        = "wakanda-postgres"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}

# RDS Security Group
resource "aws_security_group" "rds_sg" {
  name_prefix = "wakanda-rds-"
  vpc_id      = aws_vpc.wakanda_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_node_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "wakanda-rds-sg"
    Environment = var.environment
    Project     = "wakanda-protocol"
  }
}