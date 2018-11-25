import os

def rel2fullpath(relpath):
    path0 = os.path.dirname(os.path.abspath(__file__))
    fullpath = os.path.join(path0[:path0.find('ungdomsserien')],'ungdomsserien',relpath)
    return fullpath


def getexample(filename='Example.xml'):
    path = rel2fullpath('data')
    xmlfile = os.path.join(path,filename)
    return xmlfile