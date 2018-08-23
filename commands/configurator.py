import sys
import os
import shlex
from halo import Halo
import colorama
import yaml
import socket
import subprocess
from subprocess import PIPE, Popen, call, check_output

from prettytable import PrettyTable

from .aksCommands import get_cmd, get_config_cmd


K8S_CONFIG = os.path.join(os.path.expanduser('~'), '.kube/config')



def checkInternet():
    
    '''
    This is to test the internet connection for your machine.
    Tries to connect to login.microsoftonline.com.
    '''
    
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname('login.microsoftonline.com')
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((host, 80), 2)
        return True

    except:
        pass
        return False



def azure_login(spinner):
    
    '''
    Checks if there is valid azure login session, if not
    make an azure login using azure cli --> az login

    Return:
            True for successful login

    '''
    
    # Check if we have valid azure cli session

    if checkInternet():
        process = Popen(shlex.split(get_cmd('login_check')), stdout=PIPE, stderr=PIPE)
        process.communicate()    # execute it, the output goes to the stdout    
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
    else:
        spinner.fail(colorama.Fore.RED + 'Looks like there is an issue with internet connection :(')
        sys.exit()


def isExist(cluster_name):
    

        
    with open(K8S_CONFIG) as stream:
        config = yaml.safe_load(stream)

        for cluster in config.get('clusters', []):
            
            if (cluster['name'] == cluster_name):
                return True   
                
        
    return False



def get_current_context():
    
    print('here')
    with open(K8S_CONFIG) as stream:
        config = yaml.safe_load(stream)

        print(config.get('current-context'))
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

def get_AKSList(print=False):
    
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

    if print and akslist:
        
        header = ['AKS Cluster','Resource Group']
      # spinner = Halo(text=colorama.Fore.GREEN + 'Getting list of AKS clusters for your subscription:', spinner='dots',color='yellow')
        print(colorama.Fore.GREEN + 'List of AKS clusters which are currently available for your default subscription:\n')
        print_table(akslist,header)
    elif print and not akslist:
     #   spinner = Halo(text=colorama.Fore.GREEN + 'Getting list of AKS clusters for your subscription:', spinner='dots',color='yellow')
        #spinner.succeed(colorama.Fore.GREEN + 'List of AKS clusters which are currently available for your default subscription:\n')
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




def get_kubeasyList(print=False):
    

    kubeasyList = {}  

    with open(K8S_CONFIG) as stream:
        config = yaml.safe_load(stream)


        for cluster in config.get('clusters', []):
            if cluster['name'] == get_current_context():
                kubeasyList['** ' + cluster['name']] = cluster['cluster']['server']
            else:
                kubeasyList['   ' + cluster['name']] = cluster['cluster']['server']

    if print and kubeasyList:
        header = ['K8s Cluster','Master']
        print('\n List of clusters which are currently ready to use for kubeasy:\n')
        print_table(kubeasyList,header)
        print('\nNote: ** indicates current context, use \"kubeasy -c <cluster_name>\" to switch context.\n')
        
    elif print and not kubeasyList:
        print('\n Currently there are no clusters configured for kubeasy, Please check kubeasy -h for how to add new clusters.')
    

    else:
        return kubeasyList
    
        
def print_table(list,header):
     
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
    
    kubeContext = "kubectl config use-context {}".format(cluster)

    
    if isExist(cluster) and (cluster != get_current_context()):

        process = Popen(shlex.split(kubeContext), stdout=PIPE, stderr=PIPE)
        process.communicate()    # execute it, the output goes to the stdout
        rc = process.wait()
        if not rc:
            print(colorama.Fore.GREEN + 'Switched successdully to {} context !!'.format(cluster))
        else:
            # Need to catch properly
            print(colorama.Fore.RED + 'Some error')

    elif isExist(cluster) and (cluster == get_current_context()):
        print(colorama.Fore.YELLOW + '\n Already set as the current context--> {} !!'.format(cluster))
        get_kubeasyList(print)

    else:
        print(colorama.Fore.RED + '\n This is not valid cluster--> {} !!'.format(cluster))
        get_kubeasyList(print)



def get_dashboard(cluster_name):

    kubeConfig = K8S_CONFIG + cluster_name

    if os.path.exists(kubeConfig):
        
        print(colorama.Fore.GREEN + 'Proxy running on 127.0.0.1:8001/ui')
        print(colorama.Fore.GREEN + 'Press CTRL+C to close the tunnel...')
        subprocess.call(["kubectl", "--kubeconfig", kubeConfig, "proxy", "--port=62579"])
        proxy_url = 'http://127.0.0.1:62579/'
        wait_then_open_async(proxy_url)
