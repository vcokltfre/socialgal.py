from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, TypedDict

from .user import User, UserData

if TYPE_CHECKING:
    from ..client import Client
else:
    Client = Any


class PostActionsData(TypedDict):
    like_count: int
    post_liked: bool
    post_reposted: bool


class PostData(TypedDict):
    id: str
    author: UserData
    content: str
    timestamp: int
    actions: PostActionsData
    quoted_post: Optional["PostData"]
    replied_post: Optional["PostData"]
    file_urls: list[str]
    share_url: str


@dataclass(slots=True)
class Post:
    _client: Client
    id: str
    author: User
    content: str
    timestamp: datetime
    like_count: int
    liked: bool
    reposted: bool
    quoted_post: Optional["Post"]
    replied_post: Optional["Post"]
    file_urls: list[str]
    share_url: str

    @classmethod
    def from_data(cls, client: Client, data: PostData) -> "Post":
        return cls(
            _client=client,
            id=data["id"],
            author=User.from_data(client, data["author"]),
            content=data["content"],
            timestamp=datetime.fromtimestamp(data["timestamp"]),
            like_count=data["actions"]["like_count"],
            liked=data["actions"]["post_liked"],
            reposted=data["actions"]["post_reposted"],
            quoted_post=Post.from_data(client, data["quoted_post"]) if data["quoted_post"] else None,
            replied_post=Post.from_data(client, data["replied_post"]) if data["replied_post"] else None,
            file_urls=data["file_urls"],
            share_url=data["share_url"],
        )

    async def delete(self) -> None:
        await self._client.delete_post(self.id)

    async def report(self) -> None:
        await self._client.report_post(self.id)
