from datetime import datetime
import re

from pydantic import TypeAdapter
from strava_client.constants import DEFAULT_SCOPES
from strava_client.enums.auth import StravaScope
from strava_client.models.api import StravaActivity, StravaActivityStream
from strava_client.models.requests import (
    StravaGetActivitiesRequest,
    StravaGetActivitiesStreamRequest,
    StravaGetTokenRequest,
    StravaGetTokenResponse,
    StravaRefreshTokenRequest,
)
from strava_client.models.settings import StravaSettings
import webbrowser
import requests


class StravaClient:
    """
    Tiny wrapper around the Strava API.
    """

    BASE_OAUTH_URL = "https://www.strava.com/oauth"
    BASE_SERVER_URL = "https://www.strava.com/api/v3"

    def __init__(
        self,
        scopes: list[StravaScope | str] | None = None,
        settings: StravaSettings | None = None,
        dump_settings: bool = True,
    ):
        """
        Initialize the Strava client.

        Args:
            scopes (list[StravaScope | str] | None):
                The scopes to request. If None, the default scopes are used.
            settings (StravaSettings | None):
                The settings to use. If None, settings are loaded from environment variables
                or from the default settings file.
            dump_settings (bool):
                Whether to dump the settings to the file after initialization.
                This allows to save some time on following runs, as the access token
                and refresh token will be already set.
        """
        self.settings = settings if settings else StravaSettings()  # type: ignore
        self.dump_settings = dump_settings

        if scopes is None:
            self.scopes = DEFAULT_SCOPES
        else:
            self.scopes = list(
                map(lambda x: StravaScope(x) if isinstance(x, str) else x, scopes)
            )

        self._verify_initialization()

    def get_activities(
        self,
        before: datetime | None = None,
        after: datetime | None = None,
        page: int = 1,
        per_page: int = 30,
    ) -> list[StravaActivity]:
        """
        Get the activities for the authenticated user.

        See the Strava API documentation for more details:
        https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
        Args:
            before (datetime | None):
                The date before which to retrieve activities.
                If None, no limit is applied.
            after (datetime | None):
                The date after which to retrieve activities.
                If None, no limit is applied.
            page (int):
                The page number to retrieve.
            per_page (int):
                The number of activities per page.

        Returns:
            list[StravaActivity]:
                The list of activities.
        """

        self._verify_token()

        url = f"{self.BASE_SERVER_URL}/athlete/activities"

        # # Set the headers

        headers = {"Authorization": f"Bearer {self.settings.access_token}"}

        # Make the GET request
        response = requests.get(
            url,
            headers=headers,
            params=StravaGetActivitiesRequest(
                before=before,
                after=after,
                page=page,
                per_page=per_page,
            ).model_dump(),
        )

        if response.status_code != 200:
            raise ValueError(
                f"Failed to retrieve activities. Status code: {response.status_code}."
                f" Response: {response.text}"
            )

        list_act_adapter = TypeAdapter(list[StravaActivity])
        return list_act_adapter.validate_python(response.json())

    def get_activity_stream(
        self,
        id: str,
        keys: list[str] | None = None,
    ) -> StravaActivityStream:
        """
        Get the activity stream for a given activity ID.
        See the Strava API documentation for more details:
        https://developers.strava.com/docs/reference/#api-Streams-getActivityStreams

        Args:
            id (str):
                The ID of the activity.
            keys (list[str] | None):
                The keys of the streams to retrieve.
                If None, all streams are retrieved.

        Returns:
            StravaActivityStream:
                The activity stream.
        """

        self._verify_token()

        url = f"{self.BASE_SERVER_URL}/activities/{id}/streams"

        # # Set the headers

        headers = {"Authorization": f"Bearer {self.settings.access_token}"}

        if keys is None:
            keys = []

        # Make the GET request
        response = requests.get(
            url,
            headers=headers,
            params=StravaGetActivitiesStreamRequest(
                keys=keys,
            ).model_dump(),
        )

        if response.status_code != 200:
            raise ValueError(
                f"Failed to retrieve activity streams. Status code: {response.status_code}."
                f" Response: {response.text}"
            )

        stream_set_adapter = TypeAdapter(StravaActivityStream)
        return stream_set_adapter.validate_python(response.json())

    def _verify_token(self):
        """
        Verify whether the access token is still valid.
        If not, refresh it and update the settings.
        """

        if (
            self.settings.expires_at is not None
            and int(datetime.now().timestamp()) >= self.settings.expires_at
        ):
            # Token expired or missing expiration time.

            strava_refresh_token_response = self._refresh_token()
            self._update_settings_and_dump(strava_refresh_token_response)

    def _update_settings_and_dump(self, response: StravaGetTokenResponse):
        """
        Update the settings after receiving a new access token
        and dump them to the file, if required.
        """

        self.settings.access_token = response.access_token
        self.settings.refresh_token = response.refresh_token
        self.settings.expires_at = response.expires_at

        if self.dump_settings:
            self.settings.dump()

    def _verify_initialization(self):
        """
        Verify whether the application was just created
        and needs to get authentication for the desired scopes.
        """

        if not self.settings.refresh_token:
            # Not initialized. Open the browser to let
            # the user grant scopes

            auth_code = self._request_auth_code()

            # Now get the access token, refresh token and expiration time
            strava_get_token_response = self._get_access_token(auth_code)

            self._update_settings_and_dump(strava_get_token_response)

    def _get_access_token(self, auth_code: str) -> StravaGetTokenResponse:
        """
        Get the access token, refresh token and expiration time
        by exchanging the authorization code.
        """

        response = requests.post(
            f"{self.BASE_OAUTH_URL}/token",
            data=StravaGetTokenRequest(
                client_id=self.settings.client_id,
                client_secret=self.settings.client_secret,
                code=auth_code,
            ).model_dump(),
        )

        if response.status_code != 200:
            raise ValueError(
                f"Failed to get access token. Status code: {response.status_code}"
                f"Response: {response.text}"
            )

        return StravaGetTokenResponse.model_validate(response.json())

    def _request_auth_code(self) -> str:
        """
        Initialize the scopes for the application
        by requesting an authorization code.

        Returns:
            str:
                The authorization code.
        """

        # The composition of the URL is described here:
        # https://developers.strava.com/docs/getting-started/#oauth

        url = f"{self.BASE_OAUTH_URL}/authorize"  # base url for the OAuth process
        url += f"?client_id={self.settings.client_id}"  # add the client ID
        url += "&response_type=code"
        url += "&redirect_uri=http://localhost/exchange_token"  # redirect URI
        url += "&approval_prompt=force"
        url += f"&scope={StravaScope.to_query_string_list(self.scopes)}"

        # Open the browser to let the user grant the scopes
        webbrowser.open(url, new=0)

        # Get the url. The user might also skip this part,
        # obtain the code by themselves, paste it in the settings and
        # recreate the client.

        response_url = input(
            "Please paste the url obtained after granting the scopes: "
        )

        # Extract the code from the URL

        auth_code = re.search(r"code=(\w+)", response_url)

        if not auth_code:
            raise ValueError("Failed to extract the authorization code.")

        auth_code = auth_code.group(1)  # type: ignore

        return auth_code  # type: ignore

    def _refresh_token(self) -> StravaGetTokenResponse:
        """
        Refresh the access token.
        """

        if self.settings.refresh_token is None:
            raise ValueError("No refresh token provided")

        response = requests.post(
            f"{self.BASE_OAUTH_URL}/token",
            data=StravaRefreshTokenRequest(
                client_id=self.settings.client_id,
                client_secret=self.settings.client_secret,
                refresh_token=self.settings.refresh_token,
            ).model_dump(),
        )

        if response.status_code != 200:
            raise ValueError(
                f"Failed to refresh token. Status code: {response.status_code}"
            )

        return StravaGetTokenResponse.model_validate(response.json())
