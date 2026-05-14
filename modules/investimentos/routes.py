import os
import io
import pandas as pd
from flask import request, jsonify, send_file, session, current_app
from werkzeug.utils import secure_filename

from . import bp
from .db import (
    get_all_lcto_investimentos, add_lcto_investimento, update_lcto_investimento,
    delete_lcto_investimento, clear_lcto_investimentos,
)


@bp.route('/api/lcto_investimentos', methods=['GET'])
def api_get_lcto_investimentos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    return jsonify(get_all_lcto_investimentos(session['user_email']))


@bp.route('/api/lcto_investimentos', methods=['POST'])
def api_post_lcto_investimento():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    d = request.json
    add_lcto_investimento(
        session['user_email'], d.get('banco'), d.get('tp_investimento'),
        d.get('data_inv'), d.get('valor_inv'), d.get('moeda', 'BRL'),
        d.get('qtd'), d.get('taxa'), d.get('valor_atual'),
        d.get('val_mes_ant'), d.get('aporte'),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/lcto_investimentos/<int:li_id>', methods=['PUT'])
def api_put_lcto_investimento(li_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    d = request.json
    update_lcto_investimento(
        li_id, d.get('banco'), d.get('tp_investimento'),
        d.get('data_inv'), d.get('valor_inv'), d.get('moeda', 'BRL'),
        d.get('qtd'), d.get('taxa'), d.get('valor_atual'),
        d.get('val_mes_ant'), d.get('aporte'),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/lcto_investimentos/<int:li_id>', methods=['DELETE'])
def api_delete_lcto_investimento(li_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    delete_lcto_investimento(li_id)
    return jsonify({'status': 'ok'})


@bp.route('/api/upload_lcto_investimentos', methods=['POST'])
def api_upload_lcto_investimentos():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo'}), 400
    file = request.files['file']
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filepath)
    try:
        filename = file.filename.lower()
        df = pd.read_excel(filepath) if filename.endswith(('.xls', '.xlsx')) else pd.read_csv(filepath)
        clear_lcto_investimentos(session['user_email'])
        for _, row in df.iterrows():
            add_lcto_investimento(
                session['user_email'],
                str(row.get('banco', row.get('Banco', ''))),
                str(row.get('tp_investimento', row.get('Tipo Investimento', ''))),
                str(row.get('data_inv', row.get('Data Investimento', ''))),
                float(row.get('valor_inv', row.get('Valor Investimento', 0)) or 0),
                str(row.get('moeda', row.get('Moeda', 'BRL'))),
                float(row.get('qtd', row.get('Quantidade', 0)) or 0),
                float(row.get('taxa', row.get('Taxa', 0)) or 0),
                float(row.get('valor_atual', row.get('Valor Atual', 0)) or 0),
                float(row.get('val_mes_ant', row.get('Valor Mês Anterior', 0)) or 0),
                float(row.get('aporte', row.get('Aporte', 0)) or 0),
            )
        os.remove(filepath)
        return jsonify({'status': 'ok'})
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 400


@bp.route('/api/export_lcto_investimentos', methods=['GET'])
def api_export_lcto_investimentos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    data = get_all_lcto_investimentos(session['user_email'])
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.drop(columns=['id', 'user_email', 'criado_em'], errors='ignore')
        df.rename(columns={
            'banco': 'Banco', 'tp_investimento': 'Tipo Investimento', 'data_inv': 'Data Investimento',
            'valor_inv': 'Valor Investimento', 'moeda': 'Moeda', 'qtd': 'Quantidade', 'taxa': 'Taxa',
            'valor_tot_inv': 'Valor Total Investimento', 'valor_atual': 'Valor Atual',
            'valor_liq_mes': 'Valor Líquido Mês', 'val_mes_ant': 'Valor Mês Anterior',
            'aporte': 'Aporte', 'lucro_op': 'Lucro Operacional', 'lucro_mes': 'Lucro Mês',
            'pct_rent': '% Rentabilidade',
        }, inplace=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Investimentos')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='Lancamentos_Investimentos.xlsx')
