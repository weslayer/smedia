resource "aws_s3_bucket" "smedia_dev_bucket"{
    bucket = "smedia_dev_bucket"

    tags = {
    Name = "smedia_dev_bucket"
    Enviroment ="Dev"
}
}