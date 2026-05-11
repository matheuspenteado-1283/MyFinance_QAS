from db.connection import get_connection


def init_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS despesas_mensais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            data TEXT,
            descricao TEXT,
            valor_original REAL,
            moeda TEXT,
            cambio_eur REAL,
            valor_eur REAL,
            usr1 TEXT,
            usr2 TEXT,
            diferenca_original REAL,
            status_pago TEXT DEFAULT 'Pendente',
            categoria_final TEXT,
            receita INTEGER DEFAULT 0,
            comentarios TEXT,
            conta_bancaria TEXT,
            mes_referencia TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS despesas_anuais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            ano INTEGER,
            categoria_final TEXT,
            total_usr1 REAL DEFAULT 0,
            total_usr2 REAL DEFAULT 0,
            total_geral REAL DEFAULT 0,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def get_despesas_mensais(user_email, mes=None):
    conn = get_connection()
    if mes:
        rows = conn.execute(
            'SELECT * FROM despesas_mensais WHERE user_email=? AND mes_referencia=? ORDER BY data, id',
            (user_email, mes),
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM despesas_mensais WHERE user_email=? ORDER BY mes_referencia DESC, data, id',
            (user_email,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_despesas_mensais_batch(user_email, rows_list):
    if not rows_list:
        return 0
    mes = rows_list[0].get('mes_referencia', '')
    conn = get_connection()
    for r in rows_list:
        conn.execute('''
            INSERT INTO despesas_mensais
            (user_email, data, descricao, valor_original, moeda, cambio_eur, valor_eur,
             usr1, usr2, diferenca_original, status_pago, categoria_final, receita,
             comentarios, conta_bancaria, mes_referencia)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            user_email,
            r.get('data'), r.get('descricao'), r.get('valor_original'),
            r.get('moeda'), r.get('cambio_eur'), r.get('valor_eur'),
            r.get('usr1', 0), r.get('usr2', 0), r.get('diferenca_original'),
            r.get('status_pago', 'Pendente'), r.get('categoria_final'),
            1 if r.get('receita') else 0,
            r.get('comentarios'), r.get('conta_bancaria'), mes,
        ))
    conn.commit()
    conn.close()
    return len(rows_list)


def add_despesa_mensal(user_email, row):
    conn = get_connection()
    conn.execute('''
        INSERT INTO despesas_mensais
        (user_email, data, descricao, valor_original, moeda, cambio_eur, valor_eur,
         usr1, usr2, diferenca_original, status_pago, categoria_final, receita,
         comentarios, conta_bancaria, mes_referencia)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        user_email,
        row.get('data'), row.get('descricao'), row.get('valor_original'),
        row.get('moeda'), row.get('cambio_eur'), row.get('valor_eur'),
        row.get('usr1', 0), row.get('usr2', 0), row.get('diferenca_original'),
        row.get('status_pago', 'Pendente'), row.get('categoria_final'),
        1 if row.get('receita') else 0,
        row.get('comentarios'), row.get('conta_bancaria'), row.get('mes_referencia'),
    ))
    conn.commit()
    conn.close()


def update_despesa_mensal(d_id, row):
    conn = get_connection()
    conn.execute('''
        UPDATE despesas_mensais SET
        data=?, descricao=?, valor_original=?, moeda=?, cambio_eur=?, valor_eur=?,
        usr1=?, usr2=?, diferenca_original=?, status_pago=?, categoria_final=?,
        receita=?, comentarios=?, conta_bancaria=?, mes_referencia=?
        WHERE id=?
    ''', (
        row.get('data'), row.get('descricao'), row.get('valor_original'),
        row.get('moeda'), row.get('cambio_eur'), row.get('valor_eur'),
        row.get('usr1', 0), row.get('usr2', 0), row.get('diferenca_original'),
        row.get('status_pago', 'Pendente'), row.get('categoria_final'),
        1 if row.get('receita') else 0,
        row.get('comentarios'), row.get('conta_bancaria'), row.get('mes_referencia'),
        d_id,
    ))
    conn.commit()
    conn.close()


def delete_despesa_mensal(d_id):
    conn = get_connection()
    conn.execute('DELETE FROM despesas_mensais WHERE id=?', (d_id,))
    conn.commit()
    conn.close()


def delete_despesas_mensais_batch(ids):
    if not ids:
        return
    conn = get_connection()
    conn.execute('DELETE FROM despesas_mensais WHERE id IN ({})'.format(','.join('?' * len(ids))), ids)
    conn.commit()
    conn.close()


def clear_despesas_mensais(user_email, mes=None):
    conn = get_connection()
    if mes:
        conn.execute('DELETE FROM despesas_mensais WHERE user_email=? AND mes_referencia=?', (user_email, mes))
    else:
        conn.execute('DELETE FROM despesas_mensais WHERE user_email=?', (user_email,))
    conn.commit()
    conn.close()


def consolidar_despesas_anuais(user_email, ano):
    conn = get_connection()
    rows = conn.execute('''
        SELECT categoria_final, SUM(usr1) as total_usr1, SUM(usr2) as total_usr2,
               SUM(usr1)+SUM(usr2) as total_geral
        FROM despesas_mensais
        WHERE user_email=? AND substr(mes_referencia,1,4)=?
        GROUP BY categoria_final
    ''', (user_email, str(ano))).fetchall()
    conn.execute('DELETE FROM despesas_anuais WHERE user_email=? AND ano=?', (user_email, ano))
    for r in rows:
        conn.execute('''
            INSERT INTO despesas_anuais (user_email, ano, categoria_final, total_usr1, total_usr2, total_geral)
            VALUES (?,?,?,?,?,?)
        ''', (user_email, ano, r['categoria_final'], r['total_usr1'], r['total_usr2'], r['total_geral']))
    conn.commit()
    conn.close()
    return len(rows)


def get_consolidacao_tipo_despesa(user_email, mes_referencia):
    conn = get_connection()
    rows = conn.execute('''
        SELECT
            COALESCE(cd.tipo_despesa, 'Sem Tipo') as tipo_despesa,
            dm.moeda,
            SUM(dm.usr1) as total_usr1,
            SUM(dm.usr2) as total_usr2,
            SUM(dm.usr1) + SUM(dm.usr2) as total_geral
        FROM despesas_mensais dm
        LEFT JOIN cad_despesas cd ON cd.despesa = dm.categoria_final
        WHERE dm.user_email = ? AND dm.mes_referencia = ? AND dm.receita = 0
        GROUP BY cd.tipo_despesa, dm.moeda
        ORDER BY cd.tipo_despesa, dm.moeda
    ''', (user_email, mes_referencia)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_meses_disponiveis(user_email):
    conn = get_connection()
    rows = conn.execute(
        'SELECT DISTINCT mes_referencia FROM despesas_mensais WHERE user_email=? ORDER BY mes_referencia DESC',
        (user_email,),
    ).fetchall()
    conn.close()
    return [r['mes_referencia'] for r in rows]
