# aws_ssm_env/ssm.py
import boto3
import os
from typing import List, Dict

def get_env_parameters_from_ssm(
    account_id: str,
    region: str,
    role_name: str,
    parameter_names: List[str],
    with_decryption: bool = True
) -> Dict[str, str]:
    """
    Fetch parameters from AWS SSM Parameter Store, using default credentials or
    assuming a specified IAM role.

    Args:
        account_id (str): AWS Account ID.
        region (str): AWS Region.
        role_name (str): IAM role name to assume (optional).
        parameter_names (List[str]): List of parameter names to fetch.
        with_decryption (bool): Whether to decrypt secure string parameters.

    Returns:
        Dict[str, str]: Dictionary of parameter names and their values.
    """

    def create_ssm_client() -> boto3.client:
        """Creates an SSM client using default credentials or assumed role."""
        if role_name:
            sts_client = boto3.client("sts")
            response = sts_client.assume_role(
                RoleArn=f"arn:aws:iam::{account_id}:role/{role_name}",
                RoleSessionName="SSMParameterSession"
            )
            creds = response["Credentials"]
            return boto3.client(
                "ssm",
                region_name=region,
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"],
            )
        else:
            return boto3.client("ssm", region_name=region)

    ssm_client = create_ssm_client()

    response = ssm_client.get_parameters(
        Names=parameter_names,
        WithDecryption=with_decryption
    )

    parameters = {param["Name"]: param["Value"] for param in response.get("Parameters", [])}

    if response.get("InvalidParameters"):
        raise ValueError(f"Invalid parameters: {response['InvalidParameters']}")

    return parameters
