from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from ..client import Client
else:
    Client = Any


class UserData(TypedDict):
    id: str
    username: str
    display_name: str
    avatar_url: str
    banner_url: str
    about_me: str
    user_attributes: list[str]
    account_created_at: int
    following: bool
    follower_count: int
    following_count: int
    post_count: int


@dataclass(slots=True)
class User:
    _client: Client
    id: str
    username: str
    display_name: str
    avatar_url: str
    banner_url: str
    about_me: str
    attributes: list[str]
    created_at: datetime
    following: bool
    follower_count: int
    following_count: int
    post_count: int

    @classmethod
    def from_data(cls, client: Client, data: UserData) -> "User":
        return cls(
            _client=client,
            id=data["id"],
            username=data["username"],
            display_name=data["display_name"],
            avatar_url=data["avatar_url"],
            banner_url=data["banner_url"],
            about_me=data["about_me"],
            attributes=[attr for attr in data["user_attributes"] if attr],
            created_at=datetime.fromtimestamp(data["account_created_at"]),
            following=data["following"],
            follower_count=data["follower_count"],
            following_count=data["following_count"],
            post_count=data["post_count"],
        )

    async def follow(self) -> None:
        await self._client.follow_user(self.id)

    async def unfollow(self) -> None:
        await self._client.unfollow_user(self.id)
