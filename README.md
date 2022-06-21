# Audit AWS IAM Users

You can use [this small project](https://github.com/a2tt/Audit-AWS-IAM-User.git) to audit your AWS IAM users to prevent unexpected behavior and charge.
If you follow the steps below, you can make a small system that notifies you when an IAM user uses not only AWS console but also API call using SDK.  



## How to use

### Notification channel - Slack

First of all, you need a channel to receive an alert message through it. My favorites are Slack and Telegram and I'm going to use Slack in this example.  

1. Log in Slack and go to [here](https://api.slack.com/apps?new_app=1) to create new app.
2. Click **Create New App** button and select to create from scratch.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_app_list.png" alt="slack app list" width=400>
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_create_1.png" alt="create app option" width=400>
3. Enter the name of your app and pick a workspace where your app can work.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_create_2.png" alt="name and workspace" width=400>
4. Now, you are in the configuration page. Let's configure **Incoming Webhooks**. Click this button.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_config_1.png" alt="add features" width=400>
5. Activate incoming webhooks.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_config_2.png" alt="activate incoming webhooks" width=400>
6. Click **Add New Webhook to Workspace** and choose a channel that audit messages will be posted on.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_config_3.png" alt="choose channel" width=400>
7. Then, you have created new webhook URL. When sending JSON data to the URL, that data will be posted on the selected channel.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_webhook_url.png" alt="webhook created" width=400>


### AWS CloudTrail

You can use AWS CloudTrail to track user activity and API usage.

1. Log in AWS account that has a permission for CloudTrail and for CloudWatch.
2. Go to [CloudTrail dashboard](https://ap-northeast-2.console.aws.amazon.com/cloudtrail/home?#/dashboard) and click **Create trail**.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/trail_dashboard.png" alt="cloudtrail dashboard" width=400>
3. Fill in the required fields and make sure you enable **CloudWatch Logs**. Then, press next button.
4. Choose log event types you want to record and configure for them, and finish creating trail.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/trail_created.png" alt="trail created" width=400>

Now, all events are logged with CloudWatch.


### AWS Lambda

Although CloudTrail tracks and records events, it does not send any message by itself. 
You need to process and filter logs, and send message to your slack channel. We are going to use AWS Lambda for this.

1. Log in AWS account that has a permission to create AWS Lambda, and go to the page of AWS Lambda.
2. Click **Create function**.
3. Fill in the required form, select runtime as Python 3.9 or newer, and then create it.
    Now, your function is created. Let's upload code that will be used to process CloudTrail logs.
4. Download [this repository](https://github.com/a2tt/Audit-AWS-IAM-User.git) or git clone it.  
    `$ git clone https://github.com/a2tt/Audit-AWS-IAM-User.git`  
5. Copy `configs.example.py` to `configs.py` and modify it with yours.
6. Archive this directory by executing shell script.  
    > Make sure you have installed python3 on your machine.  

    `$ . zip_function.sh`  

    What this script does is ...

    1. Make directory named 'package'.
    2. Install python packages required into the directory.
    3. Zip python code with the packages.
7. Click **Upload from - .zip file** to upload `function.zip` to AWS Lambda.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/lambda_uploaded.png" alt="upload function" width=400>


### AWS CloudWatch

Finally, you need to configure AWS CloudWatch to trigger the Lambda function.
We are going to use **Subscription filters** functionality.

1. Log in AWS account that has a permission for CloudWatch and go to **CloudWatch - log groups** menu.
2. Find your cloudtrail log groups, and click the group.
3. Click **Subscription filters** tab and press **Create - Create Lambda subscription filter**.  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/cw_subs.png" alt="subscription filter" width=400>
4. Select your Lambda function and set log format as **Amazon CloudTrail**.
5. This step is one of the most important and can be changed for your taste.  
    You can set **Subscription filter pattern** to filter out unwanted events triggering the Lambda. I'm using this rule:
    
    ```plaintext
    { ($.userIdentity.type = "IAMUser") && ($.eventName != "Get*") && ($.eventName != "Describe*") }
    ```

    By filtering "IAMUser", it will trigger Lambda for the logs related to the events triggered by IAM user, 
    and by filtering out "Get*" and "Describe*", you won't receive the rampant and frequent messages that are not likely to be important.

    You can check out what patterns are allowed [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html).
6. It's time to start streaming!  
    <img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/cw_subs_created.png" alt="subscription filter created" width=400>



## Result

When you log in as an IAM user, roam about AWS console, do API call using SDK(e.g. `boto3`) or do API call with `AWS CLI`, you will receive a message about it.

<img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_alert_login.png" alt="login alert" width=300>
<img src="https://raw.githubusercontent.com/a2tt/Audit-AWS-IAM-User/main/docs/images/slack_alert.png" alt="api alert" width=300>



## Conclusion

You should make sure that more important thing than audit is well-defined role-based access control using IAM in order to allow and restrict users to each resources.  
Nonetheless, you can use this simple system for tracking users in a small sized group.
