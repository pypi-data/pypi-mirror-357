## TODOs
https://keepachangelog.com/en/1.0.0/

- country codes: use https://docs.pydantic.dev/latest/api/pydantic_extra_types_country/#pydantic_extra_types.country.CountryAlpha2
    - would require additional dependency...

uv run mcp-server-ipinfo

uv run --with jupyter jupyter lab

uvx --with 'mcp[cli]' mcp


```py
class AsnDetails(BaseModel):
    asn: constr(pattern=r"^AS\d+$") | None = None
    name: str | None = None
    domain: HttpUrl | None = None
    route: IPvAnyNetwork | None = None
    org_type: str | None = None
```


env IPINFO_API_TOKEN=80bfeb40cc2821 uvx mcp-server-ipinfo mcp-server-ipinfo
