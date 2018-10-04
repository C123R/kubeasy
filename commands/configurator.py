import sys
import os
import shlex
from halo import Halo
import colorama
import yaml
import time
from socket import socket
import subprocess
import threading
from subprocess import PIPE, Popen, call, check_output
import webbrowser
from kubernetes import client, config

from prettytable import PrettyTable

from config._cmds import get_cmd, get_config_cmd
from config._config import get_k8s_config

K8S_CONFIG = get_k8s_config()

'''
def checkInternet():
    
    
    This is to test the internet connection for your machine.
    Tries to connect to login.microsoftonline.com.
    
    
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname('login.microsoftonline.com')
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((host, 443), 5)
        return True

    except:
        pass
        return False

'''


def azure_login(spinner):
    
    '''
    Checks if there is valid azure login session, if not
    make an azure login using azure cli --> az login

    Return:
            True for successful login

    '''
    # Check if we have valid azure cli session
    try:
        process = Popen(shlex.split(get_cmd('login_check')), stdout=PIPE, stderr=PIPE)
        process.communicate(timeout=5)
        rc = process.wait()

              # Doing Azure login
        while rc:
            try:
                process = Popen(shlex.split(get_cmd('login')), stdout=PIPE, stderr=PIPE)
                process.communicate()    # execute it, the output goes to the stdout
                rc = process.wait()
            except Exception as e:
                spinner.fail(colorama.Fore.RED + 'Login failed, try doing login with \"az login\"..')
                sys.exit(e)

        default_subscription = (check_output(get_cmd('account'),shell=True).decode('utf-8')).rstrip()
        spinner.succeed(colorama.Fore.GREEN + 'Login successded --> ({})'.format(default_subscription))
        return True

    except subprocess.TimeoutExpired as e :
        (colorama.Fore.RED + 'Timeout of Azure Login {}!'.format(e))
        return False
        proc.kill()
    
    print('here')
    return False

def _config_loader():


    with open(K8S_CONFIG) as stream:

        config = yaml.safe_load(stream)

        if config == None:
            return False

        return config


def _isExist(cluster_name):
    
    '''
    
    Read ~/.kube/config to check if the provided cluster name is already configured under ~/.kube/config

    :param cluster_name: Name of cluster to check against.
    :return: True or False 

    '''
    config = _config_loader()

    if config:

        for cluster in config.get('clusters', []):                
                if (cluster['name'] == cluster_name):
                    return True 

    return False



def get_current_context():
    
    '''
    Read ~/.kube/config to get the current context from the merged kubeconfig --> 'kubectl config current-context'

    return: current_context 
    '''

    config = _config_loader()
    if config:
        return config.get('current-context')


'''
TO DO
def get_AKSAccounts(print=False):
    
    
    To get the list of AKS Account list

 

    aksAccount = []
    list = check_output(get_cmd('account_list'),shell=True)
    for a in list.splitlines():
        a = (a.decode('utf-8')).rstrip('\t')
        aksAccount.append(a)
    return aksAccount
'''

def get_AKSList(output=False):
    
    '''
    To get the list of AKS Cluster for the default Azure subscription

    You need to login via Azure CLI first, use azure_login function for this.

    Return:
            dict of Azure AKS cluster and respective resource group if no cluster_name provided.
            
    '''
    # Dict stores Azure AKS cluster and respective Resource group.
    akslist = {}

    # Temporary array to get the list of AKS cluster from azure.
    tempAKS = []

    list = check_output(get_cmd('aks_list'),shell=True)

    for a in list.splitlines():

        a = (a.decode('utf-8')).split()
        tempAKS.append(a)

    akslist = dict(tempAKS)

    if output and akslist:
        
        header = ['AKS Cluster','Resource Group']
        print(colorama.Fore.GREEN + 'List of AKS clusters which are currently available for your default subscription:\n')
        _print_table(akslist,header)

    elif output and not akslist:
        
        print(colorama.Fore.YELLOW + 'Currently there are no clusters configured for kubeasy, Please check kubeasy -h for how to add new clusters.')

    else:  
        return akslist



