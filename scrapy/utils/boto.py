"""Boto/botocore helpers"""

from __future__ import annotations


def is_botocore_available() -> bool:
    try:
        import botocore  # noqa: F401,PLC0415

        return True
    except ImportError:
        return False


def get_botocore_session(
    access_key: str | None = None,
    secret_key: str | None = None,
    session_token: str | None = None,
    region_name: str | None = None,
    role_arn: str | None = None,
    role_session_name: str | None = None,
    external_id: str | None = None,
):
    """Create a botocore session, optionally with auto-refreshing role assumption."""
    import botocore.credentials  # noqa: PLC0415
    import botocore.session  # noqa: PLC0415

    if role_arn:
        base_session = botocore.session.Session()
        if access_key and secret_key:
            base_session.set_credentials(access_key, secret_key, session_token)
        if region_name:
            base_session.set_config_variable("region", region_name)
        extra_args = {"RoleSessionName": role_session_name or "ScrapySession"}
        if external_id:
            extra_args["ExternalId"] = external_id
        fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
            client_creator=base_session.create_client,
            source_credentials=base_session.get_credentials(),
            role_arn=role_arn,
            extra_args=extra_args,
        )
        session = botocore.session.Session()
        session._credentials = botocore.credentials.DeferredRefreshableCredentials(
            method="assume-role",
            refresh_using=fetcher.fetch_credentials,
        )
        if region_name:
            session.set_config_variable("region", region_name)
        return session, True
    session = botocore.session.get_session()
    return session, False
