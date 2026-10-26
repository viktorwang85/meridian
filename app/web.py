from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .core import ROOT, connect, scores, today

app=FastAPI(title='BALI CONTENT OS')

@app.get('/',response_class=HTMLResponse)
def dashboard():
    return (ROOT/'app/dashboard.html').read_text()

@app.get('/api/state')
def state():
    with connect() as c:
        experiments=[dict(r) for r in c.execute('SELECT * FROM experiments ORDER BY seq')]
        ranked=scores(c)
        publications=[dict(r) for r in c.execute('SELECT * FROM publications')]
        dna={}
        for k in ['hook','pillar','motive','cta','format']:
            buckets={}
            for r in ranked:
                buckets.setdefault(r[k] or 'Не указан',[]).append(r['score'])
            dna[k]=sorted([{'name':n,'score':round(sum(v)/len(v),2),'samples':len(v)} for n,v in buckets.items()],key=lambda r:r['score'],reverse=True)[:10]
        return {'experiments':experiments,'scores':ranked,'publications':publications,'today':today(c),'dna':dna,
          'learnings':[dict(r) for r in c.execute('SELECT * FROM learnings')],
          'overview':{'experiments':len(experiments),'published':sum(p['status']=='PUBLISHED' for p in publications),
          **{k:sum(r[k] for r in ranked) for k in ['reach','follows','qualified_leads','revenue']},'winners':sum(r['winner'] for r in ranked)}}
