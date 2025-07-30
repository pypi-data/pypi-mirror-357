"""Usage data uploader for S3-compatible storage."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from botocore.client import Config


class UsageUploader:
    """Handles uploading usage data to S3-compatible storage and tracking user sessions."""

    def __init__(self, plan: str = "pro", timezone: str = "Europe/Warsaw"):
        """Initialize uploader with plan and timezone information.

        Args:
            plan: Claude plan type (pro, max5, max20, custom_max)
            timezone: Timezone string for the user
        """
        self.plan = plan
        self.timezone = timezone.replace("/", "_")  # Replace / for filename safety
        self.tracking_file = Path("usage_tracking.json")
        self.bucket_name = "stats"
        
        # Initialize S3 client with hardcoded credentials
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url='https://pcdzssfxzordsxhhvthu.supabase.co/storage/v1/s3',
                aws_access_key_id='9f1db57a7d3b643d28502e1ff67d857b',
                aws_secret_access_key='294773b76f31a88a195252eeee72eb4222e99f989c2f4451b7d2fed62417e08e',
                config=Config(
                    signature_version='s3v4',
                    s3={'addressing_style': 'path'}
                ),
                region_name='us-east-1'  # Default region
            )
        except Exception as e:
            print(f"Failed to initialize S3 client: {e}")
            self.s3_client = None

    def _get_or_create_user_id(self) -> str:
        """Get existing user ID or create a new one.

        Returns:
            Unique user ID
        """
        tracking_data = self._load_tracking_data()

        if "user_id" not in tracking_data:
            tracking_data["user_id"] = str(uuid.uuid4())
            tracking_data["first_run"] = datetime.now().isoformat()
            self._save_tracking_data(tracking_data)

        return tracking_data["user_id"]

    def _load_tracking_data(self) -> Dict[str, Any]:
        """Load tracking data from local file.

        Returns:
            Tracking data dictionary
        """
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_tracking_data(self, data: Dict[str, Any]) -> None:
        """Save tracking data to local file.

        Args:
            data: Tracking data to save
        """
        try:
            self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tracking_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save tracking data: {e}")

    def _add_run_record(self, filename: str) -> None:
        """Add a run record to tracking data.

        Args:
            filename: Name of the uploaded file
        """
        tracking_data = self._load_tracking_data()

        if "runs" not in tracking_data:
            tracking_data["runs"] = []

        run_record = {
            "timestamp": datetime.now().isoformat(),
            "plan": self.plan,
            "timezone": self.timezone,
            "filename": filename,
        }

        tracking_data["runs"].append(run_record)
        self._save_tracking_data(tracking_data)

    def _should_upload(self) -> bool:
        """Check if upload is needed based on plan/timezone changes.

        Returns:
            True if upload is needed, False otherwise
        """
        tracking_data = self._load_tracking_data()
        
        # First run - always upload
        if "last_upload_config" not in tracking_data:
            return True
        
        last_config = tracking_data["last_upload_config"]
        
        # Check if plan or timezone changed
        if last_config.get("plan") != self.plan or last_config.get("timezone") != self.timezone:
            return True
            
        return False
    
    def _update_last_upload_config(self) -> None:
        """Update the last upload configuration in tracking data."""
        tracking_data = self._load_tracking_data()
        tracking_data["last_upload_config"] = {
            "plan": self.plan,
            "timezone": self.timezone,
            "timestamp": datetime.now().isoformat()
        }
        self._save_tracking_data(tracking_data)

    def upload_usage_data(self, data: Dict[str, Any]) -> Optional[str]:
        """Upload usage data to S3 only if plan/timezone changed.

        Args:
            data: Usage data to upload

        Returns:
            Uploaded filename or None if upload failed or not needed
        """
        if not self.s3_client:
            return None
            
        # Check if upload is needed
        if not self._should_upload():
            return None

        # Generate filename
        user_id = self._get_or_create_user_id()
        upload_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"XXXNEW_{self.plan}_{self.timezone}_{user_id}_{upload_date}.json"

        # Save local copy for verification
        local_copy_path = Path("uploads") / filename
        try:
            local_copy_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_copy_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            pass
        # Upload to S3
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2)

            # Upload to S3 bucket
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=json_data.encode("utf-8"),
                ContentType='application/json'
            )

            # Add run record
            self._add_run_record(filename)
            
            # Update last upload config
            self._update_last_upload_config()

            return filename

        except Exception as e:
            print(f"S3 upload failed: {e}")
            return None
