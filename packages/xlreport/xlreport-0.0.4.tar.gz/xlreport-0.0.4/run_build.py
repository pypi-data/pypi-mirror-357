import subprocess as subp
import sys
import pvhelper as pv

dr = pv.get_dirname(__file__)
# print('cd "/home/tom/pyenv/bin/python" ')
# print(dr)
cmd = "/home/tom/pyenv/bin/python -m build"
if sys.platform.startswith('win'):
    cmd = "py -m build"

msg, err = subp.Popen(cmd, shell=True, cwd=dr, stdout=subp.PIPE, stderr=subp.PIPE).communicate()

print(str(msg.decode('ascii', 'ignore')))
print(str(err))


# /home/tom/pyenv/bin/python -m twine upload --repository pypi dist/*