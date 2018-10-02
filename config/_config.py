import os

def get_k8s_config():

    """ Return kube config file path and create one if not exist """

    k8sConfig = os.path.join(os.path.expanduser('~'), '.kube/config')

    if not os.path.exists(k8sConfig):
        
        open(k8sConfig, 'a').close()

    return k8sConfig