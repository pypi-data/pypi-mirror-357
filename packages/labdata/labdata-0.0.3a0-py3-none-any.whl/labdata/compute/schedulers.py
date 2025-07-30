# this has functions to interact with different schedulers.

from ..utils import *
import subprocess as sub

LABDATA_LOG_FOLDER = Path(LABDATA_FILE).parent/'logs'

def slurm_exists():
    proc = sub.Popen('sinfo', shell=True, stdout=sub.PIPE, stderr = sub.PIPE)
    out,err = proc.communicate()
    if len(err):
        return False
    return True

def slurm_submit(jobname,
                 command,
                 ntasks = None,
                 ncpuspertask = None,
                 gpus = None,
                 memory = None,
                 walltime = None,
                 partition = None,
                 begin = None,
                 conda_environment = None,
                 module_environment = None,
                 mail = None,
                 sbatch_append = '',
                 **kwargs):

    if ncpuspertask is None and ntasks is None:
        from multiprocessing import cpu_count
        ncpuspertask = 4
        ntasks = 1
    if ntasks is None:
        ntasks = 1
    if ncpuspertask is None:
        ncpuspertask = 1
        
    sjobfile = '''#!/bin/bash -login
#SBATCH --job-name={jobname}
#SBATCH --output={logfolder}/{jobname}_%j.stdout
#SBATCH --error={logfolder}/{jobname}_%j.stdout

#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={ncpus}
'''.format(jobname = jobname,
           logfolder = LABDATA_LOG_FOLDER,
           ntasks = ntasks,
           ncpus = ncpuspertask)
    if not walltime is None:
        sjobfile += '#SBATCH --time={0} \n'.format(walltime)
    if not memory is None:
        sjobfile += '#SBATCH --mem={0} \n'.format(memory)
    if not gpus is None:
        sjobfile += '#SBATCH --gpus={0} \n'.format(gpus)
    if not partition is None:
        sjobfile += '#SBATCH --partition={0} \n'.format(partition)
    if not begin is None:
        sjobfile += '#SBATCH --begin={0} \n'.format(begin)
    if not mail is None:
        sjobfile += '#SBATCH --mail-user={0} \n#SBATCH --mail-type=END,FAIL \n'.format(mail)
    if not module_environment is None:
        sjobfile += '\n module purge\n'
        sjobfile += '\n module load {0} \n'.format(module_environment)
    if not conda_environment is None:
        sjobfile += 'conda activate {0} \n'.format(conda_environment)
    sjobfile += '''echo JOB {jobname} STARTED `date`
{cmd}
echo JOB FINISHED `date`
'''.format(jobname = jobname, cmd = command)

    if not LABDATA_LOG_FOLDER.exists():
        LABDATA_LOG_FOLDER.makedirs()
    nfiles = len(list(LABDATA_LOG_FOLDER.glob('*.sh')))
    filename = LABDATA_LOG_FOLDER/'{jobname}_{nfiles}.sh'.format(jobname = jobname,
                                                                 nfiles = nfiles+1)
    with open(filename,'w') as f:
        f.write(sjobfile)
    submit_cmd = 'cd {0} && sbatch {2} {1}'.format(filename.parent,
                                                   filename.name,
                                                   sbatch_append)
    proc = sub.Popen(submit_cmd, shell=True, stdout=sub.PIPE)
    out,err = proc.communicate()
    
    if b'Submitted batch job' in out:
        jobid = int(re.findall("Submitted batch job ([0-9]+)", str(out))[0])
        return jobid
    else:
        print(out)
        return None

         
def ssh_connect(address,user,permission_key=None):
    try:
        import paramiko 
    except:
        raise(OSError('You need paramiko installed: "pip install paramiko"'))
        
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = permission_key
    if not permission_key is None:
        keys_folder = Path(LABDATA_PATH)
        key = list(keys_folder.rglob(permission_key+'*')) # doen't care where it is inside labdata
        if len(key):
            key = key[0]
            with open(key,'r') as fd:
                privkey = paramiko.RSAKey.from_private_key(fd)
    ssh.connect(hostname = address,
                username = user, 
                pkey = privkey)
    return ssh
    
def slurm_schedule_remote(command,
                          address = None,
                          user = None,
                          permission_key=None,
                          jobname = 'unknown_1',
                          ncpus = None, 
                          queue = None,
                          gpus = None,
                          memory = None,
                          walltime = None,
                          begin = None,
                          conda_environment = None,
                          module_environment = None,
                          mail = None,
                          exclusive = True,
                          pre_cmds = '',
                          remote_dir = '/shared/labdata/remote_jobs',
                          **kwargs):
    sjobfile = f'''#!/bin/bash -login
#SBATCH --job-name={jobname}
#SBATCH --output={remote_dir}/{jobname}_%j.stdout
#SBATCH --error={remote_dir}/{jobname}_%j.stdout
#SBATCH --ntasks=1
'''
    if not ncpus is None:
        sjobfile += f'#SBATCH --cpus-per-task={ncpus}'
    if not walltime is None:
        sjobfile += '#SBATCH --time={0} \n'.format(walltime)
    if not memory is None:
        sjobfile += '#SBATCH --mem={0} \n'.format(memory)
    if not gpus is None:
        sjobfile += '#SBATCH --gpus={0} \n'.format(gpus)
    if not queue is None:
        sjobfile += '#SBATCH --partition={0} \n'.format(queue)
    if not begin is None:
        sjobfile += '#SBATCH --begin={0} \n'.format(begin)
    if not mail is None:
        sjobfile += '#SBATCH --mail-user={0} \n#SBATCH --mail-type=END,FAIL \n'.format(mail)
    if exclusive:
        sjobfile += '#SBATCH --exclusive \n'
    if not module_environment is None:
        sjobfile += '\n module purge\n'
        sjobfile += '\n module load {0} \n'.format(module_environment)
    if not conda_environment is None:
        sjobfile += 'conda activate {0} \n'.format(conda_environment)
    if not pre_cmds is None:
        pre_cmds = '\n'.join(pre_cmds)
    sjobfile += f'''echo JOB {jobname} STARTED \`date\`
tic=\`date +%s.%N\`
{pre_cmds}
{command}
echo JOB FINISHED \`date\`
toc=\`date +%s.%N\`
a=\`echo "(\$toc - \$tic)" | bc -l\`
b=\`printf %.3f \$a\`
echo JOB COMPLETED IN \$b min
'''
    remote_command = f'''
    mkdir -p {remote_dir}
    cat > {remote_dir}/{jobname}.sh << EOL
{sjobfile}
EOL

sbatch {remote_dir}/{jobname}.sh
    '''
    # try to connect to ssh
    #print(remote_command)
    if not 'conn' in kwargs.keys():
        conn = ssh_connect(address,user,permission_key)
    else:
        conn = kwargs['conn']
    stdin,stdout,stderr = conn.exec_command(remote_command)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    if 'Submitted batch job' in output:
        jobid = int(re.findall("Submitted batch job ([0-9]+)", str(output))[0])
        return jobid
    else:
        print(output,errors)    
        return None
