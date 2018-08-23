import sys
import os
from subprocess import Popen, PIPE, check_output

K8S_HOME = os.path.join(os.path.expanduser('~'), '.kube/')
command_list = {

    'login':'az login',
    'login_check': 'az group list',
    'aks_list': 'az aks list --query \"[*].{Name:name,ResourceGroup:resourceGroup}\" -o tsv',
   # 'aks_list': 'az aks list --query \"[?provisioningState == \'Succeeded\'].{Name:name,ResourceGroup:resourceGroup,Master:fqdn,K8sVersion:kubernetesVersion}\" -o tsv',
    'account_list' : 'az account list --query \"[*].{Name:name,Default:isDefault}\" -o tsv',
    'account': 'az account show --query \"name\" -o tsv',
    'dashboard_pod' : 'kubectl get pods -n kube-system --output name --selector k8s-app=kubernetes-dashboard',

}

def get_cmd(cmd):
    
    if not cmd in command_list:
        print(cmd)
        sys.exit('\nNo such azure command, check command_list dict')

    return command_list[cmd]


def get_config_cmd(cluster_name,resource_group):
    

    get_kubeconfig_cmd = "az aks get-credentials -n {} -g {}".format(cluster_name,resource_group)
    
    return get_kubeconfig_cmd

