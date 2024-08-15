import datetime
import re

import aiohttp

import breadcord


class BadResponseError(Exception):
    pass


class SpotifyAPI:
    def __init__(self, *, session: aiohttp.ClientSession, settings: breadcord.config.SettingsGroup) -> None:
        self.settings = settings
        self.session = session

        self._spotify_token: str | None = None
        self._spotify_token_expires_at: datetime.datetime | None = None

    async def update_spotify_token(self) -> None:
        if (
            self._spotify_token_expires_at is not None
            and self._spotify_token_expires_at < datetime.datetime.now() + datetime.timedelta(minutes=15)
        ):
            return
        async with self.session.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.settings.spotify.client_id.value,  # type: ignore[attr-defined]
                "client_secret": self.settings.spotify.client_secret.value,  # type: ignore[attr-defined]
            },
        ) as response:
            data = await response.json()
            if data.get("error") == "invalid_client":
                raise ValueError("Invalid spotify client id or secret")
            self._spotify_token = data["access_token"]
            self._spotify_token_expires_at = datetime.datetime.now() + datetime.timedelta(seconds=data["expires_in"])

    async def fetch_track_data(self, track_id: str) -> dict:
        await self.update_spotify_token()
        async with self.session.get(
            f"https://api.spotify.com/v1/tracks/{track_id}",
            headers={"Authorization": f"Bearer {self._spotify_token}"},
        ) as response:
            if response.status == 401:
                raise BadResponseError("Invalid spotify token")
            elif response.status != 200:
                raise BadResponseError("Could not get track data")
            elif not response.ok:
                raise BadResponseError(f"{response.status} Could not get track data: {response.reason}")
            return await response.json()


