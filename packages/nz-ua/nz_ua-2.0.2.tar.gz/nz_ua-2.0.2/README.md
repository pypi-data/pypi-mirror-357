<div align="center">
  <table>
    <tr>
      <td>
        <div align="center">
          <img src="https://emojicdn.elk.sh/⚠️" width="80" height="80" align="left"/>
          <h3>The library is not supported</h3>
          <p>Since I don't use nz.ua anymore and I don't need it</p>
        </div>
      </td>
    </tr>
  </table>
</div>

[![PyPI](https://img.shields.io/pypi/v/nz-ua?style=for-the-badge)](https://pypi.org/project/nz-ua/)

Library for working with the nz.ua service.

# Requirements

* Python 3.10+
* [Aiohttp](https://github.com/aio-libs/aiohttp) for making requests to nz.ua api.
* [Pydantic](https://github.com/pydantic/pydantic) for data validation.

# Installing

```bash
pip install nz-ua
```
Or use the version from github:
```bash
pip install git+https://github.com/MrPandir/nz-ua
```

# Quick usage

```python
import nz
import asyncio

USER_NAME = "your username"
PASSWORD = "your password"


async def main():
    async with nz.Client() as client:
        await client.login(USER_NAME, PASSWORD)
        schedule = await client.get_schedule()
        print(schedule.dict())


if __name__ == "__main__":
    asyncio.run(main())

```

# Links
- Not official API documentations: [Artemka1806/api-mobile.nz.ua](https://github.com/Artemka1806/api-mobile.nz.ua), [FussuChalice/NZ.UA-API-unofficial](https://github.com/FussuChalice/NZ.UA-API-unofficial)
- Similar project: [xXxCLOTIxXx/nz-ua.py](https://github.com/xXxCLOTIxXx/nz-ua.py)
