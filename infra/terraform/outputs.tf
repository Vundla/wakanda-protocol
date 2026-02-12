output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.wakanda_vpc.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public_subnets[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private_subnets[*].id
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.wakanda_cluster.name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.wakanda_cluster.endpoint
}

output "eks_cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = aws_security_group.eks_cluster_sg.id
}

output "eks_node_security_group_id" {
  description = "EKS node security group ID"
  value       = aws_security_group.eks_node_sg.id
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.wakanda_db.endpoint
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.wakanda_db.port
}

output "eks_oidc_issuer_url" {
  description = "EKS OIDC issuer URL"
  value       = aws_eks_cluster.wakanda_cluster.identity[0].oidc[0].issuer
}

output "alb_controller_role_arn" {
  description = "ALB controller IAM role ARN"
  value       = aws_iam_role.alb_controller_role.arn
}