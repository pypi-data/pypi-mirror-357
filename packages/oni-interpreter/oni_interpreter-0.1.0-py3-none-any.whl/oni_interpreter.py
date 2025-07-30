import sys
import os
import argparse

VERSION = "0.1.0"

def interpretar(codigo):
    linhas = codigo.split("\n")
    variaveis = {}
    funcoes = {}
    i = 0

    def avaliar_expr(expr):
        try:
            for v in variaveis:
                expr = expr.replace(v, str(variaveis[v]))
            return eval(expr)
        except Exception:
            return expr.strip('"').strip("'")

    while i < len(linhas):
        linha = linhas[i].strip()
        if linha == "" or linha.startswith("#"):
            i += 1
            continue

        if linha.startswith("diga "):
            conteudo = linha[5:].strip()
            if conteudo.startswith('"') or conteudo.startswith("'"):
                print(conteudo.strip('"').strip("'"))
            else:
                print(variaveis.get(conteudo, f"[variável '{conteudo}' não definida]"))

        elif linha.startswith("var "):
            partes = linha[4:].split("=", 1)
            if len(partes) == 2:
                nome = partes[0].strip()
                valor = avaliar_expr(partes[1].strip())
                variaveis[nome] = valor
            else:
                print(f"Erro sintaxe na linha {i+1}: {linha}")

        elif linha.startswith("mostre "):
            nome = linha[7:].strip()
            if nome in variaveis:
                print(variaveis[nome])
            else:
                print(f"[variável '{nome}' não definida]")

        elif linha.startswith("se "):
            condicao = linha[3:].strip().rstrip(":")
            try:
                condicao_eval = avaliar_expr(condicao)
                if not condicao_eval:
                    while i < len(linhas):
                        i += 1
                        if i >= len(linhas):
                            break
                        if linhas[i].strip().startswith("senao:"):
                            break
            except Exception:
                print(f"Erro na condição na linha {i+1}: {linha}")

        elif linha.startswith("senao:"):
            while i < len(linhas):
                i += 1
                if i >= len(linhas):
                    break
                if not linhas[i].startswith(" "):
                    i -= 1
                    break

        elif linha.startswith("enquanto "):
            condicao = linha[9:].strip().rstrip(":")
            loop_start = i
            try:
                while avaliar_expr(condicao):
                    i = loop_start + 1
                    while i < len(linhas):
                        if linhas[i].strip() == "" or linhas[i].strip().startswith("#"):
                            i += 1
                            continue
                        if not linhas[i].startswith("    "):
                            break
                        interpretar(linhas[i][4:])
                        i += 1
                while i < len(linhas) and linhas[i].startswith("    "):
                    i += 1
                i -= 1
            except Exception as e:
                print(f"Erro no laço enquanto na linha {loop_start+1}: {e}")

        elif linha.startswith("definir "):
            nome_func = linha[8:].split("(")[0].strip()
            blocos = []
            i += 1
            while i < len(linhas):
                if linhas[i].startswith("    "):
                    blocos.append(linhas[i][4:])
                    i += 1
                else:
                    break
            funcoes[nome_func] = blocos
            i -= 1

        elif linha.startswith("chama "):
            nome_func = linha[6:].strip()
            if nome_func in funcoes:
                interpretar("\n".join(funcoes[nome_func]))
            else:
                print(f"[função '{nome_func}' não definida]")

        else:
            print(f"Linha não reconhecida ({i+1}): {linha}")

        i += 1

def main():
    parser = argparse.ArgumentParser(description="Interpretador da linguagem Oni/Uni")
    parser.add_argument("arquivo", nargs="?", help="Arquivo .oni ou .uni para interpretar")
    parser.add_argument("-V", "--version", action="store_true", help="Mostrar versão do interpretador")

    args = parser.parse_args()

    if args.version:
        print(f"Oni Interpreter versão {VERSION}")
        sys.exit(0)

    if not args.arquivo:
        parser.print_help()
        sys.exit(1)

    caminho_arquivo = args.arquivo
    _, ext = os.path.splitext(caminho_arquivo)
    if ext not in [".oni", ".uni"]:
        print("Erro: o arquivo deve ter extensão .oni ou .uni")
        sys.exit(1)

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            codigo = f.read()
        interpretar(codigo)
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        sys.exit(1)

if __name__ == "__main__":
    main()
