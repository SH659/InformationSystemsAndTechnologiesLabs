variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "meme-commenter"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "gemini_api_key" {
  description = "Gemini API Key for the application"
  type        = string
  sensitive   = true
}

variable "docker_username" {
  description = "Docker Hub username"
  type        = string
}

variable "docker_image" {
  description = "Docker image name (e.g., username/meme-commenter)"
  type        = string
}
