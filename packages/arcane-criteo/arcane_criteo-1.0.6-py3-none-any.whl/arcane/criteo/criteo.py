import json
from typing import List, Optional, Union
import hmac
import hashlib
from datetime import date, datetime, timedelta

from .exceptions import CriteoAccountLostAccessException

from criteo_api_marketingsolutions_v2023_01 import Configuration, ApiClient
from criteo_api_marketingsolutions_v2023_01.api.analytics_api import AnalyticsApi
from criteo_api_marketingsolutions_v2023_01.api.advertiser_api import AdvertiserApi
from criteo_api_marketingsolutions_v2023_01.api.campaign_api import CampaignApi
from criteo_api_marketingsolutions_v2023_01.model.ad_set_search_filter import AdSetSearchFilter
from criteo_api_marketingsolutions_v2023_01.model.request_ad_set_search import RequestAdSetSearch
from criteo_api_marketingsolutions_v2023_01.model.statistics_report_query_message import StatisticsReportQueryMessage

from criteo_api_marketingsolutions_v2023_01.exceptions import ApiValueError

from criteo_api_marketingsolutions_v2023_01 import model_utils

# Monkey patch for old campain with None value for 'media_type' (ex: Devred)
def check_allowed_values(allowed_values, input_variable_path, input_values):
    """Raises an exception if the input_values are not allowed

    Args:
        allowed_values (dict): the allowed_values dict
        input_variable_path (tuple): the path to the input variable
        input_values (list/str/int/float/date/datetime): the values that we
            are checking to see if they are in allowed_values
    """
    these_allowed_values = list(allowed_values[input_variable_path].values())
    if (isinstance(input_values, list)
            and not set(input_values).issubset(
                set(these_allowed_values))):
        invalid_values = ", ".join(
            map(str, set(input_values) - set(these_allowed_values))),
        raise ApiValueError(
            "Invalid values for `%s` [%s], must be a subset of [%s]" %
            (
                input_variable_path[0],
                invalid_values,
                ", ".join(map(str, these_allowed_values))
            )
        )
    elif (isinstance(input_values, dict)
            and not set(
                input_values.keys()).issubset(set(these_allowed_values))):
        invalid_values = ", ".join(
            map(str, set(input_values.keys()) - set(these_allowed_values)))
        raise ApiValueError(
            "Invalid keys in `%s` [%s], must be a subset of [%s]" %
            (
                input_variable_path[0],
                invalid_values,
                ", ".join(map(str, these_allowed_values))
            )
        )
    elif (input_values is not None and not isinstance(input_values, (list, dict))
            and input_values not in these_allowed_values):

        raise ApiValueError(
            "Invalid value for `%s` (%s), must be one of %s" %
            (
                input_variable_path[0],
                input_values,
                these_allowed_values
            )
        )

model_utils.check_allowed_values = check_allowed_values

class CriteoClient:
    consent_url = "https://consent.criteo.com/request{query}&signature={signature}"

    def __init__(self, criteo_credentials_path: str, criteo_signing_path: Optional[str] = None) -> None:
        with open(criteo_credentials_path) as credentials:
            criteo_credentials = json.load(credentials)
        self._client_id = criteo_credentials.get('client_id')
        self._client_secret = criteo_credentials.get('client_secret')

        if criteo_signing_path is not None:
            with open(criteo_signing_path) as credentials:
                criteo_signing_credentials = json.load(credentials)
            self._signing_key_id = criteo_signing_credentials['signing_key_id']
            self._signing_key_secret = criteo_signing_credentials['signing_key_secret']

    def get_query(self, timestamp: float, state: str, redirect_uri: str):
        query = f"?key={self._signing_key_id}&timestamp={timestamp}&state={state}&redirect-uri={redirect_uri}"
        return query

    def get_consent_signature(self, timestamp: float, state: str, redirect_uri: str):
        query = self.get_query(timestamp, state, redirect_uri)
        return self.get_hashed_value(query.encode('utf-8'))

    def get_hashed_value(self, content_to_hash: bytes):
        m = hmac.new(
            self._signing_key_secret.encode('utf-8'),
            digestmod=hashlib.sha512
        )
        m.update(content_to_hash)
        return m.hexdigest()

    def get_campaigns(self, advertiser_id: str):
        configuration = Configuration(
            username=self._client_id,
            password=self._client_secret,
            discard_unknown_keys=True,
        )
        request_ad_set_search = RequestAdSetSearch(
            filters=AdSetSearchFilter(advertiser_ids=[advertiser_id]))
        client = ApiClient(configuration)
        campaign_api = CampaignApi(client)
        resp = campaign_api.search_ad_sets(
              request_ad_set_search=request_ad_set_search)
        campaigns = resp.data
        return [
            {
                "id": campaign.id,
                "type": campaign.type,
                "name": campaign.attributes.name,
                "status": campaign.attributes.schedule.activation_status,
            } for campaign in campaigns
        ]

    def get_advertisers(self):
        configuration = Configuration(username=self._client_id, password=self._client_secret)
        client = ApiClient(configuration)
        api = AdvertiserApi(client)
        resp = api.api_portfolio_get()
        return [{"id": advertiser.id, "name": advertiser.attributes.advertiser_name}
                for advertiser in resp.data]

    def check_access_account(self, adverstiser_id: str):
        "From client secret id and client secret, check if Arcane has access to it"
        advertisers = self.get_advertisers()
        try:
            next(
                advertiser for advertiser in advertisers if advertiser['id'] == adverstiser_id)
        except StopIteration:
            raise CriteoAccountLostAccessException(
                f'We do not have access to advertiser {adverstiser_id}')

    def get_report(self,
                   account_id: str, *,
                   start_date: Union[datetime, date],
                   dimensions: Optional[List] = None,
                   metrics: Optional[List] = None,
                   end_date: Optional[Union[datetime, date]] = None
                   ) -> str:
        """Download a statistics report from Criteo API
        See more info on the official documentation https://developers.criteo.com/marketing-solutions/docs/analytics
        Args:
            account_id (str): The id of the account targeted
            start_date (Union[datetime, date]): the first date of the report
            dimensions (Optional[List], optional): Dimensions allow you to specify the aggregation level suited to your needs. Defaults to None.
            metrics (Optional[List], optional): Metrics refer to measurements such as clicks, revenue, or cost per visit. Defaults to None.
            end_date (Optional[Union[datetime, date]], optional): the last date of the report. Defaults to None.
        Returns:
            [str]: a CSV string containing all the requested data
        """
        if dimensions is None:
            dimensions = ["AdvertiserId", "Advertiser", "AdsetId", "Adset", "Day"]
        if metrics is None:
            metrics = [
                "Clicks", "Displays", "AdvertiserCost", "SalesPc30d",
                "ConversionRatePc30d", "ClickThroughRate", "ECosPc30d", "Cpc",
                "RoasPc30d"
            ]
        if end_date is None:
            end_date = datetime.today() - timedelta(days=1)

        if type(start_date) is date:
            start_date = datetime.combine(start_date, datetime.min.time())

        if type(end_date) is date:
            end_date = datetime.combine(end_date, datetime.min.time())

        configuration = Configuration(username=self._client_id, password=self._client_secret)
        client = ApiClient(configuration)
        api = AnalyticsApi(client)
        stats_query_message = StatisticsReportQueryMessage(
            advertiser_ids=account_id,
            dimensions=dimensions,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
            currency="EUR",
            format="Csv")

        response_content = api.get_adset_report(statistics_report_query_message=stats_query_message)
        return response_content

