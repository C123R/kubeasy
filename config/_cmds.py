import sys

command_list = {

    'az_login':'az login',
    'az_login_check': 'az group list',
    'aks_list': 'az aks list --query \"[*].{Name:name,ResourceGroup:resourceGroup}\" -o tsv',
    'account_list' : 'az account list --query \"[*].{Name:name,Default:isDefault}\" -o tsv',
    'account': 'az account show --query \"name\" -o tsv',
    'dashboard_pod' : 'kubectl get pods -n kube-system --output name --selector k8s-app=kubernetes-dashboard',

}

azure = {

    'login':'az login',
    'login_check': 'az group list',
    'k8s_list': 'az aks list --query \"[*].{Name:name,ResourceGroup:resourceGroup}\" -o tsv',
    'account_list' : 'az account list --query \"[*].{Name:name,Default:isDefault}\" -o tsv',
    'account': 'az account show --query \"name\" -o tsv',

}

google = {

    'login':'gcloud auth login',
    'login_check': 'gcloud projects list',
    'k8s_list': 'gcloud container clusters list --format=\"value(selfLink.scope(),selfLink.scope(projects).segment(0)\"',

}


def get_cmd(cmd):
    
    if not cmd in command_list:
        print(cmd)
        sys.exit('\nNo such azure command, check command_list dict')

    return command_list[cmd]


def get_config_cmd(cluster_name,resource_group):
    

    get_kubeconfig_cmd = "az aks get-credentials -n {} -g {}".format(cluster_name,resource_group)
    
    return get_kubeconfig_cmd
