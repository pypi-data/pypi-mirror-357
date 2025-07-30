from typing import Dict, Optional

from google.analytics.admin import AnalyticsAdminServiceClient
from google.api_core.exceptions import PermissionDenied, InvalidArgument, ServiceUnavailable
from google.oauth2 import service_account
from google.auth.exceptions import RefreshError
from google.analytics.data_v1beta.types import FilterExpression, Filter

from arcane.core import UserRightsEnum, RightsLevelEnum, BadRequestError, BaseAccount
from arcane.credentials import get_user_decrypted_credentials
from arcane.datastore import Client as DatastoreClient
from arcane.requests import call_get_route

from .exception import GoogleAnalyticsV4AccountException, GoogleAnalyticsV4ServiceDownException


def get_google_analytics_v4_account(
    base_account: BaseAccount,
    clients_service_url: Optional[str] = None,
    firebase_api_key: Optional[str] = None,
    gcp_service_account: Optional[str] = None,
    auth_enabled: bool = True
) -> Dict:
    """Call get endpoint to retrieve ga4 account

    Args:
        base_account (BaseAccount): base account to get
        clients_service_url (Optional[str], optional): clients service url to call. Defaults to None.
        firebase_api_key (Optional[str], optional): needed for calling api. Defaults to None.
        gcp_service_account (Optional[str], optional): needed for calling api. Defaults to None.
        auth_enabled (bool, optional): Boolean to know if we should use token while calling api. Defaults to True.

    Raises:
        BadRequestError: The request does not comply function requirement. See error message for more info

    Returns:
        Dict: ga4 account
    """
    if not (clients_service_url and firebase_api_key and gcp_service_account):
        raise BadRequestError('clients_service_url or firebase_api_key or gcp_service_account should not be None if google analytics v4 account is not provided')
    url = f"{clients_service_url}/api/google-analytics-account/v4?account_id={base_account['id']}&client_id={base_account['client_id']}"
    accounts = call_get_route(
        url,
        firebase_api_key,
        claims={'features_rights':{UserRightsEnum.AMS_GTP: RightsLevelEnum.VIEWER}, 'authorized_clients': ['all']},
        auth_enabled=auth_enabled,
        credentials_path=gcp_service_account
    )
    if len(accounts) == 0:
        raise BadRequestError(f'Error while getting google analytics v4 account with: {base_account}. No account corresponding.')
    elif len(accounts) > 1:
        raise BadRequestError(f'Error while getting google analytics v4 account with: {base_account}. Several account corresponding: {accounts}')

    return accounts[0]



def check_access_before_creation(property_id: str,
                                    user_email: str,
                                    gcp_service_account: str,
                                    secret_key_file: str,
                                    gcp_project: str,
                                    by_pass_user_check: Optional[bool] = False,
                                    datastore_client: Optional[DatastoreClient] = None) -> bool:
    """ check access before posting account

    Args:
        property_id (str): the id of the property we want access
        user_email (str): the email of the user checking access
        gcp_service_account (str): Arcane credential path
        secret_key_file (str): the secret file
        gcp_project (str): the Google Cloud Plateform project
        by_pass_user_check (Optional[bool], optional): By pass user access, used for super admin right. Defaults to False.
        datastore_client (Optional[DatastoreClient], optional): the Datastore client. Defaults to None.

    Raises:
        BadRequestError: Raised when arguments are not good
        GoogleAnalyticsV4AccountException: Raised when we have no access

    Returns:
        bool: should use user access
    """
    should_use_user_access = True
    scopes = ['https://www.googleapis.com/auth/analytics.readonly']

    if not secret_key_file:
        raise BadRequestError('secret_key_file should not be None while using user access protocol')

    user_credentials = get_user_decrypted_credentials(
            user_email=user_email,
            secret_key_file=secret_key_file,
            gcp_credentials_path=gcp_service_account,
            gcp_project=gcp_project,
            datastore_client=datastore_client
        )

    try:
        client = AnalyticsAdminServiceClient(credentials=user_credentials)
        _get_property_name_lgq(client, property_id, user_email)
    except GoogleAnalyticsV4AccountException as e:
        if not by_pass_user_check:
            raise e
        should_use_user_access = False
        pass

    arcane_credentials = service_account.Credentials.from_service_account_file(gcp_service_account, scopes=scopes)
    try:
        client = AnalyticsAdminServiceClient(credentials=arcane_credentials)
        _get_property_name_lgq(client, property_id, user_email)
        should_use_user_access = False
    except GoogleAnalyticsV4AccountException as e:
        if by_pass_user_check and not should_use_user_access:
            raise e
        pass

    return should_use_user_access


def _get_property_name_lgq(client: AnalyticsAdminServiceClient, property_id: str, user_email: str):
    try:
        property_ = client.get_property(name=f"properties/{property_id}")
    except PermissionDenied:
        if user_email:
            raise GoogleAnalyticsV4AccountException(
                f'{user_email} cannot access your property with the id: {property_id}. Are you sure he has access and that the ID is correct?'
            )
        raise GoogleAnalyticsV4AccountException(
            f'We cannot access your property with the id: {property_id}. Are you sure you gave us access and entered the correct ID?'
        )
    except InvalidArgument as err:
        raise GoogleAnalyticsV4AccountException(str(err))
    except ServiceUnavailable as err:
        if 'invalid_grant' in str(err):
            raise GoogleAnalyticsV4AccountException(
                f"{user_email} authorization has expired. Please renew the access to {property_id}."
            )
        down_message = f"The Google Analytics 4 API does not respond. Thus, we cannot check if we can access your Google Analytics 4 account with the id: {property_id}. Please try later"
        raise GoogleAnalyticsV4ServiceDownException(down_message)
    except RefreshError as err:
        if ('Token has been expired' in str(err) or 'invalid_grant' in str(err)):
            print(str(err))
            if 'Account has been deleted' in str(err):
                raise GoogleAnalyticsV4AccountException(
                    f"{user_email} account has been deleted and can no longer access to {property_id}."
            )

            raise GoogleAnalyticsV4AccountException(
                f"{user_email} authorization has expired. Please renew the access to {property_id}."
            )
    return str(property_.display_name)


def _build_dimension_filter(dimension_filter_dict: Dict):
    if dimension_filter_dict is None:
        return None

    if dimension_filter_dict['filter_type'] != 'string':
        raise ValueError(f'Filter Type {dimension_filter_dict["filter_type"]} is not supported')

    return FilterExpression(
        filter=Filter(
            field_name=dimension_filter_dict['key'],
            string_filter=Filter.StringFilter(
                value=dimension_filter_dict['value'],
                case_sensitive=dimension_filter_dict['case_sensitive'],
                match_type=dimension_filter_dict['match_type']
            )
        )
    )
