# socialgal.py

An async API wrapper for [SocialGal](https://social.gal) written in Python.

## Example

```py
from asyncio import run  # anyio/trio also work

from socialgal import Client

async def main() -> None:
    async with Client(
        token="your_token",
        session="your_session_token",
    ) as client:
        print(await client.get_posts())

run(main())
```

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
