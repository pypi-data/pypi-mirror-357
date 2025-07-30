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
    ...
