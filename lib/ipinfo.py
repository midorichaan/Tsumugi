import aiohttp
import json
from typing import (
    Any,
    ClassVar,
    Dict,
    Union,
)
from urllib.parse import quote as _uriquote

#json_or_text
async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return json.loads(text)
    except KeyError:
        pass
    return text

class Route:
    BASE: ClassVar[str] = "https://ipinfo.io"

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        self.path: str = path
        self.method: str = method
        self.url = self.BASE + self.path
        if parameters:
            self.url = self.url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

class APIClient(object):

    def __init__(
        self, bot=None, token: str=None, *, url: str=None, session: aiohttp.ClientSession=None, loop=None
    ) -> None:
        if not session:
            session = bot.session
        if not loop:
            loop = bot.loop

        self.bot = bot
        self._session: aiohttp.ClientSession = session
        self._loop = loop
        self.token = token
        self.url = url

    #request
    async def request(self, route: Route, **kwargs: Any) -> Any:
        method = route.method
        url = route.url

        headers: Dict[str, str] = {
            "User-Agent": "Midori-APIClient v1 ()"
        }

        try:
            async with self._session.request(method, url, **kwargs) as response:
                data = await json_or_text(response)

                if response.status == 200:
                    return data
                elif response.status == 403:
                    raise Forbidden(response, data)
                elif response.status == 404:
                    raise NotFound(response, data)
                elif response.status >= 500:
                    raise APIServerError(response, data)
                else:
                    raise HTTPException(response, data)
        except OSError as e:
            raise e

    #get_info
    #async def get_info(self, ipaddr: str) -> Dict:
    #    route = Route("GET", f"/{ipaddr}", token=self.token)
    #    request = await self.request(route)
    #    return Info(request)

    #get_data
    async def get_data(self, ipaddr: str) -> Dict:
        route = Route("GET", f"/{ipaddr}", token=self.token)
        request = await self.request(route)
        return request

class Info:

    def __init__(self, data: dict) -> None:
        self._set_raw_data(data)
        self._update_data(data)

    @property
    def __raw_data(self) -> None:
        return self.__raw_data

    @__raw_data.setter
    def _set_raw_data(self, data) -> None:
        self.__raw_data = data

    def _update_data(self, data):
        self.ip: str = data["ip"]
        self.hostname: str = data["hostname"]
        self.anycast: bool = data.get("anycast", False)
        self.city: str = data.get("city", None)
        self.region: str = data.get("region", None)
        self.country: str = data.get("country", None)
        self.location: str = data.get("loc", None)
        self.postal: int = data.get("postal", None)
        self.timezone: str = data.get("timezone", None)

        self.asn: ASN = ASN(data.get("asn"))
        self.company: Company = Company(data.get("company"))
        self.privacy: Privacy = Privacy(data.get("privacy"))
        self.abuse: Abuse = Abuse(data.get("abuse"))
        self.domains: Domains = Domains(data.get(domains))

class ASN(object):
    def __init__(self, data: dict) -> None:
        self.asn: str = data["asn"]
        self.name: str = data["name"]
        self.domain: str = data["domain"]
        self.route: str = data["route"]
        self.type: str = data["type"]
        self._raw_data: dict = data

class Company(object):
    def __init__(self, data: dict) -> None:
        self.name: str = data["name"]
        self.domain: str = data["domain"]
        self.type: str = data["type"]
        self._raw_data: dict = data

class Privacy(object):
    def __init__(self, data: dict) -> None:
        self.vpn: bool = data["vpn"]
        self.proxy: bool = data["proxy"]
        self.tor: bool = data["tor"]
        self.relay: bool = data["relay"]
        self.hosting: bool = data["hosting"]
        self.service: str = data["service"]
        self._raw_data: dict = data

class Abuse(object):
    def __init__(self, data: dict) -> None:
        self.address: str = data["address"]
        self.country: str = data["country"]
        self.email: str = data["email"]
        self.network: str = data["network"]
        self.phone: str = data["phone"]
        self._raw_data: dict = data

class Domains(object):
    def __init__(self, data: dict) -> None:
        self.ip: str = data["ip"]
        self.total: str = data["total"]
        self.domains: list = data["domains"]
        self._raw_data: dict = data

class ClientException(Exception):
    pass

class HTTPException(ClientException):

    def __init__(self, response, message):
        self.response = response
        self.status: int = response.status

        fmt = "{0.status} {0.reason}: {1}"
        super().__init__(fmt.format(self.response, self.message))

class Forbidden(HTTPException):
    pass

class NotFound(HTTPException):
    pass

class AIPServerError(HTTPException):
    pass
