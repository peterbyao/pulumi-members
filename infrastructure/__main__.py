"""An AWS Python Pulumi program"""

import pulumi
import json
import pulumi_aws as aws


config = pulumi.Config()
db_username = config.require('db_username')
db_password = config.require_secret('db_password')


#---- Get VPC for default AWS account
default_vpc = aws.ec2.DefaultVpc("default-vpc", tags={
    "Name": "Default VPC",
})

default_az1 = aws.ec2.DefaultSubnet("default-az-1",
    availability_zone="us-east-2a",
    tags={
        "Name": "Default subnet for us-east-2a",
    }
)

default_az2 = aws.ec2.DefaultSubnet("default-az-2",
    availability_zone="us-east-2b",
    tags={
        "Name": "Default subnet for us-east-2b",
    }
)

default_az3 = aws.ec2.DefaultSubnet("default-az-3",
    availability_zone="us-east-2c",
    tags={
        "Name": "Default subnet for us-east-2c",
    }
)

subnet_ids = pulumi.Output.all(default_az1.id, default_az2.id, default_az3.id).apply(lambda az: f"{az[0]},{az[1]},{az[2]}")

vpc_to_rds = aws.ec2.SecurityGroup("vpc-to-rds",
    description="Allow the resources inside the VPC to communicate with postgres RDS instance",
    vpc_id=default_vpc.id,
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        from_port=3306,
        to_port=3306,
        protocol="tcp",
        cidr_blocks=[default_vpc.cidr_block],
    )])

#---- 
#Create security group to allow RDS traffic
mysql_sg = aws.ec2.SecurityGroup('mysql-sg',
    description='MySQL security group with inbound access',
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=3306,
            to_port=3306,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ])

#----




instance_profile_role = aws.iam.Role("eb-ec2-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Sid": "",
            "Principal": {
                "Service": "ec2.amazonaws.com",
            },
        }],
    }))

eb_policy_attach = aws.iam.RolePolicyAttachment("eb-policy-attach",
    role=instance_profile_role.name,
    policy_arn="arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier")

instance_profile = aws.iam.InstanceProfile("eb-ec2-instance-profile", role=instance_profile_role.name)









# Create an Amazon RDS instance.
# It uses the security group and subnet group created above.
rds_instance = aws.rds.Instance('mysql-instance',
    engine='mysql',
    engine_version='8.0',
    instance_class='db.t3.micro',
    allocated_storage=10,
    username='admin',
    password='TradingApp1234',
    db_name='pulumimembers',  # name of the default database to create
    vpc_security_group_ids=[vpc_to_rds.id],
    skip_final_snapshot=True,
    publicly_accessible = True
    )



# Create the elastic beanstalk app
app = aws.elasticbeanstalk.Application("fastapi-app", description="Testing FastAPI app deployment")

# Define the elastic beanstalk environment
env = aws.elasticbeanstalk.Environment("pulumi-env",
    application=app.name,
    solution_stack_name="64bit Amazon Linux 2023 v4.1.2 running Docker",
    settings=[
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            namespace="aws:autoscaling:launchconfiguration",
            name="IamInstanceProfile",
            value=instance_profile.name
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            namespace="aws:ec2:vpc",
            name="VPCId",
            value=default_vpc.id,
        ),
        aws.elasticbeanstalk.EnvironmentSettingArgs(
            namespace="aws:ec2:vpc",
            name="Subnets",
            value=subnet_ids,
        ),
    ],
    wait_for_ready_timeout = "20m"
    )

# Export the value for the DB instance so it can be used with other Pulumi programs
pulumi.export('address_of_db_instance', rds_instance.address)

# Export IDs and names.
# pulumi.export("appID",      app.id)
# pulumi.export("appName",    app.name)
# pulumi.export("environmentID",  env.id)
# pulumi.export("environmentName", env.name)