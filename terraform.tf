provider "aws" {
  region = "eu-west-1"
}

variable "telegram_bot_key" {
  type        = "string"
  description = "The telegram bot key like: botddddd:aaaaaa"
}

variable "telegram_channel_id" {
  type        = "string"
  description = "Telegram channel id like: @channel_asd_adsa"
}

resource "aws_lambda_function" "open_lambda" {
  function_name    = "telegram-open"
  runtime          = "python3.8"
  role             = "${aws_iam_role.telegram_open_role.arn}"
  handler          = "scraper.handle"
  filename         = "function.zip"
  source_code_hash = "${base64sha256("scraper.py")}"
  timeout          = 30
  environment {
    variables = {
      TGCHANNELID = "${var.telegram_channel_id}"
      TGBOTKEY    = "${var.telegram_bot_key}"
    }
  }
}

resource "aws_lambda_permission" "scrape-open-permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.open_lambda.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.scrap-scheduled-event-rule.arn}"
}


resource "aws_iam_role" "telegram_open_role" {
  name = "telegram-open-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "access_dynamodb" {
  role   = "${aws_iam_role.telegram_open_role.id}"
  name   = "dynamodb-access-policy"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
        "Action": [
            "dynamodb:GetItem",
            "dynamodb:PutItem"
        ],
        "Resource": "${aws_dynamodb_table.open_daily_history.arn}"
    }
  ]
}
EOF
}


# dynamo db
resource "aws_dynamodb_table" "open_daily_history" {
  name           = "open_daily_history"
  hash_key       = "url"
  billing_mode   = "PROVISIONED"
  write_capacity = "1"
  read_capacity  = "1"
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  attribute {
    name = "url"
    type = "S"
  }
}

resource "aws_cloudwatch_event_rule" "scrap-scheduled-event-rule" {
  name                = "scheduled-scrap"
  description         = "Scrap open news"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "scarap-target" {
  rule = "${aws_cloudwatch_event_rule.scrap-scheduled-event-rule.name}"
  arn  = "${aws_lambda_function.open_lambda.arn}"
}