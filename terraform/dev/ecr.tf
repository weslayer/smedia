resource "aws_ecr_repository" "smedia-repo" {
  name = "${var.cluster_name}-smedia"
  image_scanning_configuration {
    scan_on_push = true
  }
  lifecycle_policy {
    policy = jsonencode({
      rules = [
        {
          rulePriority = 1
          description  = "Expire untagged images older than 30 days"
          selection = {
            tagStatus   = "untagged"
            countType   = "sinceImagePushed"
            countUnit   = "days"
            countNumber = 30
          }
          action = { type = "expire" }
        }
      ]
    })
  }
}
