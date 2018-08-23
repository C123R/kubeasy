#!/usr/bin/env python
import click
import sys
import os
import time
import shlex
import socket
import colorama
from halo import Halo
from subprocess import Popen, PIPE, check_output
from commands.aksCommands import get_cmd, get_config_cmd
from commands.configurator import azure_login, get_AKSList, addConfig, get_kubeasyList, get_dashboard, isExist, set_k8s_context

import logging
logging.basicConfig(format='%(levelname)s:kubeasy  %(message)s', level=logging.DEBUG)



def get_list(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    get_kubeasyList(print)
    ctx.exit()

def set_context(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    set_k8s_context(value)
    ctx.exit()

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Kubeasy Version 0.1')
    ctx.exit()


@click.group()
@click.help_option('-h','--help', help="Show the usage of kubeasy.")
@click.option('-v','--version',help="Show the version of kubeasy", is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('-l','--list',is_flag=True,help="List existing clusters in kubeasy.",callback=get_list,expose_value=False, is_eager=False)
@click.option('-c','--context',help="Change k8s config context",callback=set_context,expose_value=False, is_eager=False)
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
def addAks(name,force):
    

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

    if not azure_login(spinner):
        print('Azure login failed')

    spinner.stop()

    spinner = Halo(text=colorama.Fore.GREEN + 'Getting Kubernetes Configuration for {}'.format(name), spinner='dots',color='yellow')
    spinner.start()

    if name == 'all':
    
         for key in get_AKSList():
         
             
             if (not isExist(key) or (isExist(key) and force)):
                 
                 addConfig(spinner,key)
             else:
                 spinner.info(colorama.Fore.GREEN + '\"{}\" is already configured for the Kubeasy, Cheers ! '.format(key))

    elif (not isExist(name) or (isExist(name) and force)):
        
        addConfig(spinner,name)

    else:
        
        spinner.info(colorama.Fore.GREEN + '\"{}\" is already configured for the Kubeasy, Cheers !'.format(name))

    spinner.stop()
    


@cli.group()
@click.help_option('-h','--help', help="Show the usage of ext command.")
def ext():
    
    '''
    \b
    Manages external k8s clusters.
    
    \b
    You can add new k8s clusters just specifying the path of the K8s Cluster configuration. 
    '''


@ext.command('add', short_help='Add new cluster to kubeasy')
@click.help_option('-h','--help', help="Show the usage of add command.")
@click.option('-f','--file',required=True, help="Add new kube cluster in kubeasy")
def addExt(file):
    
    '''
    \b
    Example:
    \b
    # Add external K8s clusters using kube config.

    kubeasy aks add -f <path for kubeConfig>
 
    '''


@cli.group()
@click.help_option('-h','--help', help="Show the usage of dash command.")
@click.option('-n','--name',required=True,help="Add new kube cluster in kubeasy")
def dash(name):
    
    '''

    Opens up the dashboard for the specied cluster

    '''

    get_dashboard(name)


if __name__ == '__main__':
    cli()