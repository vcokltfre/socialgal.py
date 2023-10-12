from io import BufferedReader
from typing import Any, Final, Literal, TypeVar

from httpx import AsyncClient, Response
from httpx._types import QueryParamTypes, RequestData, RequestFiles

from ..types import Post, User

API_URL: Final[str] = "https://social.gal/api"


class Unset:
    pass


MaybeT = TypeVar("MaybeT")
MaybeUnset = MaybeT | Unset

UNSET = Unset()


class Client:
    __slots__ = (
        "__session",
        "__session_token",
        "__token",
    )

    def __init__(self, token: str, session: str) -> None:
        self.__token = token
        self.__session_token = session

        self.__session: AsyncClient | None = None

    @property
    def _session(self) -> AsyncClient:
        if not self.__session:
            raise Exception("Client is not initialised.")

        return self.__session

    async def __aenter__(self) -> "Client":
        self.__session = AsyncClient(
            headers={
                "Authorization": f"{self.__token}",
                "User-Agent": "Bot (socialgal.py/1.0.0)",
            },
            cookies={
                "session": self.__session_token,
            },
        )
        return self

    async def __aexit__(self, *_exc: Any) -> None:
        await self._session.aclose()
        self.__session = None

    async def request(
        self,
        method: str,
        path: str,
        params: QueryParamTypes | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        **kwargs: Any,
    ) -> Response:
        resp = await self._session.request(
            method,
            API_URL + path,
            params=params,
            data=data,
            files=files,
            **kwargs,
        )

        if resp.status_code >= 400:
            raise Exception(resp.text)

        return resp

    async def get_user(self, user_id: str) -> User:
        return User.from_data(self, (await self.request("GET", f"/user/{user_id}")).json())

    async def update_user(
        self,
        username: MaybeUnset[str] = UNSET,
        about_me: MaybeUnset[str] = UNSET,
        display_name: MaybeUnset[str] = UNSET,
        avatar: MaybeUnset[BufferedReader] = UNSET,
        banner: MaybeUnset[BufferedReader] = UNSET,
    ) -> User:
        data: dict[str, Any] = {}

        if username is not UNSET:
            data["username"] = username

        if about_me is not UNSET:
            data["about_me"] = about_me

        if display_name is not UNSET:
            data["display_name"] = display_name

        files = {}

        if avatar is not UNSET:
            data["update_avatar"] = True
            files["avatar_file"] = avatar

        if banner is not UNSET:
            data["update_banner"] = True
            files["banner_file"] = banner

        new_data = (await self.request("PATCH", "/user", data=data, files=files)).json()

        return User.from_data(self, new_data)

    async def follow_user(self, user_id: str) -> None:
        await self.request("POST", f"/user/{user_id}/follow")

    async def unfollow_user(self, user_id: str) -> None:
        await self.request("DELETE", f"/user/{user_id}/follow")

    async def get_post(self, post_id: str) -> Post:
        return Post.from_data(self, (await self.request("GET", f"/post/{post_id}")).json())

    async def get_posts(
        self,
        offset: int = 0,
        amount: int = 24,
        search_mode: Literal["all", "following"] = "all",
        user_id: str | None = None,
        user_search_mode: Literal["posts", "replies"] = "posts",
    ) -> list[Post]:
        return [
            Post.from_data(self, post)
            for post in (
                await self.request(
                    "GET",
                    "/posts",
                    params={
                        "offset": offset,
                        "amount": amount,
                        **(
                            {
                                "search_mode": search_mode,
                            }
                            if not user_id
                            else {}
                        ),
                        **({"user_id": user_id, "user_search_mode": user_search_mode} if user_id else {}),
                    },
                )
            ).json()
        ]

    async def create_post(
        self,
        content: str,
        reply_id: str | None = None,
        quote_id: str | None = None,
        files: list[BufferedReader] | None = None,
    ) -> Post:
        data = {
            "post_content": content,
        }

        file_data = {}

        if reply_id:
            data["reply_id"] = reply_id

        if quote_id:
            data["quote_id"] = quote_id

        if files:
            for i, file in enumerate(files):
                file_data[f"file_{i}"] = file

        return Post.from_data(self, (await self.request("POST", "/posts", data=data, files=file_data)).json())

    async def delete_post(self, post_id: str) -> None:
        await self.request("DELETE", f"/posts/{post_id}")

    async def like_post(self, post_id: str) -> None:
        await self.request("POST", f"/posts/{post_id}/like")

    async def unlike_post(self, post_id: str) -> None:
        await self.request("DELETE", f"/posts/{post_id}/like")

    async def report_post(self, post_id: str) -> None:
        await self.request("POST", f"/posts/{post_id}/report")

    async def get_post_replies(self, post_id: str) -> list[Post]:
        return [Post.from_data(self, post) for post in (await self.request("GET", f"/posts/{post_id}/replies")).json()]

    async def pin_post(self, post_id: str) -> None:
        await self.request("POST", f"/posts/{post_id}/pin")

    async def unpin_post(self, post_id: str) -> None:
        await self.request("DELETE", f"/posts/{post_id}/pin")
