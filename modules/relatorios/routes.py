import io
import traceback
import pandas as pd
from flask import request, jsonify, send_file, session

from . import bp
from .db import (
    save_relatorio_dinamico, get_all_relatorios_dinamicos, delete_relatorio_dinamico,
    get_dados_relatorio_dinamico, get_tabelas_campos,
)
from modules.despesas_mensais.db import get_meses_disponiveis


@bp.route('/api/relatorio_dinamico/tabelas', methods=['GET'])
def api_relatorio_dinamico_tabelas():
    return jsonify(get_tabelas_campos())


@bp.route('/api/relatorio_dinamico', methods=['GET'])
def api_get_relatorios_dinamicos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    return jsonify(get_all_relatorios_dinamicos(session['user_email']))


@bp.route('/api/relatorio_dinamico', methods=['POST'])
def api_create_relatorio_dinamico():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    data = request.json or {}
    save_relatorio_dinamico(
        session['user_email'],
        data.get('nome', 'Relatório Sem Nome'),
        data.get('tabelas', []),
        data.get('campos', []),
        data.get('agrupador', ''),
        data.get('mes_inicio', ''),
        data.get('mes_fim', ''),
        data.get('moedas', []),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/relatorio_dinamico/<int:r_id>', methods=['DELETE'])
def api_delete_relatorio_dinamico(r_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    delete_relatorio_dinamico(session['user_email'], r_id)
    return jsonify({'status': 'ok'})


@bp.route('/api/relatorio_dinamico/gerar', methods=['POST'])
def api_gerar_relatorio_dinamico():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    try:
        data = request.json or {}
        tabelas = data.get('tabelas', [])
        if not tabelas:
            return jsonify({'agrupadores': [], 'meses': []})

        resultado = get_dados_relatorio_dinamico(
            session['user_email'],
            tabelas,
            data.get('campos', []),
            data.get('agrupador', ''),
            data.get('mes_inicio', ''),
            data.get('mes_fim', ''),
            data.get('moedas', []),
        )
        return jsonify(resultado)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


@bp.route('/api/relatorio_dinamico/meses', methods=['GET'])
def api_meses_disponiveis_relatorio():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    try:
        meses = get_meses_disponiveis(session['user_email'])
        return jsonify(meses)
    except Exception:
        traceback.print_exc()
        return jsonify([])


@bp.route('/api/relatorio_dinamico/exportar', methods=['POST'])
def api_export_relatorio_dinamico():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    data = request.json or {}
    resultado = get_dados_relatorio_dinamico(
        session['user_email'],
        data.get('tabelas', []),
        data.get('campos', []),
        data.get('agrupador', ''),
        data.get('mes_inicio', ''),
        data.get('mes_fim', ''),
        data.get('moedas', []),
    )

    linhas = []
    meses = resultado.get('meses', [])
    moedas = data.get('moedas', ['EUR'])

    for agr in resultado.get('agrupadores', []):
        nome = agr.get('nome', '')
        dados = agr.get('dados', {})
        valores = agr.get('valores', {})

        for mes in meses:
            vals_mes = valores.get(mes, {})
            linha = {'Agrupador': nome, 'Mês': mes}
            linha.update(dados)
            for moeda in moedas:
                linha[f'{moeda}'] = vals_mes.get(moeda, 0)
            linhas.append(linha)

    df = pd.DataFrame(linhas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatorio')
    output.seek(0)

    nome_arquivo = data.get('nome', 'Relatorio_Dinamico').replace(' ', '_') + '.xlsx'
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=nome_arquivo)
