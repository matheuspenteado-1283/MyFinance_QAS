from flask import request, jsonify, session

from . import bp
from .db import (
    get_all_lcto_emprestimos, add_lcto_emprestimo, update_lcto_emprestimo,
    delete_lcto_emprestimo, get_saldo_emprestimos,
)


@bp.route('/api/lcto_emprestimos', methods=['GET'])
def api_get_lcto_emprestimos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    return jsonify(get_all_lcto_emprestimos(session['user_email']))


@bp.route('/api/lcto_emprestimos', methods=['POST'])
def api_post_lcto_emprestimo():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    d = request.json
    add_lcto_emprestimo(
        session['user_email'], d.get('tipo'), d.get('beneficiario'),
        d.get('valor_operacao'), d.get('moeda_emp', 'BRL'),
        d.get('data_emprestimo'), d.get('data_operacao'),
        d.get('obs'), d.get('status', 'Ativo'),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/lcto_emprestimos/<int:le_id>', methods=['PUT'])
def api_put_lcto_emprestimo(le_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    d = request.json
    update_lcto_emprestimo(
        le_id, d.get('tipo'), d.get('beneficiario'),
        d.get('valor_operacao'), d.get('moeda_emp', 'BRL'),
        d.get('data_emprestimo'), d.get('data_operacao'),
        d.get('obs'), d.get('status', 'Ativo'),
    )
    return jsonify({'status': 'ok'})


@bp.route('/api/lcto_emprestimos/<int:le_id>', methods=['DELETE'])
def api_delete_lcto_emprestimo(le_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    delete_lcto_emprestimo(le_id)
    return jsonify({'status': 'ok'})


@bp.route('/api/lcto_emprestimos/saldo', methods=['GET'])
def api_get_saldo_emprestimos():
    if 'user_email' not in session:
        return jsonify({'error': 'Não logado'}), 401
    return jsonify(get_saldo_emprestimos(session['user_email']))
