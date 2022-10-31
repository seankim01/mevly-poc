# 전체 리전의 Ec2, RDS 중지하는 Lambda 스크립트

### 1. 설정 방법
#### 1.1 Lambda의 role을 아래와 같은 policy로 생성합니다.
   ```bash
{
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
}
   ``` 
</br>

#### 1.2 Lambda를 생성하고 소스코드를 업로드 합니다. 
   ```bash
   - 제약조건 
    > 실행시간을 3분으로 지정합니다. 
    > 람다 생성 시 이전에 만들어두었던 role을 attach 합니다. 
   ``` 

</br>

#### 1.3 CloudWatch event rules 에러 람다를 트리거 합니다. 
   ```bash
   - Daily 19:00 PM KST에 트리거될 수 있게 설정합니다. 
   0 10 * * ? *
   ``` 
