from redis import StrictRedis
# 当连接本机时 不需要加ip 和端口

def main():
    try:
        # 创建StrictRedis对象，连接数据库
        sr = StrictRedis()
        # 添加一个key 为 name value 为 itheima
        res = sr.set('name', 'itheima')
        # 返回为True则设置成功
        print(res)
        # 如果取不到值就返回null
        res1 = sr.get("name")
        print(res1)
        # 删除name及值  可同时删除多个  并返回删除的个数
        sr.delete('name')
        # 获取所有键  阐述pattern默认为* 返回所有
        res = sr.keys()
        print(res)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()

