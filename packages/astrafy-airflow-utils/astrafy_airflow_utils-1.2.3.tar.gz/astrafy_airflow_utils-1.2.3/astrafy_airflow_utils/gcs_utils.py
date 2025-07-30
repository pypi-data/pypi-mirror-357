from astrafy_environment import AstrafyEnvironment

def get_gcs_bucket_path(environment: AstrafyEnvironment) -> str:
    """
    Constructs the GCS bucket path using the environment configuration.
    
    @param environment: AstrafyEnvironment instance with the configuration
    @return: The constructed GCS bucket path
    """
    return f"gs://{environment.bucket_folder_results}"

def upload_to_gcs(environment: AstrafyEnvironment, target_path: str = "") -> str:
    """
    Generates command to upload dbt artifacts to GCS.
    
    @param environment: AstrafyEnvironment instance with the configuration
    @param target_path: Optional target path within the /app directory
    @return: The bash command string
    """
    bucket_path = get_gcs_bucket_path(environment)
    
    # If target_path is provided, use it in the path, otherwise use the default.
    path = f"/app/{target_path}/target" if target_path else "/app/target"
    
    return f"""
    gcloud storage cp {path}/*.json {bucket_path}/
    """

def download_failed_models(environment: AstrafyEnvironment, target_path: str = "") -> str:
    """
    Generates command to download previous dbt artifacts from GCS.
    
    @param environment: AstrafyEnvironment instance with the configuration
    @return: The bash command string
    """
    bucket_path = get_gcs_bucket_path(environment)
    path = f"/app/{target_path}/target" if target_path else "/app/target"
    return f"""
    mkdir -p {path}
    gcloud storage cp -r {bucket_path}/* /app/target/
    """