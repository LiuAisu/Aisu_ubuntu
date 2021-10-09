from rediscluster import RedisCluster


def main():
    try:
        # 构建所有节点 redis会使用crc16算法 将键和值写到某个节点上
        startup_nodes = [
            {'host': '192.168.106.128', 'port':'7000'},
            {'host': '192.168.106.128', 'port': '7001'},
            {'host': '192.168.106.128', 'port': '7002'},
        ]
        # 构建RedisCluster对象
        src = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
        result = src.set('k2', 'itlo')
        print(result)
        k2 = src.get('k2')
        print(k2)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
