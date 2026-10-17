import importlib.util,json,os,pathlib,tempfile,types,sys
# Exercise real persistence and callback authorization without contacting Feishu.
root=pathlib.Path(tempfile.mkdtemp());cred=root/'creds';cred.mkdir();os.environ['STATE_DIRECTORY']=str(root/'state');os.environ['CREDENTIALS_DIRECTORY']=str(cred)
(cred/'app.json').write_text(json.dumps({'chat_id':'oc_test'}));(cred/'beszel.json').write_text('{}');(cred/'ingest-token').write_text('test')
spec=importlib.util.spec_from_file_location('cards',str(pathlib.Path(__file__).with_name('feishu-cards.py')));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
i=m.ingest('test','dedup','Test','Detail','critical');assert i==m.ingest('test','dedup','Test','Detail','critical');assert m.DB.execute('SELECT count(*) FROM incidents').fetchone()[0]==1
m.DB.execute('UPDATE incidents SET message_id=\'om_test\' WHERE id=?',(i,));m.DB.execute('INSERT INTO messages VALUES(\'om_test\',?)',(i,));m.DB.commit()
def click(act,eid='e1',chat='oc_test',actor='ou_test'):
 e=types.SimpleNamespace(header=types.SimpleNamespace(event_id=eid),event=types.SimpleNamespace(context=types.SimpleNamespace(open_chat_id=chat,open_message_id='om_test'),operator=types.SimpleNamespace(open_id=actor),action=types.SimpleNamespace(value={'incident':i,'action':act}),token=eid));return m.action(e)
click('claim',chat='oc_other');assert m.get(i)['actor']==''
click('claim');assert m.get(i)['actor']=='ou_test';click('claim');assert m.DB.execute('SELECT count(*) FROM actions').fetchone()[0]==1
click('pause120','e2');assert m.paused(m.get(i))
click('resume','e3');assert not m.paused(m.get(i))
click('mute30','e4');assert m.paused(m.get(i))
click('resolve','e5');assert not m.get(i)['active'];assert m.get(i)['status']=='resolved'
j=m.ingest('beszel','cpu','CPU','90%','warning');m.ingest('beszel','cpu','CPU','90%','warning',False);assert m.get(j)['status']=='recovered'
k=m.ingest('beszel','cpu','CPU','90%','warning');assert k!=j
assert m.DB.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
print('PASS: persistence, deduplication, callback group validation, replay protection, claim, global pause/resume, per-incident mute, manual test resolve, automatic recovery and recurrence.')
