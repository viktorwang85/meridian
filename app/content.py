import json
from .core import ROOT, artifact, get, transition

HOOKS = {
 'curiosity': 'Какой Бали я хочу показать Насте первым?',
 'confession': 'Я скучаю не по открыткам с Бали. Я скучаю по обычным дням.',
 'authority': 'Я прожил на Бали 11 лет. Вот с чего начну возвращение.',
 'contrarian': 'Мой маршрут по Бали начинается не со списка лучших пляжей.',
 'story': 'Когда я уезжал с Бали, я не знал, когда вернусь.',
 'specific number': 'Три вещи, которые я хочу снова сделать на Бали.',
 'identity': 'Если тебе в поездке важны люди, давай знакомиться.',
 'invitation': 'Мы с Настей возвращаемся на Бали. Несколько человек могут поехать с нами.',
 'question': 'Ты бы поехал на Бали с человеком, который жил там 11 лет?',
 'visual-first': '[Покажи архивный кадр] Хочу вернуться сюда и показать это Насте.'}

class LocalProvider:
    """Deterministic drafts, explicitly not a remote model response."""
    def generate(self, kind, e):
        if kind == 'hooks':
            return [{'type': k, 'text': f'{v} Тема: {e["angle"] or e["hypothesis"]}'} for k,v in HOOKS.items()]
        if kind == 'script':
            # Timed outline asks for truthful personal detail rather than inventing anecdotes.
            return {'duration': e['duration'], 'HOOK': e['hook'] or f'Хочу показать Насте: {e["angle"]}.',
              'OPEN LOOP': 'Почему я выбрал именно это?',
              'STORY/PROOF': f'Тема: {e["hypothesis"]}. [Расскажи один реальный личный эпизод; покажи свой архив.]',
              'PAYOFF': 'Такой Бали я хочу прожить снова — вместе с Настей и небольшой компанией.',
              'CTA': e['cta'], 'note': 'Черновик. Заменить скобки личной историей; прочитать вслух и уложить в тайминг.'}
        if kind == 'brief':
            return {'shot list':['Лицо крупно: hook','Средний план: личная история','Архив места','CTA отдельным дублем'],
              'A-roll':'Виктор рассказывает один эпизод', 'B-roll':'Свой архив места, дорога, бытовая деталь',
              'location':'Тихое место с естественным светом', 'wardrobe':'Однотонная привычная одежда',
              'first frame':e['hook'] or e['angle'], 'camera distance':'Крупный, затем средний план',
              'delivery note':'Говорить Насте, а не рекламной аудитории', 'natural actions':'Показать фото или карту',
              'archive footage requests':e['angle'], 'CTA take':e['cta']}
        if kind == 'caption':
            return {'caption':f'{e["hook"] or e["angle"]}\n{e["hypothesis"]}\n{e["cta"]}', 'cta':e['cta']}
        raise ValueError('Неизвестный генератор')


PROVIDERS = {'local': LocalProvider}
ROLES = {'hooks':'Hook Lab','script':'Script Writer','brief':'Shooting Director','caption':'Caption Writer','ideas':'Idea Miner','analysis':'Analyst','evolve':'Winner Evolver'}


def generate(c, eid, kind, provider='local'):
    e = get(c, eid)
    if provider == 'prompt':
        template = (ROOT / 'content/prompts' / f'{kind}.md').read_text()
        body = template + '\n\nКонтекст:\n' + json.dumps(e, ensure_ascii=False, indent=2)
        result = artifact(c, eid, kind + '-prompt', body)
        return result
    if provider not in PROVIDERS:
        raise ValueError('provider: local или prompt; API-интеграции пока нет')
    body = PROVIDERS[provider]().generate(kind, e)
    artifact(c, eid, kind, body)
    if kind == 'script':
        c.execute('UPDATE experiments SET script=? WHERE id=?', (json.dumps(body,ensure_ascii=False),eid))
        if e['status'] == 'IDEA':
            transition(c,eid,'SCRIPTED')
    if kind == 'brief' and e['status'] == 'SCRIPTED':
        transition(c,eid,'READY_TO_SHOOT')
    return body


def plan(c, eid):
    e = get(c,eid)
    existing = c.execute('SELECT * FROM variants WHERE experiment_id=?', (eid,)).fetchall()
    if existing:
        return [dict(r) for r in existing]
    result=[]
    for i,(kind,frame,style,duration) in enumerate([
      ('personal','Лицо Виктора','Личная история с архивной вставкой',30),
      ('route','Карта маршрута','Карта → место → объяснение выбора',45),
      ('invitation','Виктор и Настя','Диалог и отдельный CTA',15)],1):
        vid=f'{eid}-V{i:02d}'
        c.execute('INSERT INTO variants(id,experiment_id,variant_type,hook,first_frame,edit_style,duration,cta) VALUES(?,?,?,?,?,?,?,?)',(vid,eid,kind,e['hook'],frame,style,duration,e['cta']))
        result.append(dict(id=vid,experiment_id=eid,variant_type=kind,first_frame=frame,edit_style=style,duration=duration,cta=e['cta']))
    return result
