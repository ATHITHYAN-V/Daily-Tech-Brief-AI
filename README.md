# Daily Tech Brief

**While you were away, technology changed.**

Daily Tech Brief is a completely free, anonymous, always-on AI technology news agent. Built for the AWS Builder Center Weekend Challenge, it demonstrates an autonomous scheduled agent that creates original content without user initiation.

## Architecture

![Architecture](https://via.placeholder.com/800x400?text=EventBridge+->+Lambda+(Bedrock,+Polly)+->+S3+<-+Amplify)

At 06:00 UTC daily:
1. **EventBridge Scheduler** wakes up the system.
2. **AWS Lambda** executes the autonomous agent worker.
3. The worker fetches public RSS feeds (Hacker News, TechCrunch, AWS Blogs, etc.).
4. News is cleaned and deduplicated deterministically.
5. **Amazon Bedrock (Claude 3.5 Sonnet / Nova Lite)** is invoked as the "Autonomous Editor" to analyze the unique stories, select the top 10 most impactful ones, and generate an original radio-style script with commentary and transitions.
6. **Amazon Polly (Neural Newscaster)** synthesizes the script into a professional MP3 audio briefing.
7. The audio, metadata, and JSON transcripts are published to an **Amazon S3** bucket.
8. The React frontend, hosted via **AWS Amplify**, automatically displays the new episode for any visitor.

## AWS Services Used

- **Amazon EventBridge Scheduler**: Autonomously triggers the daily workflow.
- **AWS Lambda**: Serverless compute to execute the Python agent pipeline.
- **Amazon Bedrock**: Provides the AI reasoning to deduplicate events, select top stories, and write the creative briefing script.
- **Amazon Polly**: Synthesizes the generated script into high-quality spoken audio using the Neural Newscaster style.
- **Amazon S3**: Stores the generated artifacts (JSON and MP3) and serves them to the frontend via CORS.
- **AWS Amplify Hosting**: Hosts the React frontend application.
- **Amazon CloudWatch**: Captures structured logs to demonstrate autonomous behavior and pipeline success metrics.

## Local Development (Mock Mode)

You can run the entire backend pipeline locally without invoking AWS services or incurring charges.

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the local demo script:
   ```bash
   python scripts/run_local_demo.py
   ```
   This will fetch live RSS feeds, but mock the Bedrock, Polly, and S3 stages, saving the output to `local_output/`.

4. Run the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## AWS Deployment

### 1. Backend Infrastructure (CloudFormation)

Deploy the backend resources using the provided CloudFormation template:

```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation.yaml \
  --stack-name daily-tech-brief-backend \
  --capabilities CAPABILITY_IAM
```

**Note**: Ensure your AWS account has model access enabled in Amazon Bedrock for your chosen model (`anthropic.claude-3-5-sonnet-20240620-v1:0` by default).

To deploy the Lambda code, you will need to zip the `backend/src` and its dependencies, upload it to an S3 bucket, and update the CloudFormation template `Code` property before deploying.

### 2. Frontend Deployment (AWS Amplify)

1. Push this repository to GitHub.
2. Go to the AWS Amplify Console.
3. Choose "Host your web app" and select GitHub.
4. Select the repository and branch.
5. In the build settings, set the base directory to `frontend`.
6. Add the environment variable `VITE_S3_BASE_URL` pointing to your CloudFormation S3 bucket's public URL.
7. Deploy.

## How to Verify Autonomous Execution

To prove the application operates autonomously for the AWS Builder Challenge:

1. **EventBridge**: Show the rule `daily-tech-brief-schedule` configured for `06:00 UTC`.
2. **CloudWatch Logs**: View the logs for the Lambda function. You will see a structured summary like:
   ```
   [START] Execution ID: ...
   Sources: 12 attempted, 11 successful, 1 failed
   Articles: 143 collected, 37 duplicates/invalid, 106 unique
   Bedrock: 106 analyzed, 10 selected
   Script: 845 words
   Polly: Audio generated
   S3: Upload successful
   [COMPLETE]
   ```
3. **S3 / Website**: Open the live website and see the newly generated episode appear without any user interaction.
