provider "aws" {
  version = "~> 2.7"
  region  = "ap-northeast-2"
}

resource "aws_iam_role_policy" "Auto_Stop_policy" {
  name = "Auto_Stop_policy"
  role = aws_iam_role.Auto_Stop_Role.id

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "EC2",
            "Effect": "Allow",
            "Action": [
                "ec2:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "RDS",
            "Effect": "Allow",
            "Action": [
                "rds:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AutoScale",
            "Effect": "Allow",
            "Action": [
                "autoscaling:*"
            ],
            "Resource": "*"
        },        
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
  })
}

resource "aws_iam_role" "Auto_Stop_Role" {
  name = "Auto_Stop_Role"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_lambda_function" "Auto_Stop_Lambda" {
  filename      = "Auto_stop.zip"
  function_name = "Auto_Stop_Lambda"
  role          = aws_iam_role.Auto_Stop_Role.arn
  handler       = "Auto_stop.lambda_handler"
  runtime = "python3.7"
  timeout = 180
}

resource "aws_cloudwatch_event_rule" "Auto_Stop_trigger_EventBridge" {
  name        = "Auto_Stop_trigger_EventBridge"
  description = "Auto_Stop_trigger_EventBridge"
  schedule_expression = "cron(0 10 * * ? *)"
  depends_on = ["aws_lambda_function.Auto_Stop_Lambda"]
}

resource "aws_cloudwatch_event_target" "Auto_Stop_Lambda" {
  target_id = "Auto_Stop_Lambda"
  rule = aws_cloudwatch_event_rule.Auto_Stop_trigger_EventBridge.name
  arn = aws_lambda_function.Auto_Stop_Lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.Auto_Stop_Lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.Auto_Stop_trigger_EventBridge.arn
}