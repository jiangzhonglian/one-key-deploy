import subprocess as subp
import json
import psutil
import shutil
import os
from os import path
import jinja2

DOCKER_NGINX_LOG  = '/var/log/nginx'
DOCKER_NGINX_CONF = '/etc/nginx/conf.d'
DOCKER_NGINX_RSRC = '/usr/share/nginx/html'
DOCKER_NGINX_SSL  = '/etc/nginx/ssl'

def d(name):
    return path.join(path.dirname(__file__), name)

def get_docker_containers():
    r = subp.Popen(
        'docker ps -a --format "{{.ID}}----{{.Ports}}----{{.Status}}----{{.Names}}"',
        stdout=subp.PIPE,
        stderr=subp.PIPE,
        shell=True,
    ).communicate()[0].decode('utf-8')
    res = []
    for line in r.split('\n'):
        tmp = line.split('----')
        if len(tmp) != 4: continue
        res.append({
            'ID': tmp[0],
            'Ports': tmp[1],
            'Status': tmp[2],
            'Names': tmp[3],
        })
    return res

def kill_port(port):
    netstats = psutil.net_connections('tcp')
    for n in netstats:
        if  n.laddr.port == port and \
            n.status == 'LISTEN':
            os.kill(n.pid, 9)
            print(f'KILL PID: {n.pid}')
    containers = get_docker_containers()
    for c in containers:
        if f':{port}->' in c['Ports']:
            subp.Popen(f'docker rm -f {c["ID"]}', shell=True)
            print(f'KILL CONTAINER: {c["ID"]}')

def mkdirs_safe(dir):
    if not path.exists(dir):
        os.makedirs(dir)
        
def rmtree_safe(dir):
    if path.exists(dir):
        shutil.rmtree(dir)

def deploy_doc():
    config = json.loads(
        open(d('config.json'), encoding='utf-8').read())
    # 按照首字母排序文档
    config['docs'].sort(key=lambda x: x.get('name', ''))
    # 按照类别分组文档
    config['cates'] = [    
        {
            'name': c,
            'docs': [d for d in config['docs'] if d['cate'] == c],
        } for c in config['cates']
    ]
    
    # 释放配置文件
    data_dir = config['dataDir']
    mkdirs_safe(data_dir)
    conf_dir = path.join(data_dir, 'conf')
    mkdirs_safe(conf_dir)
    rsrc_dir = path.join(data_dir, 'html')
    mkdirs_safe(rsrc_dir)
    log_dir = path.join(data_dir, 'log')
    mkdirs_safe(log_dir)
    ssl_dir = config['sslDir']
    mkdirs_safe(ssl_dir)
    
    asset_dir = path.join(rsrc_dir, 'asset')
    rmtree_safe(asset_dir)
    shutil.copytree(d('asset/site_asset'), asset_dir)
    shutil.copy(
        d('asset/conf/' + config['conf'] + '.conf'),
        path.join(conf_dir, 'default.conf'),
    )
    index_tmpl = open(d('asset/index.j2'), encoding='utf-8').read()
    index = jinja2.Template(index_tmpl).render(**config)
    open(path.join(rsrc_dir, 'index.html'), 'w', encoding='utf-8').write(index)
    
    # 下载 Github 仓库
    for doc in config['docs']:
        if 'name' not in doc or \
           'repo' not in doc:
           continue
        
        name, repo = doc['name'], doc['repo']
        print(f'name: {name}, repo: {repo}')
        
        doc_dir = path.join(rsrc_dir, name)
        if config['clean']:
            rmtree_safe(doc_dir)
        if not path.exists(doc_dir):
            os.chdir(rsrc_dir)
            subp.Popen(
                f'git clone {repo} {name} -b master', 
                shell=True,
            ).communicate()
            if not path.exists(doc_dir): continue
        os.chdir(doc_dir)
        subp.Popen(f'git pull', shell=True).communicate()
    
    # 启动 Nginx
    name, port, sec_port = config['name'], config['port'], config['secPort']
    print(f'name: {name}, repo: nginx, port: {port}, secPort: {sec_port}')
    kill_port(port)
    kill_port(sec_port)
    subp.Popen(f'docker rm -f {name}', shell=True).communicate()
    subp.Popen(f'docker pull nginx', shell=True).communicate()
    args = '\x20'.join([
        # 后台运行
        'docker run -tid',
        # 设置容器名称
        f'--name {name}',
        # 绑定端口
        f'-p {port}:80',
        f'-p {sec_port}:443',
        # 绑定配置、资源和日志目录
        f'-v "{conf_dir}:{DOCKER_NGINX_CONF}"',
        f'-v "{rsrc_dir}:{DOCKER_NGINX_RSRC}"',
        f'-v "{log_dir}:{DOCKER_NGINX_LOG}"',
        f'-v "{ssl_dir}:{DOCKER_NGINX_SSL}"',
        # 镜像名称
        'nginx',
    ])
    subp.Popen(args, shell=True).communicate()
    
def main():
    deploy_doc()
    
if __name__ == '__main__': main()