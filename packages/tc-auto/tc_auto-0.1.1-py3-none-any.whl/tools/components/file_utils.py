import importlib
import os.path

from tools.components.string_utils import camel_to_snake
from tools.config.logger import logger


def search_files(file_path, file_suffix, max_depths=1):
    """
    :param file_path:
    :param file_suffix:
    :param max_depths:
    :return:
    """
    if not os.path.isdir(file_path) or max_depths == 0:
        return []
    result = []
    cur_depths_objs = [os.path.join(file_path, p) for p in os.listdir(file_path)]
    for obj in cur_depths_objs:
        if os.path.isdir(obj):
            result.extend(search_files(file_path=obj, file_suffix=file_suffix, max_depths=max_depths - 1))
        else:
            if obj.endswith(file_suffix):
                result.append(obj)
                logger.info("查到指定后缀文件:%s" % obj)
    return result


def create_init_file(file_path):
    """
    :param file_path:
    :return:
    """
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    init_file = os.path.join(file_path, '__init__.py')
    if os.path.exists(init_file):
        os.remove(init_file)
        logger.info("删除已存在的__init__.py:%s" % init_file)
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write("# -*- coding:utf-8 -*-\n")
        f.write("\"\"\"\n")
        f.write("自动生成的文件\n")
        f.write("\"\"\"\n")
        logger.info("创建__init__.py文件成功:%s" % init_file)


def create_product_base_class(product, product_root):
    """
    :param product:
    :param product_root:
    :return:
    """
    data = f"""\"\"\"{product}
\"\"\"
from lib.{product}.{product}_base import {product.title()}Base


class {product.title()}({product.title()}Base):
    \"\"\"{product}业务类\"\"\"
    pass
    
    
{product.upper()} = {product.title()}()
"""
    base_file_path = os.path.join(product_root, '%s.py' % product.lower())
    if os.path.exists(base_file_path):
        os.remove(base_file_path)
        logger.info("删除已存在的class文件:%s" % base_file_path)
    with open(base_file_path, 'w', encoding='utf-8') as f:
        f.write(data)


def create_function_class(product, product_root, clients_info):
    versions = ', '.join(['"%s-%s-%s"' %
                          (x['version'][1:5], x['version'][5:7], x['version'][7:9]) for x in clients_info])

    import_content = f"""\"\"\"{product}基础接口封装。 注:自动生成\"\"\"
from lib.models import Model
from lib.utils import retry_with_conditions
"""

    # class_content
    class_content = f"""
    
class {product.title()}Base(Model):
    def init_client_models(self, **kwargs):
        self.business = "{product}"
        self.versions = [{versions}]
"""

    functions_content = ""
    for item in clients_info:
        client_name = '%s_%s' % (item['client_class'], item['version'])
        import_content += f"""from tencentcloud.{product}.{item['version']}.{product}_client import {item['client_class']} as {client_name}
from tencentcloud.{product}.{item['version']} import models as model_{item['version']}
"""
        class_content += f"""        self.client_{item['version']} = {client_name}(**kwargs)
        self.model_{item['version']} = model_{item['version']}
"""

        for func in item['func_names']:
            request_name = '%sRequest' % func
            mod = importlib.import_module('%s.models' % item['client_root'])
            if not hasattr(mod, request_name):
                logger.error("未找到函数%s的请求参数模型%s,跳过函数的自动生成" % (func, request_name))
                continue
            func_class = getattr(__import__('%s.models' % item['client_root'], fromlist=[request_name]), request_name)
            func_doc = getattr(func_class, '__init__').__doc__
            request_model = getattr(mod, request_name)()
            request_params = [x.lstrip('_') for x in request_model.__dict__.keys()]
            for param in request_params:
                func_doc = func_doc.replace('_%s' % param, camel_to_snake(param))
                func_doc = func_doc.replace(param, camel_to_snake(param))
            func_params = ', '.join(['%s=None' % camel_to_snake(x) for x in request_params])
            func_descriptions = ''.join(item['docs'][func]).split('\n')[0]+ ''.join(func_doc)
            if len(request_params) > 0:
                func_content = f"""
    @retry_with_conditions(3, 10)
    def {camel_to_snake(func)}(self, {func_params}, **kwargs):
        \"\"\"{func_descriptions}
        \"\"\"
        req = self.model_{item['version']}.{request_name}()
"""
            else:
                func_content = f"""
    def {camel_to_snake(func)}(self, **kwargs):
        \"\"\"{''.join(item['docs'][func])}
        \"\"\"
        req = self.model_{item['version']}.{request_name}()
"""
            for param in request_params:
                func_content += f"""        req.{param} = {camel_to_snake(param)}
"""
            func_content += f"""        if kwargs:
            req = self.convert_request(req, **kwargs)
        response = self.client_{item['version']}.{func}(req)
        return response
"""
            functions_content += func_content

    function_file_path = os.path.join(product_root, '%s_base.py' % product.lower())
    if os.path.exists(function_file_path):
        os.remove(function_file_path)
        logger.info("删除已存在的class文件:%s" % function_file_path)
    with open(function_file_path, 'w', encoding='utf-8') as f:
        f.write(import_content)
        f.write(class_content)
        f.write(functions_content)
