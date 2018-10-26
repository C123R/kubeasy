#!/usr/bin/env python
import sys
import colorama
import click
from halo import Halo
from subprocess import Popen, PIPE, check_output
from config._cmds import get_cmd, get_credentials
from core.configurator import login, get_K8SList, get_GKEList, addConfig, get_kubeasyList, get_dashboard, _isExist, set_k8s_context, get_current_context, get_k8s_config


def get_list(ctx, param, value):

    """ To get list of Kubernetes Clusters (As per ~/.kube/config) """

    if not value or ctx.resilient_parsing:
        return
    get_kubeasyList(output=True)
    ctx.exit()


def set_context(ctx, param, value):

    """ To set the kubernentes cofing context """

    if not value or ctx.resilient_parsing:
        return
    set_k8s_context(value)
    ctx.exit()


def print_version(ctx, param, value):

    """ Get the version of kubeasy """

    if not value or ctx.resilient_parsing:
        return
    click.echo('Kubeasy Version 0.1')
    ctx.exit()


def open_dashboard(ctx, param, value):

    """ Open kubernetes Dashboard with browser tab"""

    if not value or ctx.resilient_parsing:
        return
    
    get_dashboard()
    ctx.exit()



@click.group()
@click.help_option('-h','--help', help="Show the usage of kubeasy.")
@click.option('-v','--version',help="Show the version of kubeasy", is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('-l','--list',is_flag=True,help="List existing clusters in kubeasy.",callback=get_list,expose_value=False, is_eager=False)
@click.option('-c','--context',help="Change k8s config context",callback=set_context,expose_value=False, is_eager=False)
@click.option('-d','--dashboard',is_flag=True,help="Opens up the dashboard for current context",callback=open_dashboard,expose_value=False, is_eager=False)
def cli():

    '''
    
    \b
     _          _   
    | | ___   _| |__   ___  __ _ ___ _   _
    | |/ / | | | '_ \ / _ \/ _` / __| | | |
    |   <| |_| | |_) |  __/ (_| \__ \ |_| |
    |_|\_\\__,_|_.__/ \___|\__,_|___/\__, |
                                      |___/
    \b
    Kubeasy is just an easiest and fastest way to switch between multiple K8's clusters.
    '''



@cli.group()
@click.help_option('-h','--help', help="Show the usage of aks command.")
def aks():

    '''
    \b
    Manages k8s clusters from AKS.

    \b
    You can add new k8s clusters just specifying name of the AKS Cluster,
    Or all the clusters from specific Azure Subscription.

    '''

@aks.command('add', short_help='Add new cluster to kubeasy')
@click.option('-n','--name',required=True,help="Add new kube cluster in kubeasy")
@click.option('-f','--force',required=False,is_flag=True,default=False,help="Forcefully add cluster configuration even if it exists")
@click.help_option('-h','--help', help="Show the usage of add command.")
def add_aks(name,force):
    

    '''
    \b
    Example:
    \b
    # Add all AKS clusters from Azure Subscription.
    kubeasy aks add -n all

    \b
    # Add specific AKS clusters from Azure Subscription.
    kubeasy aks add -n <aksCluster>

    '''
   

    spinner = Halo(text=colorama.Fore.GREEN + 'Logging into Azure using Azure CLI..', spinner='dots',color='yellow')
    spinner.start()

    if not login('azure',spinner):
        spinner.fail(colorama.Fore.RED + 'Azure login failed')
        sys.exit(1)

    spinner.stop()

    spinner = Halo(text=colorama.Fore.GREEN + 'Getting Kubernetes Configuration for {}'.format(name), spinner='dots',color='yellow')
    spinner.start()

    if name == 'all':
                 
        for key in get_K8SList('azure'):
         
             if (not _isExist(key) or (_isExist(key) and force)):
                 
                 addConfig(spinner,'azure',key)
             else:
                 spinner.info(colorama.Fore.GREEN + '\"{}\" is already configured for the Kubeasy, Cheers ! '.format(key))

    elif (not _isExist(name) or (_isExist(name) and force)):
        
        addConfig(spinner,'azure',name)

    else:
        
        spinner.info(colorama.Fore.GREEN + '\"{}\" is already configured for the Kubeasy, Cheers !'.format(name))

    spinner.stop()
    


@cli.group()
@click.help_option('-h','--help', help="Show the usage of gke command.")
def gke():
    
    '''
    \b
    Manages k8s clusters from GKE.

    \b
    You can add new k8s clusters just specifying name of the GKE Cluster

    '''
    


@gke.command('add', short_help='Add new cluster to kubeasy')
@click.option('-n','--name',required=True,help="Add new kube cluster in kubeasy")
@click.option('-f','--force',required=False,is_flag=True,default=False,help="Forcefully add cluster configuration even if it exists")
@click.help_option('-h','--help', help="Show the usage of add command.")
def add_gke(name,force):
    
    '''
    \b
    Example:
    \b
    # Add all GKE clusters .
    kubeasy gke add -n all

    \b
    # Add specific GKE clusters.
    kubeasy gke add -n <gkeCluster>
    '''

    spinner = Halo(text=colorama.Fore.GREEN + 'Logging into Google Cloud using gcloud ..', spinner='dots',color='yellow')
    spinner.start()

    if not login('google',spinner):
        spinner.fail(colorama.Fore.RED + 'Google Cloud login failed')
        sys.exit(1)
    
    spinner.stop()

    spinner = Halo(text=colorama.Fore.GREEN + 'Getting Kubernetes Configuration for {}'.format(name), spinner='dots',color='yellow')
    
    spinner.start()

    if name == 'all':
                 
        for key in get_K8SList('google'):
         
             if (not _isExist(key) or (_isExist(key) and force)):
                 
                 addConfig(spinner,'google',key)
             else:
                 spinner.info(colorama.Fore.GREEN + '\"{}\" is already configured for the Kubeasy, Cheers ! '.format(key))

    elif (not _isExist(name) or (_isExist(name) and force)):
        
        addConfig(spinner,'google',name)

    else:
        
        spinner.info(colorama.Fore.GREEN + '\"{}\" is already configured for the Kubeasy, Cheers !'.format(name))

    spinner.stop()


if __name__ == '__main__':
    cli()