from celery import Celery,task
import jinja2
import shutil
import glob
import subprocess
import os
import redis
import emitter
import zipfile

CELERY_RESULT_BACKEND = 'redis://lheinric-recast-hype:6379/0'
app = Celery('tasks', backend='redis://lheinric-recast-hype', broker='redis://lheinric-recast-hype')

red = redis.StrictRedis(host = 'lheinric-recast-hype', db = 0)
io  = emitter.Emitter({'client': red})

import requests
def download_file(url,download_dir):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    download_path = '{}/{}'.format(download_dir,local_filename)
    with open(download_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return download_path    

@task
def results(requestId,parameter_point):
  resultdir = 'results/{}/{}'.format(requestId,parameter_point)
  a = open('{}/hype.logfile'.format(resultdir)).readlines()
  limits = [l for l in a if 'limit' in l]
  results = [float(l.strip().split('=')[-1]) for l in limits]
  return results

@task
def postresults(jobguid,requestId,parameter_point):
  workdir = 'workdirs/{}'.format(jobguid)
  hypelog = '{}/hype.logfile'.format(workdir)
  resultdir = 'results/{}/{}'.format(requestId,parameter_point)
  
  
  if(os.path.exists(resultdir)):
    shutil.rmtree(resultdir)
    
  os.makedirs(resultdir)
  
  print 'trying to copy file'
  print '{}/hype.logfile'.format(workdir)
  print '{}/hype.logfile'.format(resultdir)

  shutil.copyfile('{}/hype.logfile'.format(workdir),'{}/hype.logfile'.format(resultdir))

  a = open(hypelog).readlines()
  limits = [l for l in a if 'limit' in l]
  results = [float(l.strip().split('=')[-1]) for l in limits]

  print results

  #also copy to server
  subprocess.call('''ssh ciserver@lheinric-recast-hype "mkdir -p /home/ciserver/recast/recast-frontend-prototype/results/{}"'''.format(requestId),shell = True)
  subprocess.call(['scp', '-r', resultdir,'ciserver@lheinric-recast-hype:/home/ciserver/recast/recast-frontend-prototype/results/{}/{}'.format(requestId,parameter_point)])
  
  io.Of('/monitor').Emit('postresults_done_{}'.format(jobguid),{'requestId':requestId})

@task
def hype(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)


  spin0 = os.path.abspath('../implementation/hype_static/fake_spin0.yoda'.format(workdir))
  spin2 = os.path.abspath('{}/inputs/fake_spin2.yoda'.format(workdir))
  
  env = jinja2.Environment(undefined=jinja2.StrictUndefined)

  hypetmplt = '../implementation/hype_static/Higgs_spin0_vs_2_diphoton_hepdata.tmplt'
 

  print "trying to render template"
  with open(hypetmplt) as hypeRunTemplate:
    basename = os.path.basename(hypetmplt)
    filledtemplate = '{}/{}'.format(workdir,basename.rsplit('.',1)[0]+'.hype')

    template = env.from_string(hypeRunTemplate.read())

    with open(filledtemplate,'w+') as output:
        print "writeing template to {}".format(filledtemplate)
        output.write(template.render({'SPIN_0_YODA':spin0,'SPIN_2_YODA':spin2}))


  logfile = '{}/hype.logfile'.format(workdir)
  print "trying to run hype and print to logfile {}".format(logfile)
  with open(logfile,'w') as log:
    subprocess.call(['../implementation/hype/bin/hype',os.path.abspath(filledtemplate)], stdout = log)

  io.Of('/monitor').Emit('hype_done_{}'.format(jobguid))

  return jobguid

@task
def prepare_job(jobguid,jobinfo):
  print "job info is {}".format(jobinfo)
  print "job uuid is {}".format(jobguid)
  workdir = 'workdirs/{}'.format(jobguid)

  input_url = jobinfo['run-condition'][0]['lhe-file']
  print "downloading file : {}".format(input_url) 
  filepath = download_file(input_url,workdir)
  
  print "downloaded file to: {}".format(filepath)

  with zipfile.ZipFile(filepath)as f:  
    f.extractall('{}/inputs'.format(workdir))

  return jobguid

@task
def prepare_workdir(fileguid,jobguid):
  uploaddir = 'uploads/{}'.format(fileguid)
  workdir = 'workdirs/{}'.format(jobguid)
  
  os.makedirs(workdir)
  # os.symlink(os.path.abspath(uploaddir),workdir+'/inputs')
  io.Of('/monitor').Emit('pubsubmsg','prepared workdirectory...')

  print "emitting to room"
  io.Of('/monitor').In(str(jobguid)).Emit('workdir_done','prepared workdirectory...')

  return jobguid
  

import recastapi.request
import json
import uuid


def get_chain(request_uuid,point):
  request_info = recastapi.request.request(request_uuid)
  jobinfo = request_info['parameter-points'][point]


  jobguid = uuid.uuid1()

  analysis_queue = 'hype_queue'
  
  chain = (
            prepare_workdir.subtask((request_uuid,jobguid),queue=analysis_queue) |
            prepare_job.subtask((jobinfo,),queue=analysis_queue) |
            hype.subtask(queue=analysis_queue) |
            postresults.subtask((request_uuid,point),queue=analysis_queue)
          )
  return (jobguid,chain)
  
