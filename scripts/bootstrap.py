"""Idempotent local database bootstrap; never fabricate metrics or publications."""
from app.core import ROOT,connect,init,import_experiments
from app.content import generate,plan
init()
import_experiments(ROOT/'experiments/backlog.csv')
with connect() as c:
    for i in range(1,11):
        eid=f'BALI-{i:04d}'
        for kind in ['hooks','script','brief','caption']:
            if not c.execute('SELECT 1 FROM artifacts WHERE experiment_id=? AND kind=?',(eid,kind)).fetchone():
                generate(c,eid,kind)
        plan(c,eid)
print('50 seed experiments ready; first 10 have local drafts and variant plans.')
