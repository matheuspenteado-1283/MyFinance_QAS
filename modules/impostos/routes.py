import io
import pandas as pd
from flask import request, jsonify, send_file, session

from . import bp
from .db import (
    get_all_lcto_impostos, add_lcto_imposto, update_lcto_imposto,
    delete_lcto_imposto, get_dashboard_impostos,
)


@bp.route('/api/lcto_impostos', methods=['GET'])
def api_get_lcto_impostos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    return jsonify(get_all_lcto_impostos(session['user_email']))


@bp.route('/api/lcto_impostos', methods=['POST'])
def api_post_lcto_imposto():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    d = request.json
    add_lcto_imposto(
        session['user_email'], d.get('mes_ano'), d.get('tp_imposto'),
        d.get('moeda_faturado'), d.get('valor_faturado'), d.get('valor_imposto'),
        d.get('moeda_pagamento'), d.get('pagamento'), d.get('pagamento_mes_ano'), d.get('desconto_iva'),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/lcto_impostos/<int:li_id>', methods=['PUT'])
def api_put_lcto_imposto(li_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    d = request.json
    update_lcto_imposto(
        li_id, d.get('mes_ano'), d.get('tp_imposto'),
        d.get('moeda_faturado'), d.get('valor_faturado'), d.get('valor_imposto'),
        d.get('moeda_pagamento'), d.get('pagamento'), d.get('pagamento_mes_ano'), d.get('desconto_iva'),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/lcto_impostos/<int:li_id>', methods=['DELETE'])
def api_delete_lcto_imposto(li_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    delete_lcto_imposto(li_id)
    return jsonify({'status': 'ok'})


@bp.route('/api/dashboard_impostos', methods=['GET'])
def api_get_dashboard_impostos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    return jsonify(get_dashboard_impostos(session['user_email']))


@bp.route('/api/export_lcto_impostos', methods=['GET'])
def api_export_lcto_impostos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    data = get_all_lcto_impostos(session['user_email'])
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.drop(columns=['id', 'user_email', 'criado_em'], errors='ignore')
        df['Valor_Liquido'] = df['valor_imposto'] - df['desconto_iva']
        df.rename(columns={
            'mes_ano': 'Mês/Ano', 'tp_imposto': 'Tipo Imposto',
            'moeda_faturado': 'Moeda Faturado', 'valor_faturado': 'Valor Faturado',
            'valor_imposto': 'Valor Imposto', 'moeda_pagamento': 'Moeda Pagamento',
            'pagamento': 'Pagamento', 'pagamento_mes_ano': 'Pagamento Mês/Ano',
            'desconto_iva': 'Desconto IVA',
        }, inplace=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Impostos')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='Lancamentos_Impostos.xlsx')