def addConfig(spinner,cluster_name):
    
    ''' 
    To add the AKS cluster configuration to default Kubeasy directory.

    Validate the correct clustername by comparing with the list of AKS cluster for the default Azure subscription

    Arguments: 
            spinner obj
            name of AKS cluster
    Return:
            'success' if configuration copied successfully.
            'error' while copying the file.
            'incorrect_cluster' if cluster is not present in Azure subscription.
    '''

    aksClusters = get_AKSList()

    if cluster_name in aksClusters:
            
        process = Popen(shlex.split(get_config_cmd(cluster_name,aksClusters[cluster_name])), stdout=PIPE, stderr=PIPE)
        process.communicate()    # execute it, the STDOUT and STDERR are disabled
        rc = process.wait()
        if not rc:
            spinner.succeed(colorama.Fore.GREEN + 'Added "{}" configuration to kubeasy default directory.'.format(cluster_name))
        else:
            spinner.fail(colorama.Fore.RED + 'Error downloading the configuration for the {},Please try to get the config file with the mentioned command --> \"{}\"'.format(cluster_name,get_config_cmd(cluster_name,aksClusters[cluster_name])))

    else:
        
        spinner.fail(colorama.Fore.RED + 'Invalid AKS cluster {} !!'.format(cluster_name))
        get_AKSList(print)




def get_kubeasyList(output=False):
    

    kubeasyList = {}
    config = _config_loader()

    if config:

            for cluster in config.get('clusters', []):

                if cluster['name'] == get_current_context():
                    kubeasyList['** ' + cluster['name']] = cluster['cluster']['server']
                else:
                    kubeasyList['   ' + cluster['name']] = cluster['cluster']['server']

    if output and kubeasyList:
    
        header = ['K8s Cluster','Master']
        print('\n List of clusters which are currently ready to use for kubeasy:')
        print(colorama.Fore.GREEN + '\n - \'kubeasy -d\' to access Kubernetes dashboard for the current context.')
        print(colorama.Fore.GREEN + ' - \'kubeasy -c <cluster_name>\' to switch to another listed context.\n')
        _print_table(kubeasyList,header)
        print(colorama.Fore.GREEN + '\nNote: ** indicates current context.\n')
        
    elif output and not kubeasyList:

        print('\n Currently there are no clusters configured for kubeasy, Please check kubeasy -h for how to add new clusters.')
    
    else:

        return kubeasyList
    
        

def _print_table(list,header):
     
    '''
    Print list in Table format
    Arguments:
              list, or dict
              header which defines the table header
    '''
    x = PrettyTable()
    x.field_names = header
    for item in list:
        x.add_row([item,list[item]])

    print(x)
  

def set_k8s_context(cluster):
    

    config = _config_loader()

    if config:

        if _isExist(cluster) and (cluster != get_current_context()):

            config['current-context'] = cluster

            with open(K8S_CONFIG, 'w+') as stream:
                yaml.dump(config, stream, default_flow_style=False)
            
            print(colorama.Fore.GREEN + '\"{}\" set as the current context.'.format(cluster))
        
        elif _isExist(cluster) and (cluster == get_current_context()):

            print(colorama.Fore.YELLOW + '\"{}\" already set as the current context.'.format(cluster))
        
        else:
            print(colorama.Fore.RED + '\n This is not valid cluster--> {} !!'.format(cluster))
            get_kubeasyList(print)
    
    else:

        print(colorama.Fore.RED + '{} is not a valid kubeconfig!'.format(K8S_CONFIG))



##Copied from Azure CLI for AKS

def wait_then_open(url):
    
    """
    Waits for a bit then opens a URL.  Useful for waiting for a proxy to come up, and then open the URL.
    """
    spinner = Halo(text=colorama.Fore.GREEN + 'Opening Kubernetes Dashboard for {} --> {}'.format(get_current_context(),url), spinner='dots',color='yellow')
    spinner.start()
    time.sleep(3)
    webbrowser.open_new_tab(url)
    spinner.info(colorama.Fore.GREEN + 'Running dashboard for {}, Press CTRL+C to stop the port forwarding..'.format(get_current_context()))


##Copied from Azure CLI for AKS

def wait_then_open_async(url):
    """
    Spawns a thread that waits for a bit then opens a URL.
    """
    t = threading.Thread(target=wait_then_open, args=({url}))
    t.daemon = True
    t.start()


def get_dashboard():

    # Get free port 
    with socket() as s:
        s.bind(('',0))
        listen_port = (s.getsockname()[1])
    try:
        pod = (check_output(get_cmd('dashboard_pod'),shell=True).decode('utf-8')).rstrip()

    except subprocess.CalledProcessError as e:
        raise('Not able to find the k8s dashboard pod: {}'.format(e))

    wait_then_open_async('http://localhost:{}'.format(listen_port))
   # wait_then_open_async('http://localhost:{}/api/v1/namespaces/kube-system/services/http:kubernetes-dashboard:/proxy/#!/overview?namespace=default'.format(listen_port))

    try:
        subprocess.call(["kubectl", "-n", "kube-system",
                         "port-forward", pod, "{}:9090".format(listen_port)],stdout=PIPE, stderr=PIPE)
        
    except KeyboardInterrupt:
        return
