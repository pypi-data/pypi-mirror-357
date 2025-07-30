from abc import ABC
from typing import BinaryIO
from pypix_api.auth.oauth2 import OAuth2Client
from pypix_api.banks.cobv_methods import CobVMethods


class BankPixAPIBase(CobVMethods, ABC):
    """Classe base abstrata para clientes Pix de bancos."""

    BASE_URL = None
    TOKEN_URL = None
    SCOPES = None

    def __init__(
        self,
        client_id: str | None = None,
        cert: str | None = None,
        pvk: str | None = None,
        cert_pfx: str | bytes | BinaryIO | None = None,
        pwd_pfx: str | None = None,
        sandbox_mode: bool = False,
    ) -> None:
        if not self.BASE_URL or not self.TOKEN_URL or not self.SCOPES:
            raise ValueError(
                'BASE_URL, TOKEN_URL e SCOPES devem ser definidos na subclasse.'
            )
        self.sandbox_mode = sandbox_mode
        self.client_id = client_id

        self.oauth = OAuth2Client(
            token_url=self.TOKEN_URL,
            client_id=client_id,
            cert=cert,
            pvk=pvk,
            cert_pfx=cert_pfx,
            pwd_pfx=pwd_pfx,
            sandbox_mode=sandbox_mode,
        )
        self.session = self.oauth.session

    def _create_headers(self) -> dict[str, str]:
        """
        Cria os headers necessários para as requisições.
        """
        token = self.oauth.get_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'client_id': self.client_id or '',
        }
