from celery import shared_task
import jinja2
import shutil
import glob
import subprocess
import yaml

@shared_task
def extract_results(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)
  a = open('{}/hype.logfile'.format(workdir)).readlines()
  limits = [l for l in a if 'limit' in l]
  results = [float(l.strip().split('=')[-1]) for l in limits]

  with open('{}/results.yaml'.format(workdir),'w') as f:
    f.write(yaml.dump(results,default_flow_style=False))

  return jobguid

@shared_task
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
  with open(logfile,'w') as log:
    subprocess.call(['hype/bin/hype',os.path.abspath(filledtemplate)], stdout = log)

  io.Of('/monitor').Emit('hype_done_{}'.format(jobguid))

  return jobguid

@shared_task
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

def get_chain(queuename):
  chain = (
            hype.subtask(queue=queuename) |
            extract_results.subtask(queue=queuename)
          )
  return chain  
