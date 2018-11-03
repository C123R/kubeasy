import unittest
from core.configurator import _isExist,get_kubeasyList,set_k8s_context,get_current_context

class Testing(unittest.TestCase):


    def test_isExist(self):

        '''
        Test _isExist function to check Cluster existance in the mock kubeconfig tests/.kube/config

        '''

        a = _isExist('apple')

        self.assertEqual(a, True)

    def test_get_kubeasyList(self):

        '''
        Test get_kubeasyList function against the mock kubeconfig tests/.kube/config

        '''


        a = get_kubeasyList(output=False)
        b = {'** apple': 'https://localhost:6441','   banana': 'https://localhost:6442','   mango': 'https://localhost:6443'}
        self.assertEqual(a, b)

    def test_kube_context(self):

        '''
        Test funcntions related to k8s context using the mock kubeconfig tests/.kube/config

        '''

        set_k8s_context('apple')
        a = get_current_context()
        self.assertEqual('apple', a)


if __name__ == '__main__':
    unittest.main()