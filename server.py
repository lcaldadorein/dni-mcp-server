"""
MCP Server – kyoe-consultas
Transporte: stdio

Uso:
    Este fichero está preparado para registrarse como MCP Server
    en Cloudera Agent Studio mediante uvx.

Herramientas:
    - consultar_comisarias
    - consultar_cita_dnie
"""

import httpx
from fastmcp import FastMCP
raise RuntimeError("ESTO_VIENE_REAL")
# ──────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────

BASE_URL = "http://rag.kyoe.es"
TIMEOUT = 15.0

mcp = FastMCP(
    name="kyoe-consultas",
    instructions=(
        "Herramientas para consultar comisarías disponibles y citas de "
        "DNI/NIE/pasaporte a través de los servicios de rag.kyoe.es."
    ),
)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _error(code: str, message: str) -> dict:
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
        },
    }


# ──────────────────────────────────────────────
# Tools MCP
# ──────────────────────────────────────────────

@mcp.tool()
async def consultar_comisarias(
    codigo_peticion: str,
    id_provincia: int,
    id_localidad: int,
) -> dict:
    """
    Devuelve las comisarías disponibles para tramitar DNI/NIE/pasaporte
    en una provincia y localidad concretas.

    Args:
        codigo_peticion: Identificador de la petición.
        id_provincia: Código numérico de provincia.
        id_localidad: Código numérico de localidad.

    Returns:
        Diccionario con el resultado de la consulta.
    """

    params = {
        "codigoPeticion": codigo_peticion,
        "idProvincia": id_provincia,
        "idLocalidad": id_localidad,
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/ConsultarComisarias",
                params=params,
            )
            response.raise_for_status()

    except httpx.TimeoutException:
        return _error(
            "TIMEOUT",
            "El servicio no respondió a tiempo.",
        )

    except httpx.HTTPStatusError as e:
        return _error(
            "HTTP_ERROR",
            f"El servicio devolvió HTTP {e.response.status_code}.",
        )

    except httpx.RequestError as e:
        return _error(
            "CONNECTION_ERROR",
            f"No se pudo conectar al servicio: {e}.",
        )

    try:
        raw = response.json()
    except Exception:
        raw = response.text

    return {
        "ok": True,
        "data": {
            "provincia": id_provincia,
            "localidad": id_localidad,
            "comisarias": raw,
        },
    }


@mcp.tool()
async def consultar_cita_dnie(
    codigo_peticion: str,
    tipo_titular: str,
    id_titular: str,
) -> dict:
    """
    Consulta la cita de DNI/NIE/pasaporte asociada a un titular.

    Args:
        codigo_peticion: Identificador de la petición.
        tipo_titular: Tipo de documento: D, N o P.
        id_titular: Número de documento.

    Returns:
        Diccionario con el resultado de la consulta.
    """

    tipo_titular = tipo_titular.upper().strip()

    if tipo_titular not in {"D", "N", "P"}:
        return _error(
            "INVALID_PARAM",
            "tipo_titular debe ser 'D', 'N' o 'P'.",
        )

    params = {
        "codigoPeticion": codigo_peticion,
        "tipotitular": tipo_titular,
        "Idtitular": id_titular,
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/ConsultarCitaDnie",
                params=params,
            )
            response.raise_for_status()

    except httpx.TimeoutException:
        return _error(
            "TIMEOUT",
            "El servicio no respondió a tiempo.",
        )

    except httpx.HTTPStatusError as e:
        return _error(
            "HTTP_ERROR",
            f"El servicio devolvió HTTP {e.response.status_code}.",
        )

    except httpx.RequestError as e:
        return _error(
            "CONNECTION_ERROR",
            f"No se pudo conectar al servicio: {e}.",
        )

    try:
        raw = response.json()
    except Exception:
        raw = response.text

    return {
        "ok": True,
        "data": {
            "tipo_titular": tipo_titular,
            "id_titular": id_titular,
            "cita": raw,
        },
    }


# ──────────────────────────────────────────────
# Entry point para Agent Studio
# ──────────────────────────────────────────────

def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
