from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings
# 有了这个类 django上传文件就会调用我们自己定义的文件上传方法
# setting里配置项DEFAULT_FILE_STORAGE是指定django文件上传默认的类 我们需要改变指定自己的文件上传类

class FDFSStorage(Storage):
    def __init__(self, client_conf=None, base_url=None):
        if client_conf is None:
            client_conf = settings.FAFS_CLIENT_CONF
        if base_url is None:
            base_url = settings.FAFS_BASE_URL
        self.client_conf = client_conf
        self.base_url = base_url
    """fdfs 文件储存类"""
    def _open(self, name, mode='rb'):
        """打开文件时使用"""
        pass

    # name就是：你选择文件上传的名
    # content 包含上传文内容的file对象
    def _save(self, name, content):
        """保存文件时使用"""
        # 创建一个fdfs clint对象
        client = Fdfs_client(self.client_conf)
        # 上传文件到fdfs系统  返回一个字典
        res = client.upload_by_buffer(content.read())
        """dict {
            'Group name'      : group_name,
            'Remote file_id'  : remote_file_id,
            'Status'          : 'Upload successed.',
            'Local file name' : '',
            'Uploaded size'   : upload_size,
            'Storage IP'      : storage_ip
        }"""
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到fast_dfs失败')
        # 获取返回的文件id 以便保存到数据库里
        file_name = res.get('Remote file_id')
        return file_name

    # 在调用save方法之前会调用exist方法
    # 这个方法会上传文件的名字传过来 如果这个文件名在文件里存在 那么这个文件名不可用
    def exists(self, name):
        """django判断文件名是否可用
        但我们存储在fdfs里  并不是存储在django里所以不用考虑"""
        return False

    def url(self, name):
        """返回访问文件的url路径"""
        return self.base_url + name


