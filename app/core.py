"""Local content ledger. No network publishing or implicit paid operations."""
import csv
import json
import math
import os
import sqlite3
import statistics
import subprocess
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = 'IDEA SCRIPTED READY_TO_SHOOT SHOT EDITING READY SCHEDULED PUBLISHED MEASURED WINNER ARCHIVED'.split()
FIELDS = 'hypothesis audience pillar angle hook script format footage_type duration cta motive notes'.split()
COUNTS = 'views reach shares saves comments profile_visits follows dms applications qualified_leads sales'.split()
NUMBERS = COUNTS + ['avg_watch_time', 'completion_rate', 'revenue']
WEIGHTS = dict(share_rate=.25, save_rate=.20, follow_rate=.20, profile_visit_rate=.15, comment_rate=.10, completion_rate=.10)


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect():
    path = Path(os.environ.get('BALI_DB', ROOT / 'data/bali.sqlite3'))
    path.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(path, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    try:
        with c:
            yield c
    finally:
        c.close()


def init():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS experiments (
          seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE,
          hypothesis TEXT NOT NULL, audience TEXT DEFAULT '', pillar TEXT DEFAULT '',
          angle TEXT DEFAULT '', hook TEXT DEFAULT '', script TEXT DEFAULT '',
          format TEXT DEFAULT 'talking head + archive', footage_type TEXT DEFAULT 'A-roll + B-roll',
          duration INTEGER DEFAULT 30, cta TEXT DEFAULT 'Напиши БАЛИ', motive TEXT DEFAULT '',
          notes TEXT DEFAULT '', parent_id TEXT REFERENCES experiments(id),
          status TEXT DEFAULT 'IDEA', created_at TEXT, updated_at TEXT);
        CREATE TABLE IF NOT EXISTS artifacts (
          id TEXT PRIMARY KEY, experiment_id TEXT REFERENCES experiments(id), kind TEXT, body TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS variants (
          id TEXT PRIMARY KEY, experiment_id TEXT REFERENCES experiments(id), variant_type TEXT,
          hook TEXT, first_frame TEXT, edit_style TEXT, duration INTEGER, cta TEXT,
          file_path TEXT DEFAULT '', status TEXT DEFAULT 'PLANNED');
        CREATE TABLE IF NOT EXISTS publications (
          id TEXT PRIMARY KEY, variant_id TEXT REFERENCES variants(id), platform TEXT DEFAULT 'instagram',
          trial INTEGER DEFAULT 1, published_at TEXT, external_id TEXT, status TEXT DEFAULT 'PENDING', approved_at TEXT);
        CREATE TABLE IF NOT EXISTS metrics (
          publication_id TEXT REFERENCES publications(id), collected_at TEXT,
          views INTEGER DEFAULT 0, reach INTEGER DEFAULT 0, avg_watch_time REAL DEFAULT 0,
          completion_rate REAL DEFAULT 0, shares INTEGER DEFAULT 0, saves INTEGER DEFAULT 0,
          comments INTEGER DEFAULT 0, profile_visits INTEGER DEFAULT 0, follows INTEGER DEFAULT 0,
          dms INTEGER DEFAULT 0, applications INTEGER DEFAULT 0, qualified_leads INTEGER DEFAULT 0,
          sales INTEGER DEFAULT 0, revenue REAL DEFAULT 0, PRIMARY KEY(publication_id,collected_at));
        CREATE TABLE IF NOT EXISTS learnings (
          id TEXT PRIMARY KEY, experiment_id TEXT REFERENCES experiments(id), category TEXT,
          learning TEXT, confidence REAL, created_at TEXT);
        CREATE TABLE IF NOT EXISTS footage (
          path TEXT PRIMARY KEY, duration REAL, resolution TEXT, created_at TEXT,
          tags TEXT DEFAULT '', location TEXT DEFAULT '', people TEXT DEFAULT '', scene TEXT DEFAULT '',
          usable_as TEXT DEFAULT '', notes TEXT DEFAULT '');
        ''')


def create(c, values):
    if not values.get('hypothesis', '').strip():
        raise ValueError('Нужна hypothesis')
    values = {k: v for k, v in values.items() if k in FIELDS + ['parent_id'] and v != ''}
    duration = int(values.get('duration', 30))
    if duration not in (15, 30, 45, 60):
        raise ValueError('duration: 15, 30, 45 или 60')
    values.update(duration=duration, created_at=now(), updated_at=now())
    keys = list(values)
    cur = c.execute(f"INSERT INTO experiments ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", list(values.values()))
    eid = f'BALI-{cur.lastrowid:04d}'
    c.execute('UPDATE experiments SET id=? WHERE seq=?', (eid, cur.lastrowid))
    return eid


def get(c, eid):
    row = c.execute('SELECT * FROM experiments WHERE id=?', (eid,)).fetchone()
    if not row:
        raise ValueError(f'Не найден {eid}')
    return dict(row)


def transition(c, eid, target):
    old = get(c, eid)['status']
    if target not in STATUSES or (target != 'ARCHIVED' and STATUSES.index(target) != STATUSES.index(old) + 1):
        raise ValueError(f'Недопустимый переход {old} → {target}')
    c.execute('UPDATE experiments SET status=?, updated_at=? WHERE id=?', (target, now(), eid))


def import_experiments(path, dry_run=False):
    rows = list(csv.DictReader(Path(path).open(encoding='utf-8-sig', newline='')))
    with connect() as c:
        result = []
        for row in rows:
            if row.get('id') and c.execute('SELECT 1 FROM experiments WHERE id=?', (row['id'],)).fetchone():
                continue
            eid = create(c, row)
            if row.get('id') and row['id'] != eid:
                raise ValueError('Seed IDs не совпадают с последовательностью; импорт отменён')
            result.append(eid)
        if dry_run:
            c.rollback()
        return result


def artifact(c, eid, kind, body):
    aid = uuid.uuid4().hex
    c.execute('INSERT INTO artifacts VALUES (?,?,?,?,?)', (aid, eid, kind, json.dumps(body, ensure_ascii=False), now()))
    return body


def import_metrics(path, dry_run=False):
    rows = list(csv.DictReader(Path(path).open(encoding='utf-8-sig', newline='')))
    with connect() as c:
        for row in rows:
            pub = c.execute('SELECT * FROM publications WHERE id=? AND status=?', (row['publication_id'], 'PUBLISHED')).fetchone()
            if not pub:
                raise ValueError('Метрики требуют зарегистрированную опубликованную запись')
            datetime.fromisoformat(row['collected_at'].replace('Z', '+00:00'))
            values = {n: float(row.get(n) or 0) for n in NUMBERS}
            if any(not math.isfinite(v) or v < 0 for v in values.values()):
                raise ValueError('Метрики должны быть конечными и неотрицательными')
            if values['completion_rate'] > 1 or any(values[n] != int(values[n]) for n in COUNTS):
                raise ValueError('completion_rate: 0..1; счётчики: целые числа')
            keys = ['publication_id', 'collected_at'] + NUMBERS
            c.execute(f"INSERT INTO metrics ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)}) ON CONFLICT(publication_id,collected_at) DO UPDATE SET " + ','.join(f'{k}=excluded.{k}' for k in NUMBERS), [row['publication_id'], row['collected_at']] + [values[k] for k in NUMBERS])
            c.execute("UPDATE experiments SET status='MEASURED',updated_at=? WHERE id=(SELECT experiment_id FROM variants WHERE id=?) AND status='PUBLISHED'", (now(), pub['variant_id']))
        if dry_run:
            c.rollback()
    return len(rows)


def scores(c):
    # Latest cumulative snapshot per publication, never sum repeated observations.
    rows = c.execute('''SELECT e.id,e.hook,e.pillar,e.motive,e.cta,e.format,m.* FROM metrics m
      JOIN publications p ON p.id=m.publication_id JOIN variants v ON v.id=p.variant_id
      JOIN experiments e ON e.id=v.experiment_id
      WHERE m.collected_at=(SELECT m2.collected_at FROM metrics m2 WHERE m2.publication_id=m.publication_id
      ORDER BY julianday(m2.collected_at) DESC, m2.rowid DESC LIMIT 1)''').fetchall()
    grouped = {}
    for row in rows:
        r = dict(row)
        item = grouped.setdefault(r['id'], {k: r[k] for k in ['id', 'hook', 'pillar', 'motive', 'cta', 'format']} | {k: 0 for k in NUMBERS} | {'completion_weighted': 0})
        for k in NUMBERS:
            item[k] += r[k]
        item['completion_weighted'] += r['completion_rate'] * r['views']
    for r in grouped.values():
        for name, field in [('share_rate','shares'), ('save_rate','saves'), ('comment_rate','comments'), ('follow_rate','follows'), ('profile_visit_rate','profile_visits'), ('lead_rate','applications'), ('qualified_lead_rate','qualified_leads')]:
            r[name] = r[field] / r['reach'] if r['reach'] else 0
        r['completion_rate'] = r['completion_weighted'] / r['views'] if r['views'] else 0
        r['lead_score'] = r['qualified_lead_rate'] * 10000
        r['revenue_per_10k_reach'] = r['revenue'] / r['reach'] * 10000 if r['reach'] else 0
    eligible = [r for r in grouped.values() if r['reach'] > 0]
    medians = {k: statistics.median(r[k] for r in eligible) if eligible else 0 for k in WEIGHTS}
    for r in grouped.values():
        # Zero median has no usable baseline; neutral for zero, capped 2x for positive.
        r['score'] = round(100 * sum(w * (min(r[k] / medians[k], 3) if medians[k] else (2 if r[k] > 0 else 1)) for k, w in WEIGHTS.items()), 2) if r['reach'] else 0
        r['winner'] = r['reach'] >= 1000 and r['score'] >= 120 and len(eligible) >= 3
    return sorted(grouped.values(), key=lambda r: (r['winner'], r['score']), reverse=True)


def evolve(c, eid):
    if not any(r['id'] == eid and r['winner'] for r in scores(c)):
        raise ValueError('Недостаточно данных: evolve доступен подтверждённому winner')
    existing = c.execute('SELECT id FROM experiments WHERE parent_id=? ORDER BY seq', (eid,)).fetchall()
    if existing:
        return [r['id'] for r in existing]
    e = get(c, eid)
    changes = [('hook', h) for h in ['Почему я возвращаюсь именно сейчас?', 'Бали после 11 лет жизни: что осталось со мной', 'Что я первым покажу Насте', 'Мой маршрут начинается не с пляжа', 'Кому подойдёт наша маленькая компания?']] + [('angle', a) for a in ['Один день глазами Насти', 'Личный опыт вместо списка достопримечательностей', 'Как выбрать свою компанию']] + [('duration', 15), ('cta', 'Хочу программу')]
    ids = []
    for rank, (key, value) in enumerate(changes, 1):
        values = {k: e[k] for k in FIELDS}
        values.update(parent_id=eid, notes=f'Rank {rank}; проверить изменение {key}; first frames: лицо / карта; CTA: БАЛИ / Хочу программу; durations: 15 / 30')
        values[key] = value
        values['script'] = ''
        ids.append(create(c, values))
    return ids


def today(c):
    rows = [dict(r) for r in c.execute('SELECT id,status,hypothesis FROM experiments ORDER BY seq')]
    select = lambda states: [r for r in rows if r['status'] in states][:10]
    return {'Снять': select(['READY_TO_SHOOT', 'SCRIPTED']), 'Смонтировать': select(['SHOT','EDITING']), 'Готово к публикации': select(['READY','SCHEDULED']), 'Собрать метрики': select(['PUBLISHED']), 'Развить winners': [r['id'] for r in scores(c) if r['winner']], 'Главное действие': 'Снять один подготовленный сценарий' if select(['READY_TO_SHOOT','SCRIPTED']) else 'Подготовить первый сценарий'}


def index_footage(c, folder):
    result = []
    for p in Path(folder).resolve().rglob('*'):
        if p.suffix.lower() not in ('.mp4','.mov','.m4v','.webm'):
            continue
        meta = json.loads(subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)], check=True, capture_output=True, text=True).stdout)
        video = next(s for s in meta['streams'] if s['codec_type'] == 'video')
        c.execute('INSERT INTO footage(path,duration,resolution,created_at) VALUES(?,?,?,?) ON CONFLICT(path) DO UPDATE SET duration=excluded.duration,resolution=excluded.resolution', (str(p), float(meta['format'].get('duration',0)), f"{video['width']}x{video['height']}", meta['format'].get('tags',{}).get('creation_time')))
        result.append(str(p))
    return result
