import os
import sys

# Ensure backend modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from src.handler import main_handler

if __name__ == "__main__":
    print("====================================")
    print("DAILY TECH BRIEF LOCAL DEMO")
    print("====================================")
    
    os.environ["MOCK_MODE"] = "true"
    
    # Mock AWS environment variables to prevent boto3 from complaining if missing
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
    
    main_handler({}, None)
