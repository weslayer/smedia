# IAM role for spot fleet
resource "aws_iam_role" "fleet_role" {
  name = "${var.cluster_name}-spot-fleet-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "spotfleet.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "spot_fleet_policy" {
  role       = aws_iam_role.fleet_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2SpotFleetTaggingRole"
}

# Spot fleet request
resource "aws_spot_fleet_request" "sport-workers" {
  iam_fleet_role              = aws_iam_role.fleet_role.arn
  target_capacity             = var.desired_capacity
  allocation_strategy         = "lowestPrice"
  fleet_type                  = "maintain"
  instance_pools_to_use_count = 2

  dynamic "launch_specification" {
    for_each = toset(aws_subnet.private[*].id)
    content {
      instance_type               = var.instance_type
      subnet_id                   = launch_specification.value
      associate_public_ip_address = false
      ami                         = data.aws_ami.eks_worker.id
      iam_instance_profile_arn    = aws_iam_instance_profile.eks_worker.arn
      vpc_security_group_ids      = [aws_security_group.eks_worker.id]
      
      tags = {
        Name                                            = "${var.cluster_name}-spot-instances-Node"
        "alpha.eksctl.io/cluster-name"                  = var.cluster_name
        "alpha.eksctl.io/nodegroup-name"                = "spot-instances"
        "eksctl.cluster.k8s.io/v1alpha1/cluster-name"   = var.cluster_name
        "eksctl.io/v1alpha2/nodegroup-name"             = "spot-instances"
        "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
        "k8s.io/cluster-autoscaler/enabled"             = "true"
        "kubernetes.io/cluster/${var.cluster_name}"     = "owned"
      }

      user_data = base64encode(templatefile("${path.module}/templates/userdata.sh", {
        cluster_name = var.cluster_name
        cluster_endpoint = aws_eks_cluster.smedia-eks.endpoint
        cluster_certificate_authority_data = aws_eks_cluster.smedia-eks.certificate_authority[0].data
      }))
    }
  }
}

# Get the latest EKS worker AMI
data "aws_ami" "eks_worker" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amazon-eks-node-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security group for worker nodes
resource "aws_security_group" "eks_worker" {
  name        = "${var.cluster_name}-worker-sg"
  description = "Security group for EKS worker nodes"
  vpc_id      = aws_vpc.smedia-vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-worker-sg"
  }
}

# IAM instance profile for worker nodes
resource "aws_iam_instance_profile" "eks_worker" {
  name = "${var.cluster_name}-worker-profile"
  role = aws_iam_role.eks_node.name
} 