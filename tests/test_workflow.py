import csv
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from app import core as d
from app.content import generate, plan
from app.web import app

@pytest.fixture(autouse=True)
def database(tmp_path,monkeypatch):
    monkeypatch.setenv('BALI_DB',str(tmp_path/'test.db')); d.init()

def new():
    with d.connect() as c: return d.create(c,{'hypothesis':'Личный опыт вызывает интерес'})

def test_atomic_ids():
    with ThreadPoolExecutor(max_workers=8) as pool: ids=list(pool.map(lambda _:new(),range(40)))
    assert len(set(ids))==40
    assert 'BALI-0040' in ids

def test_csv_import_repeat_and_dry_run():
    assert len(d.import_experiments(d.ROOT/'experiments/backlog.csv',True))==50
    with d.connect() as c: assert c.execute('select count(*) from experiments').fetchone()[0]==0
    assert len(d.import_experiments(d.ROOT/'experiments/backlog.csv'))==50
    assert d.import_experiments(d.ROOT/'experiments/backlog.csv')==[]

def test_status_and_artifacts():
    eid=new()
    with d.connect() as c:
        with pytest.raises(ValueError): d.transition(c,eid,'PUBLISHED')
        assert len(generate(c,eid,'hooks'))==10
        assert generate(c,eid,'script')['duration']==30
        assert d.get(c,eid)['status']=='SCRIPTED'
        assert 'CTA take' in generate(c,eid,'brief')
        assert d.get(c,eid)['status']=='READY_TO_SHOOT'
        assert len(plan(c,eid))==3
        assert len(plan(c,eid))==3

def measured(c,eid,n):
    vid=plan(c,eid)[0]['id']; pub='PUB-'+vid
    c.execute("INSERT INTO publications(id,variant_id,status) VALUES(?,?,'PUBLISHED')",(pub,vid))
    c.execute('INSERT INTO metrics(publication_id,collected_at,views,reach,shares,saves,follows,profile_visits,comments,completion_rate,qualified_leads,revenue) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(pub,'2026-10-26T00:00:00Z',2000,2000,n,n,n,n,n,.5,2,100))
    return pub

def test_scores_winners_evolve_latest_snapshot():
    ids=[new() for _ in range(3)]
    with d.connect() as c:
        pubs=[measured(c,e,n) for e,n in zip(ids,[10,10,30])]
        ranked=d.scores(c)
        assert ranked[0]['id']==ids[2]
        assert ranked[0]['score']==280
        assert ranked[1]['score']==100
        assert ranked[0]['lead_score']==10
        assert ranked[0]['winner']
        assert len(d.evolve(c,ids[2]))==10
        assert len(d.evolve(c,ids[2]))==10
        with pytest.raises(ValueError): d.evolve(c,ids[0])
        c.execute('INSERT INTO metrics(publication_id,collected_at,views,reach) VALUES(?,?,?,?)',(pubs[2],'2026-10-27T00:00:00Z',3000,3000))
        assert next(r for r in d.scores(c) if r['id']==ids[2])['reach']==3000

def test_metrics_validation_and_upsert(tmp_path):
    eid=new()
    with d.connect() as c: pub=measured(c,eid,10)
    p=tmp_path/'metrics.csv'
    def write(rate):
        with p.open('w') as f:
            w=csv.DictWriter(f,fieldnames=['publication_id','collected_at','reach','completion_rate']);w.writeheader();w.writerow(dict(publication_id=pub,collected_at='2026-10-28T00:00:00Z',reach=3000,completion_rate=rate))
    write(2)
    with pytest.raises(ValueError): d.import_metrics(p)
    write(.6); assert d.import_metrics(p)==1; assert d.import_metrics(p)==1
    with d.connect() as c: assert c.execute('select count(*) from metrics').fetchone()[0]==2

def test_dashboard_and_xss_as_data():
    with d.connect() as c: d.create(c,{'hypothesis':'<script>alert(1)</script>'})
    client=TestClient(app)
    assert client.get('/').status_code==200
    state=client.get('/api/state').json()
    assert state['overview']['experiments']==1
    assert state['experiments'][0]['hypothesis'].startswith('<script>')

def test_cli_dry_run_and_approval():
    import sys
    def run(*args,ok=True):
        r=subprocess.run([sys.executable,'-m','cli.main',*args],capture_output=True,text=True)
        assert (r.returncode==0)==ok, r.stderr
        return r.stdout
    eid=new()
    run('--dry-run','experiment','new','--hypothesis','Не сохранять')
    with d.connect() as c:
        assert c.execute('select count(*) from experiments').fetchone()[0]==1
        plan(c,eid)
        c.execute("UPDATE experiments SET status='READY' WHERE id=?",(eid,))
    pubs=json.loads(run('publish','queue')); pub=pubs[0]['id']
    run('publish','record',pub,'--external-id','manual-1','--published-at','2026-10-26T12:00:00Z',ok=False)
    run('publish','approve',pub)
    run('publish','record',pub,'--external-id','manual-1','--published-at','2026-10-26T12:00:00Z')
    with d.connect() as c: assert d.get(c,eid)['status']=='PUBLISHED'
