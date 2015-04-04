import jinja2
import shutil
import glob
import subprocess
import yaml
import os

import logging
log = logging.getLogger('RECAST')


def extract_results(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)
  a = open('{}/hype.logfile'.format(workdir)).readlines()
  limits = [l for l in a if 'limit' in l]

  labels = ['observed','expected-spin0','expected-spin2']
  values = [float(l.strip().split('=')[-1]) for l in limits]

  results = dict(zip(labels,values))
    
  with open('{}/results.yaml'.format(workdir),'w') as f:
    f.write(yaml.dump(results,default_flow_style=False))
    log.info('got results: {}'.format(results))
    
  return jobguid

def hype(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)


  spin0 = os.path.abspath('hype_static/fake_spin0.yoda'.format(workdir))
  spin2 = os.path.abspath('{}/inputs/fake_spin2.yoda'.format(workdir))
  
  env = jinja2.Environment(undefined=jinja2.StrictUndefined)

  hypetmplt = 'hype_static/Higgs_spin0_vs_2_diphoton_hepdata.tmplt'
 

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
  with open(logfile,'w') as logfile:
    subprocess.call(['hype/bin/hype',os.path.abspath(filledtemplate)], stdout = log)

  log.info('hype done')

  return jobguid

def resultlist():
    return ['hype.logfile','results.yaml']

def recast(ctx):
  jobguid = ctx['jobguid']
  hype(jobguid)
  extract_results(jobguid)
