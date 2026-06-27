"""
Alibaba Cloud OSS Configuration

To use Alibaba Cloud OSS for image storage:
1. Set the environment variables below, OR
2. Edit the values directly in this file

Environment variables:
- OSS_ACCESS_KEY_ID: Your Alibaba Cloud AccessKey ID
- OSS_ACCESS_KEY_SECRET: Your Alibaba Cloud AccessKey Secret
- OSS_BUCKET_NAME: Your OSS bucket name
- OSS_ENDPOINT: Your OSS endpoint (e.g., oss-cn-hangzhou.aliyuncs.com)
- OSS_USE_HTTPS: Set to 'true' to use HTTPS (default: true)

If these are not configured, the app will fall back to local storage.
"""
import os

# OSS Configuration - read from environment variables
OSS_CONFIG = {
    'access_key_id': os.environ.get('OSS_ACCESS_KEY_ID', ''),
    'access_key_secret': os.environ.get('OSS_ACCESS_KEY_SECRET', ''),
    'bucket_name': os.environ.get('OSS_BUCKET_NAME', ''),
    'endpoint': os.environ.get('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com'),
    'use_https': os.environ.get('OSS_USE_HTTPS', 'true').lower() == 'true',
}

# Check if OSS is properly configured
OSS_ENABLED = all([
    OSS_CONFIG['access_key_id'],
    OSS_CONFIG['access_key_secret'],
    OSS_CONFIG['bucket_name'],
    OSS_CONFIG['endpoint'],
])


def get_oss_bucket():
    """Get OSS bucket object. Returns None if not configured."""
    if not OSS_ENABLED:
        return None

    import oss2

    auth = oss2.Auth(
        OSS_CONFIG['access_key_id'],
        OSS_CONFIG['access_key_secret']
    )

    endpoint = OSS_CONFIG['endpoint']
    if OSS_CONFIG['use_https'] and not endpoint.startswith('https://'):
        endpoint = f'https://{endpoint}'
    elif not OSS_CONFIG['use_https'] and not endpoint.startswith('http://') and not endpoint.startswith('https://'):
        endpoint = f'http://{endpoint}'

    bucket = oss2.Bucket(auth, endpoint, OSS_CONFIG['bucket_name'])
    return bucket


def get_oss_base_url():
    """Get the base URL for OSS objects."""
    protocol = 'https' if OSS_CONFIG['use_https'] else 'http'
    return f"{protocol}://{OSS_CONFIG['bucket_name']}.{OSS_CONFIG['endpoint']}"
