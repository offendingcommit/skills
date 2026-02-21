#!/usr/bin/env python3
"""Omie ERP API Client."""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

APP_KEY = os.environ.get("OMIE_APP_KEY", "")
APP_SECRET = os.environ.get("OMIE_APP_SECRET", "")
BASE_URL = "https://app.omie.com.br/api/v1"


def api_call(endpoint: str, call: str, params: list) -> dict:
    """Make an Omie API call."""
    payload = json.dumps({
        "call": call,
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "param": params
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/{endpoint}/",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "detail": body}
    except Exception as e:
        return {"error": str(e)}


# ── Clientes ──────────────────────────────────────────────

def clientes_listar(pagina=1, por_pagina=20):
    data = api_call("geral/clientes", "ListarClientesResumido", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def clientes_buscar(filtro: dict):
    params = {"pagina": 1, "registros_por_pagina": 50}
    if "cnpj_cpf" in filtro:
        params["clientesFiltro"] = {"cnpj_cpf": filtro["cnpj_cpf"]}
    if "codigo" in filtro:
        params["clientesFiltro"] = {"codigo_cliente_omie": int(filtro["codigo"])}
    if "nome" in filtro:
        params["clientesFiltro"] = {"nome_fantasia": filtro["nome"]}
    data = api_call("geral/clientes", "ListarClientesResumido", [params])
    return data


def clientes_detalhar(codigo: int):
    data = api_call("geral/clientes", "ConsultarCliente", [
        {"codigo_cliente_omie": codigo}
    ])
    return data


# ── Produtos ──────────────────────────────────────────────

def produtos_listar(pagina=1, por_pagina=20):
    data = api_call("geral/produtos", "ListarProdutosResumido", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def produtos_detalhar(codigo: int):
    data = api_call("geral/produtos", "ConsultarProduto", [
        {"codigo_produto": codigo}
    ])
    return data


# ── Pedidos de Venda ──────────────────────────────────────

def pedidos_listar(pagina=1, por_pagina=20):
    data = api_call("produtos/pedido", "ListarPedidos", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def pedidos_detalhar(numero: int):
    data = api_call("produtos/pedido", "ConsultarPedido", [
        {"numero_pedido": numero}
    ])
    return data


def pedidos_status(numero: int):
    data = api_call("produtos/pedido", "StatusPedido", [
        {"numero_pedido": numero}
    ])
    return data


# ── Financeiro ────────────────────────────────────────────

def contas_receber(pagina=1, por_pagina=20):
    data = api_call("financas/contareceber", "ListarContasReceber", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def contas_pagar(pagina=1, por_pagina=20):
    data = api_call("financas/contapagar", "ListarContasPagar", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def resumo_financeiro():
    """Get summary of receivables and payables."""
    rec = api_call("financas/contareceber", "ListarContasReceber", [
        {"pagina": 1, "registros_por_pagina": 1}
    ])
    pag = api_call("financas/contapagar", "ListarContasPagar", [
        {"pagina": 1, "registros_por_pagina": 1}
    ])
    return {
        "contas_a_receber": {"total_registros": rec.get("total_de_registros", 0)},
        "contas_a_pagar": {"total_registros": pag.get("total_de_registros", 0)},
    }


# ── Notas Fiscais ─────────────────────────────────────────

def nfe_listar(pagina=1, por_pagina=20):
    data = api_call("produtos/nfconsultar", "ListarNF", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def nfe_detalhar(numero: int):
    data = api_call("produtos/nfconsultar", "ConsultarNF", [
        {"nNumeroNF": numero}
    ])
    return data


# ── Estoque ───────────────────────────────────────────────

def estoque_posicao(pagina=1, por_pagina=20):
    data = api_call("estoque/consulta", "ListarPosEstoque", [
        {"nPagina": pagina, "nRegPorPagina": por_pagina}
    ])
    return data


def estoque_produto(codigo: int):
    data = api_call("estoque/consulta", "PosicaoEstoque", [
        {"nCodProd": codigo}
    ])
    return data


# ── CLI ───────────────────────────────────────────────────

COMMANDS = {
    "clientes_listar": lambda args: clientes_listar(
        int(args[0]) if len(args) > 0 else 1,
        int(args[1]) if len(args) > 1 else 20
    ),
    "clientes_buscar": lambda args: clientes_buscar(
        dict(a.split("=", 1) for a in args)
    ),
    "clientes_detalhar": lambda args: clientes_detalhar(
        int(dict(a.split("=", 1) for a in args)["codigo"])
    ),
    "produtos_listar": lambda args: produtos_listar(
        int(args[0]) if len(args) > 0 else 1,
        int(args[1]) if len(args) > 1 else 20
    ),
    "produtos_detalhar": lambda args: produtos_detalhar(
        int(dict(a.split("=", 1) for a in args)["codigo"])
    ),
    "pedidos_listar": lambda args: pedidos_listar(
        int(args[0]) if len(args) > 0 else 1,
        int(args[1]) if len(args) > 1 else 20
    ),
    "pedidos_detalhar": lambda args: pedidos_detalhar(
        int(dict(a.split("=", 1) for a in args)["numero"])
    ),
    "pedidos_status": lambda args: pedidos_status(
        int(dict(a.split("=", 1) for a in args)["numero"])
    ),
    "contas_receber": lambda args: contas_receber(
        int(args[0]) if len(args) > 0 else 1,
        int(args[1]) if len(args) > 1 else 20
    ),
    "contas_pagar": lambda args: contas_pagar(
        int(args[0]) if len(args) > 0 else 1,
        int(args[1]) if len(args) > 1 else 20
    ),
    "resumo_financeiro": lambda args: resumo_financeiro(),
    "nfe_listar": lambda args: nfe_listar(
        int(args[0]) if len(args) > 0 else 1,
        int(args[1]) if len(args) > 1 else 20
    ),
    "nfe_detalhar": lambda args: nfe_detalhar(
        int(dict(a.split("=", 1) for a in args)["numero"])
    ),
    "estoque_posicao": lambda args: estoque_posicao(
        int(args[0]) if len(args) > 0 else 1,
        int(args[1]) if len(args) > 1 else 20
    ),
    "estoque_produto": lambda args: estoque_produto(
        int(dict(a.split("=", 1) for a in args)["codigo"])
    ),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print("Omie ERP Client")
        print(f"\nComandos: {', '.join(sorted(COMMANDS.keys()))}")
        print("\nExemplos:")
        print("  python3 omie_client.py clientes_listar 1 10")
        print("  python3 omie_client.py clientes_buscar cnpj_cpf=29.451.427/0001-98")
        print("  python3 omie_client.py pedidos_listar")
        print("  python3 omie_client.py resumo_financeiro")
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd not in COMMANDS:
        print(json.dumps({"error": f"Unknown command: {cmd}", "available": sorted(COMMANDS.keys())}, ensure_ascii=False, indent=2))
        sys.exit(1)

    result = COMMANDS[cmd](args)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
