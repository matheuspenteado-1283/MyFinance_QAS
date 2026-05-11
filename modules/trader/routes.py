import os
import io
import pandas as pd
from flask import request, jsonify, send_file, session, current_app
from werkzeug.utils import secure_filename

from . import bp
from .db import (
    get_all_trader_positions, add_trader_position, update_trader_position,
    delete_trader_position, clear_trader_positions, get_trader_periodos, get_trader_contas,
)


@bp.route('/api/trader_positions', methods=['GET'])
def api_get_trader_positions():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    periodo = request.args.get('periodo')
    return jsonify(get_all_trader_positions(session['user_email'], periodo))


@bp.route('/api/trader_positions', methods=['POST'])
def api_post_trader_position():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    d = request.json
    add_trader_position(
        session['user_email'], d.get('periodo'), d.get('conta_bancaria'), d.get('symbol'), d.get('type'),
        float(d.get('volume', 0) or 0), d.get('open_time'), float(d.get('open_price', 0) or 0),
        d.get('close_time'), float(d.get('close_price', 0) or 0),
        float(d.get('sl', 0) or 0), float(d.get('tp', 0) or 0), float(d.get('margin', 0) or 0),
        float(d.get('commission', 0) or 0), float(d.get('swap', 0) or 0),
        float(d.get('rollover', 0) or 0), float(d.get('gross_pl', 0) or 0),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/trader_positions/<int:t_id>', methods=['PUT'])
def api_put_trader_position(t_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    d = request.json
    update_trader_position(
        t_id, d.get('periodo'), d.get('conta_bancaria'), d.get('symbol'), d.get('type'),
        float(d.get('volume', 0) or 0), d.get('open_time'), float(d.get('open_price', 0) or 0),
        d.get('close_time'), float(d.get('close_price', 0) or 0),
        float(d.get('sl', 0) or 0), float(d.get('tp', 0) or 0), float(d.get('margin', 0) or 0),
        float(d.get('commission', 0) or 0), float(d.get('swap', 0) or 0),
        float(d.get('rollover', 0) or 0), float(d.get('gross_pl', 0) or 0),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/trader_positions/<int:t_id>', methods=['DELETE'])
def api_delete_trader_position(t_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    delete_trader_position(t_id)
    return jsonify({'status': 'ok'})


@bp.route('/api/trader_positions/clear', methods=['POST'])
def api_clear_trader_positions():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    periodo = (request.json or {}).get('periodo')
    clear_trader_positions(user_email=session['user_email'], periodo=periodo if periodo else None)
    return jsonify({'status': 'ok'})


@bp.route('/api/trader_periodos', methods=['GET'])
def api_get_trader_periodos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    return jsonify(get_trader_periodos(session['user_email']))


@bp.route('/api/trader_contas', methods=['GET'])
def api_get_trader_contas():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    return jsonify(get_trader_contas(session['user_email']))


@bp.route('/api/upload_trader_positions', methods=['POST'])
def api_upload_trader_positions():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo'}), 400
    file = request.files['file']
    conta_bancaria_input = request.form.get('conta_bancaria', '')
    periodo_input = request.form.get('periodo', '')
    if not conta_bancaria_input or not periodo_input:
        return jsonify({'error': 'Conta Bancária e Período são obrigatórios'}), 400
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filepath)
    try:
        filename = file.filename.lower()
        df = pd.read_excel(filepath) if filename.endswith(('.xls', '.xlsx')) else pd.read_csv(filepath)

        header_row_index = -1
        col_str = ' '.join(str(c).lower() for c in df.columns)
        if 'symbol' not in col_str or 'type' not in col_str:
            for i, row in df.iterrows():
                row_str = ' '.join(str(val).lower() for val in row.values)
                if 'symbol' in row_str and 'type' in row_str and 'volume' in row_str:
                    header_row_index = i
                    break
            if header_row_index != -1:
                new_header = df.iloc[header_row_index]
                df = df[header_row_index + 1:]
                df.columns = new_header
                df.reset_index(drop=True, inplace=True)

        df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_').str.replace('/', '_')
        print('Colunas encontradas:', df.columns.tolist())

        count = 0
        for _, row in df.iterrows():
            symbol = str(row.get('symbol', '')).strip() if pd.notna(row.get('symbol')) else ''
            type_ = str(row.get('type', '')).strip().title() if pd.notna(row.get('type')) else 'Buy'
            if type_.lower() in ['buy', 'long', 'b']:
                type_ = 'Buy'
            elif type_.lower() in ['sell', 'short', 's']:
                type_ = 'Sell'

            def safe_float(val, default=0):
                if pd.isna(val) or val == '' or val is None:
                    return default
                try:
                    s = str(val).strip().replace(',', '').replace(' ', '').replace('\xa0', '')
                    if s == '' or s.lower() in ('nan', 'none'):
                        return default
                    return float(s)
                except Exception:
                    return default

            def safe_str(val):
                if pd.isna(val) or val is None:
                    return ''
                return str(val).strip()

            def get_any(keys, default=None):
                for k in keys:
                    if k in row and pd.notna(row[k]):
                        return row[k]
                return default

            add_trader_position(
                session['user_email'], periodo_input, conta_bancaria_input,
                symbol, type_,
                safe_float(get_any(['volume'])),
                safe_str(get_any(['open_time', 'time'])),
                safe_float(get_any(['open_price', 'price'])),
                safe_str(get_any(['close_time'])),
                safe_float(get_any(['close_price'])),
                safe_float(get_any(['sl', 's___l', 's__l', 's_l'])),
                safe_float(get_any(['tp', 't___p', 't__p', 't_p'])),
                safe_float(get_any(['margin'])),
                safe_float(get_any(['commission', 'comm.', 'comm'])),
                safe_float(get_any(['swap'])),
                safe_float(get_any(['rollover'])),
                safe_float(get_any(['gross_pl', 'gross_p_l'])),
            )
            count += 1
        os.remove(filepath)
        return jsonify({'status': 'ok', 'count': count})
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


@bp.route('/api/export_trader_positions', methods=['GET'])
def api_export_trader_positions():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    periodo = request.args.get('periodo')
    data = get_all_trader_positions(session['user_email'], periodo)
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.drop(columns=['id', 'user_email', 'criado_em'], errors='ignore')
        df.rename(columns={
            'periodo': 'Período', 'conta_bancaria': 'Conta Bancária', 'symbol': 'Symbol',
            'type': 'Type', 'volume': 'Volume', 'open_time': 'Open Time', 'open_price': 'Open Price',
            'close_time': 'Close Time', 'close_price': 'Close Price', 'sl': 'SL', 'tp': 'TP',
            'margin': 'Margin', 'commission': 'Commission', 'swap': 'Swap', 'rollover': 'Rollover',
            'gross_pl': 'Gross P/L',
        }, inplace=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Trader Positions')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='Trader_Positions.xlsx')
