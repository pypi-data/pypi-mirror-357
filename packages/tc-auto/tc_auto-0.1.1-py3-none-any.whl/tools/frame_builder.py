import os
from tools.components.file_utils import search_files, create_product_base_class, create_init_file, create_function_class


def build(product, sdk_root):
    lib_root = os.path.join(os.path.dirname(os.getcwd()), 'lib')
    sdk_root = os.path.join(sdk_root, 'tencentcloud')
    if not os.path.exists(lib_root):
        os.makedirs(lib_root)
        create_init_file(lib_root)
    # 产品对应的sdk路径
    product_sdk_root = os.path.join(sdk_root, product)
    product_lib_root = os.path.join(lib_root, product)
    clients_path = search_files(file_path=product_sdk_root, file_suffix='_client.py', max_depths=3)
    client_infos = []
    all_func_names = []
    same_func_names = []

    for client_path in clients_path:
        # 去掉根路径并去掉.py后拼接包路径
        client = 'tencentcloud%s' % ('.'.join(client_path.split(sdk_root)[1].split(os.sep))).replace('.py', '')
        client_name = client.split('.')[-1]
        client_root = client.replace('.%s' % client_name, '')
        mod = __import__(client, fromlist=[client_name])
        client_class = None
        for x in mod.__dict__.keys():
            if "Client" in x and x != 'AbstractClient':
                client_class = getattr(mod, x)
                break

        if not client_class:
            raise Exception("包中不包含client")
        func_names = [func_name for func_name in list(client_class.__dict__.keys()) if not func_name.startswith('_')]
        docs = {}
        for func_name in func_names:
            func_doc = getattr(client_class, func_name).__doc__.split(':params')
            docs[func_name] = func_doc
            if func_name in all_func_names:
                same_func_names.append(func_name)
            else:
                all_func_names.append(func_name)

        client_infos.append({
            'client_file': clients_path,
            'client_class': client_class.__name__,
            'version': client_root.split('.')[-1],
            'client_root': client_root,
            'func_names': func_names,
            'docs': docs
        })

    # 生成产品根目录
    product_lib_root = os.path.join(lib_root, product)
    if not os.path.exists(product_lib_root):
        os.makedirs(product_lib_root)
    create_init_file(product_lib_root)

    # 生成基于Base的业务类
    create_product_base_class(product=product, product_root=product_lib_root)

    # 生成产品函数
    create_function_class(product=product, product_root=product_lib_root, clients_info=client_infos)


if __name__ == '__main__':
    build(product='tke', sdk_root='E:\\Code\\tencentcloud-sdk-python')
