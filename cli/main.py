import argparse
import csv
import json
import sys
from pathlib import Path
from app import core as db
from app.content import generate, plan


def parser():
    p=argparse.ArgumentParser(prog='bali',description='BALI CONTENT OS · локальный контентный эксперимент')
    p.add_argument('--dry-run',action='store_true',help='Проверить операцию без сохранения; указывать до команды')
    s=p.add_subparsers(dest='command',required=True)
    s.add_parser('init')
    for group, commands in {'experiments':['import','list','export'], 'experiment':['new','status'], 'hooks':['generate'], 'script':['generate'], 'variants':['plan'], 'metrics':['import'], 'footage':['index','list','tag'], 'learning':['add','list'], 'publish':['queue','approve','record']}.items():
        g=s.add_parser(group); subs=g.add_subparsers(dest='action',required=True)
        for cmd in commands:
            a=subs.add_parser(cmd)
            if group in ['hooks','script','variants'] or (group=='experiment' and cmd=='status') or group=='publish' and cmd!='queue' or group=='learning' and cmd=='add': a.add_argument('id')
            if cmd in ['import','export','index']: a.add_argument('path')
            if group=='experiment' and cmd=='new':
                for k in db.FIELDS:
                    a.add_argument('--'+k,required=k=='hypothesis',default=None)
            if cmd=='status': a.add_argument('status',choices=db.STATUSES)
            if group in ['hooks','script']: a.add_argument('--provider',choices=['local','prompt'],default='local')
            if group=='footage' and cmd=='tag':
                a.add_argument('path'); a.add_argument('--tags',required=True); a.add_argument('--location',default=''); a.add_argument('--people',default=''); a.add_argument('--scene',default=''); a.add_argument('--usable-as',default=''); a.add_argument('--notes',default='')
            if group=='learning' and cmd=='add':
                a.add_argument('--text',required=True); a.add_argument('--category',default='manual'); a.add_argument('--confidence',type=float,default=.5)
            if group=='publish' and cmd=='record':
                a.add_argument('--external-id',required=True); a.add_argument('--published-at',required=True)
    for cmd in ['shoot-brief','caption','prompt','evolve']:
        a=s.add_parser(cmd); a.add_argument('id')
        if cmd in ['shoot-brief','caption']: a.add_argument('--provider',choices=['local','prompt'],default='local')
        if cmd=='prompt': a.add_argument('kind',choices=['hooks','script','brief','caption','ideas','analysis','evolve']); a.add_argument('--output',required=True)
    for cmd in ['score','winners','today']: s.add_parser(cmd)
    a=s.add_parser('dashboard'); a.add_argument('--port',type=int,default=8000)
    return p


def main():
    args=parser().parse_args(); cmd=args.command; act=getattr(args,'action',None)
    try:
        if cmd=='dashboard':
            if args.dry_run: return print('uvicorn app.web:app --host 127.0.0.1 --port',args.port)
            import uvicorn
            uvicorn.run('app.web:app',host='127.0.0.1',port=args.port); return
        if cmd=='init':
            if not args.dry_run: db.init()
            print('SQLite schema ready' if not args.dry_run else 'Would initialize SQLite'); return
        if act=='import':
            result=db.import_experiments(args.path,args.dry_run) if cmd=='experiments' else db.import_metrics(args.path,args.dry_run)
        else:
            with db.connect() as c:
                if cmd=='experiments' and act in ['list','export']:
                    result=[dict(r) for r in c.execute('SELECT * FROM experiments ORDER BY seq')]
                    if act=='export' and not args.dry_run:
                        with Path(args.path).open('x',encoding='utf-8',newline='') as f:
                            w=csv.DictWriter(f,fieldnames=['id']+db.FIELDS); w.writeheader(); w.writerows({k:r[k] for k in ['id']+db.FIELDS} for r in result)
                elif cmd=='experiment':
                    result=db.create(c,{k:v for k in db.FIELDS if (v:=getattr(args,k)) is not None}) if act=='new' else db.transition(c,args.id,args.status)
                elif cmd in ['hooks','script','shoot-brief','caption','prompt']:
                    kind={'shoot-brief':'brief'}.get(cmd,cmd)
                    result=generate(c,args.id,args.kind if cmd=='prompt' else kind,'prompt' if cmd=='prompt' else args.provider)
                    if cmd=='prompt' and not args.dry_run:
                        with Path(args.output).open('x',encoding='utf-8') as f: f.write(result)
                elif cmd=='variants': result=plan(c,args.id)
                elif cmd=='evolve': result=db.evolve(c,args.id)
                elif cmd in ['score','winners']: result=[r for r in db.scores(c) if cmd=='score' or r['winner']]
                elif cmd=='today': result=db.today(c)
                elif cmd=='footage':
                    if act=='index': result=db.index_footage(c,args.path)
                    elif act=='tag':
                        cursor=c.execute('UPDATE footage SET tags=?,location=?,people=?,scene=?,usable_as=?,notes=? WHERE path=?',(args.tags,args.location,args.people,args.scene,args.usable_as,args.notes,str(Path(args.path).resolve())))
                        if cursor.rowcount!=1: raise ValueError('Сначала индексируйте файл')
                        result='Tagged'
                    else: result=[dict(r) for r in c.execute('SELECT * FROM footage')]
                elif cmd=='learning':
                    if act=='add':
                        db.get(c,args.id)
                        if not 0<=args.confidence<=1: raise ValueError('confidence: 0..1')
                        c.execute('INSERT INTO learnings VALUES(?,?,?,?,?,?)',(db.uuid.uuid4().hex,args.id,args.category,args.text,args.confidence,db.now()))
                    result=[dict(r) for r in c.execute('SELECT * FROM learnings')]
                elif cmd=='publish':
                    if act=='queue':
                        c.execute("INSERT OR IGNORE INTO publications(id,variant_id) SELECT 'PUB-'||v.id,v.id FROM variants v JOIN experiments e ON e.id=v.experiment_id WHERE e.status IN ('READY','SCHEDULED')")
                    elif act=='approve':
                        cur=c.execute("UPDATE publications SET status='APPROVED',approved_at=? WHERE id=? AND status='PENDING'",(db.now(),args.id))
                        if cur.rowcount!=1: raise ValueError('Нужна запись PENDING')
                    else:
                        db.datetime.fromisoformat(args.published_at.replace('Z','+00:00'))
                        pub=c.execute("SELECT p.*,e.status AS experiment_status FROM publications p JOIN variants v ON v.id=p.variant_id JOIN experiments e ON e.id=v.experiment_id WHERE p.id=? AND p.status='APPROVED'",(args.id,)).fetchone()
                        if not pub or pub['experiment_status'] not in ['READY','SCHEDULED','PUBLISHED','MEASURED']: raise ValueError('Нужны approve и готовый эксперимент')
                        c.execute("UPDATE publications SET status='PUBLISHED',published_at=?,external_id=? WHERE id=?",(args.published_at,args.external_id,args.id))
                        c.execute("UPDATE experiments SET status='PUBLISHED',updated_at=? WHERE id=(SELECT experiment_id FROM variants WHERE id=?) AND status IN ('READY','SCHEDULED')",(db.now(),pub['variant_id']))
                    result=[dict(r) for r in c.execute('SELECT * FROM publications')]
                else: raise ValueError('Неизвестная команда')
                if args.dry_run: c.rollback()
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError,db.sqlite3.Error) as e:
        print(f'Ошибка: {e}',file=sys.stderr); sys.exit(1)

if __name__=='__main__': main()
