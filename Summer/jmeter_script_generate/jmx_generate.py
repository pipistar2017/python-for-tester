#! ecoding=utf-8
# author: fanxn19000
# date: 2018-02-02
from urllib import request
import json
import os
import random
from datetime import datetime
from xml.dom.minidom import parse
from xml.dom.minidom import Document

# 用于获取swagger中的接口名称,说明和入参
class web_spider():

    def __init__(self):
        self.url = self.get_conf_para()["url"]+"/v2/api-docs"
        self.conf_path = os.getcwd()+"\\conf\\"

    def get_conf_para(self):
        file_path = os.getcwd()+"\\conf\\" + "conf.json"
        conf = open(file_path)
        return json.load(conf)

    def get_web_content(self):
        req = request.Request(self.url)
        resp = request.urlopen(req)
        return resp.read().decode('utf8')

    #获取每个接口的详情--url，说明，参数名称，参数类型等
    def get_para_details(self,para,method):
        para_result = []
        required_para = []
        required_type = []
        required_dic = []
        unrequired_para = []
        unrequired_type = []
        unrequired_dic = []
        dic_num1 = 1
        dic_num2 = 1
        for sub_para in para:
            # 必须参数
            if sub_para["required"] == True:
                required_para.append(sub_para["name"])
                subrequired_dic = []
                # 通过"description"判断是否为字典类型
                if "description" in sub_para.keys():
                    if sub_para["description"].count("：") > 0 and sub_para["description"].count("；") > 0 \
                            and sub_para["type"] == "String":
                        required_type.append("dic" + str(dic_num1))
                        dic_num1 = dic_num1 + 1
                        if "，" in sub_para["description"]:
                            for sub_dic in sub_para["description"].split("，"):
                                subrequired_dic.append(sub_dic[-1])
                        else:
                            for sub_dic in sub_para["description"].split(","):
                                subrequired_dic.append(sub_dic[-1])
                # 如果是字典类型，则取字典列表
                if len(subrequired_dic) > 0:
                    required_dic.append(subrequired_dic[:-1])
                # 否则，取实际的数据类型
                else:
                    if 'format' in sub_para.keys():
                        required_type.append(sub_para['format'])
                    else:
                        required_type.append(sub_para["type"])
            # 非必须参数
            else:
                unrequired_para.append(sub_para["name"])
                subunrequired_dic = []
                if "description" in sub_para.keys():
                    if sub_para["description"].count("：") > 0 and sub_para["description"].count("；") > 0:
                        unrequired_type.append("dic" + str(dic_num2))
                        dic_num2 = dic_num2 + 1
                        if "，" in sub_para["description"]:
                            for sub_dic in sub_para["description"].split("，"):
                                subunrequired_dic.append(sub_dic[-1])
                        else:
                            for sub_dic in sub_para["description"].split(","):
                                subunrequired_dic.append(sub_dic[-1])
                if len(subunrequired_dic) > 0:
                    unrequired_dic.append(subunrequired_dic[:-1])
                else:
                    if 'format' in sub_para.keys():
                        unrequired_type.append(sub_para['format'])
                    else:
                        unrequired_type.append(sub_para["type"])
        para_result.append(required_para)
        para_result.append(required_type)
        para_result.append(required_dic)
        para_result.append(unrequired_para)
        para_result.append(unrequired_type)
        para_result.append(unrequired_dic)
        para_result.append([method])
        return para_result

    # 返回每个项目的每个接口的参数详情和方法类型，以及项目名称对应关系
    def get_API_content(self):

        content = json.loads(self.get_web_content())
        # 用于存储项目名称
        tools_name = {}
        api_detail_dic = {}
        name_con = content["tags"]
        for sub_name_con in name_con:
            if sub_name_con['description'].count('Error') > 0:
                pass
            else:
                tools_name[sub_name_con['name']] = sub_name_con['description']

        con= content["paths"]
        for sub in con.keys():
            apiDic = {}
            if "post" in con[sub]:
                # self.method = 'POST'
                temp = con[sub]["post"]
                if "parameters" in temp:
                    tag_name = temp["tags"][0]
                    url_name = sub + "," + temp["summary"]
                    para_res = self.get_para_details(temp["parameters"],"POST")
                    # apiDic[url_name] = para_res.append([methon_type])
                    apiDic[url_name] = para_res
                    api_detail_dic = self.add_value_to_dic(api_detail_dic,tag_name,apiDic)

            elif "get" in con[sub]:
                # self.method = 'GET'
                temp = con[sub]["get"]
                if "parameters" in temp:
                    tag_name = temp["tags"][0]
                    url_name = sub + "," + temp["summary"]
                    para_res = self.get_para_details(temp["parameters"],"GET")
                    # apiDic[url_name] = para_res.append([methon_type])
                    apiDic[url_name] = para_res
                    api_detail_dic = self.add_value_to_dic(api_detail_dic, tag_name, apiDic)
            else:
                print("无法识别是post还是get方法！生成数据失败！")

        return tools_name,api_detail_dic

    # 用于往项目中添加接口详情
    def add_value_to_dic(self,dic_para,key,value_list):
        value_dic = []
        if key in dic_para.keys():
            sub_value = dic_para[key]
            value_dic.append(value_list)
            value_dic = sub_value + value_dic
            dic_para[key] = value_dic
        else:
            value_dic.append(value_list)
            dic_para[key] = value_dic
        return dic_para

    # 获取全部的参数，用于jmx的用户参数设置
    def get_para_list(self,para_value):
        para_list = {}
        para_list['error_no_0']='0'
        for ssub_para_values in para_value:
            for sub_value in ssub_para_values.values():
                # 检查必传参数，放入字典
                index_len = len(sub_value[0])
                if index_len > 0:
                    dic_index = 0
                    for index in range(index_len):
                        key = sub_value[0][index]
                        if sub_value[1][index].count('dic') > 0:
                            # 如果是字典，取字典数据
                            if not self.check_key_exists(key, para_list):
                                para_list[key] = sub_value[2][dic_index]
                            dic_index = dic_index + 1
                        else:
                            # 如果不是，自动生成
                            if not self.check_key_exists(key, para_list):
                                para_list[key] = self.generate_valid_para(sub_value[1][index], key)
                # 检查非必须参数，存入字典
                index_len = len(sub_value[3])
                if index_len > 0:
                    dic_index = 0
                    for index in range(index_len):
                        key = sub_value[3][index]
                        if sub_value[4][index].count('dic') > 0:
                            # 如果是字典，取字典数据
                            if not self.check_key_exists(key, para_list):
                                para_list[key] = sub_value[5][dic_index]
                            dic_index = dic_index + 1
                        else:
                            # 如果不是，自动生成
                            if not self.check_key_exists(key, para_list):
                                para_list[key] = self.generate_valid_para(sub_value[4][index], key)

        return para_list

    #检查字典中key是否存在
    def check_key_exists(self,key_para,dic_para):
        if key_para in dic_para.keys():
            return True
        else:
            return False

    #生成合法的参数
    def generate_valid_para(self,para_type,para_name):
        date_string_now = datetime.now().strftime("%Y%m%d")
        if para_type.lower() == 'string':
            if para_name.count('month') > 0 :
                return [date_string_now[:6]]
            elif para_name.count('date') > 0 :
                return [date_string_now]
            elif para_name.count('stock_code') > 0 or para_name.count('stockcode') > 0:
                return['600570']
            else:
                return ['test'+str(int(random.random()*1000))]

        elif para_type.count('int') > 0 :
            if para_name.count('page_no') > 0 or para_name.count('pageno') > 0 or para_name.count('pageNo') > 0:
                return [1]
            elif para_name.count('page_size') > 0 or para_name.count('pagesize') > 0 or para_name.count('pageSize') > 0:
                return [10]
            elif para_name.count('month') > 0 :
                return [date_string_now[:6]]
            elif para_name.count('date') > 0 :
                return [date_string_now]
            else:
                return [max(int(random.random()*100),1)]

        elif para_type.count('date') > 0 :
            return [date_string_now]
        else:
            return ['test']

    # 生成不合法的参数
    def generate_invalid_para(self,para_type,para_name):

        date_string_now = datetime.now().strftime("%Y%m%d")

        if para_type.lower() == 'string':
            if para_name.count('month') > 0 :
                return [date_string_now[:5],date_string_now[:4]+"13",date_string_now[:5]+"m"]

            elif para_name.count('date') > 0 :
                return [date_string_now[:6],date_string_now[:6]+"60",date_string_now[:7]+'d']

            else:
                return ['test&*$%'+str(int(random.random()*1000)),self.generate_len_para(50,'string')]

        elif para_type.count('int') > 0 :
            if para_name.count('month') > 0 :
                return [date_string_now[:5],date_string_now[:4]+"13",date_string_now[:5]+"m"]

            elif para_name.count('date') > 0 :
                return [date_string_now[:6],date_string_now[:6]+"60",date_string_now[:7]+'d']

            else:
                return ['invalid' + str(max(int(random.random()*100),1)),self.generate_len_para(50,'int'),'&*$#']

        elif para_type.count('date') > 0 :
            return [date_string_now[:6],date_string_now[:6]+"60",date_string_now[:7]+'d']

        else:
            return ['&&&**##']

    # 生成一定长度的参数的参数
    def generate_len_para(self,length,type):

        seeds = 'abcABCDEFdefghijPQRSTUVklmnopNOWqrstuvwsyzGHIJKLMXYZ'
        res = ''
        if type.lower() == 'string':
            for i in range(length):
                res = res + seeds[min(len(seeds),int(random.random()*len(seeds)))]

        if type.count('int') > 0:
            for i in range(length):
                res = res + str(random.randint(1,9))

        return res

    # 生成jmx的参数部分，最外层标签为collectionProp
    def get_para_jmx(self,para_list):
        # para_list = self.get_para_list()
        path = self.conf_path + "parameter.jmx"
        dom_tree = parse(path)
        dom_root = dom_tree.documentElement
        sub_first = dom_root.getElementsByTagName("elementProp")[0]
        mode_node = sub_first.cloneNode(True)
        dom_root.removeChild(sub_first)
        # 用于标识，是否是第一个节点，如果是需要覆盖，否则新增
        # is_first = True
        for key in para_list:
            value = para_list[key]
            add_index = 1
            for sub_value in value:
                temp_node = mode_node.cloneNode(True)
                sub_nodes = temp_node.childNodes
                # 用于清除空格子节点
                for sub_sub_node in sub_nodes:
                    if sub_sub_node.nodeName != 'stringProp':
                        temp_node.removeChild(sub_sub_node)
                sub_nodes = temp_node.childNodes
                if len(value) > 1:
                    sub_nodes[0].firstChild.data = key + '_' + str(add_index)
                else:
                    sub_nodes[0].firstChild.data = key
                sub_nodes[1].firstChild.data = sub_value
                dom_root.appendChild(temp_node)
                add_index = add_index + 1

        return dom_root

    #用于生成每个接口的模块node
    def generate_http_node(self):
        path = self.conf_path + "httpsampler.jmx"
        dom_tree = parse(path)
        dom_root = dom_tree.documentElement
        control_element = dom_root.getElementsByTagName('GenericController')[0]
        http_out_element = dom_root.getElementsByTagName('hashTree')[0]

        http_element = http_out_element.getElementsByTagName('HTTPSamplerProxy')[0]
        assert_element = http_out_element.getElementsByTagName('hashTree')[0]

        return control_element,http_element,assert_element

    # 生成jmx的http请求部分
    def get_http_jmx(self,interface_list,control_element,http_element,assert_element):

        document = Document()
        dom_tree = document.createElement("hashTree")

        for interface_dic in interface_list:

            used_control_element = control_element.cloneNode(True)
            dom_tree.appendChild(used_control_element)
            sub_dom = document.createElement("hashTree")
            dom_tree.appendChild(sub_dom)

            for interface_url in interface_dic.keys():
                request_url = interface_url[:interface_url.find(',')]
                clean_url = request_url.split('/')[-1]
                clean_des = interface_url[interface_url.find(',')+1:]
                method = interface_dic[interface_url][-1][0]

                used_control_element.setAttribute('testname',clean_url+'--接口功能测试')

                api_content = interface_dic[interface_url]
                para_list = api_content[0] + api_content[3]
                para_type = api_content[1] + api_content[4]

                para_combine_list = []
                for index in range(len(para_list)):
                    if para_type[index].count('dic'):
                        sub_dic_list = []
                        for i in range(len(para_type[index])):
                            sub_dic_list.append(para_list[index]+'=${' \
                                                               + para_list[index] +'_' + str(i) + '}')
                        para_combine_list.append(sub_dic_list.copy())
                    else:
                        para_combine_list.append([para_list[index] + '=${' + para_list[index] + '}'])

                combine_result = self.get_combine_para(para_combine_list,method)

                for combine in combine_result:
                    clone_http_sampler = http_element.cloneNode(True)
                    clone_assert_element = assert_element.cloneNode(True)
                    clone_http_sampler.setAttribute('testname', clean_url+'_'+clean_des)
                    # 参数设置的node
                    http_para_element = clone_http_sampler.getElementsByTagName('elementProp')[0]. \
                            getElementsByTagName('collectionProp')[0].getElementsByTagName('elementProp')[0]. \
                            getElementsByTagName('stringProp')[0]
                    http_para_element.firstChild.data = '{' + combine + '}'
                    #方法和名称的Node
                    method_element = clone_http_sampler.getElementsByTagName('stringProp')[7]
                    name_element = clone_http_sampler.getElementsByTagName('stringProp')[6]
                    method_element.firstChild.data = method
                    name_element.firstChild.data = request_url

                    sub_dom.appendChild(clone_http_sampler)
                    sub_dom.appendChild(clone_assert_element)

        return dom_tree
     # 用于组合入参的组合

    # 参数组合函数
    def get_combine_para(self,para_combine_list,method):
        combine = para_combine_list[0]
        for index in range(1, len(para_combine_list)):
            temp = combine.copy()
            len1 = len(temp)
            len2 = len(para_combine_list[index])
            new_len = 0
            for i in range(len1):
                for inner in range(len2):
                    if new_len >= len1:
                        if method.lower() == 'get':
                            combine.append(temp[i] + '&' + para_combine_list[index][inner])
                        else:
                            combine.append(temp[i] + ',' + para_combine_list[index][inner])
                    else:
                        if method.lower() == 'get':
                            combine[new_len] = temp[i] + '&' + para_combine_list[index][inner]
                        else:
                            combine[new_len] = temp[i] + ',' + para_combine_list[index][inner]
                    new_len = new_len + 1
        return combine

    # 生成jmx
    def generate_jmx(self,para_node,http_node,jmx_name):

        path = self.conf_path + "mode.jmx"
        dom_tree = parse(path).documentElement
        jmx_path = os.getcwd() + "\\jmx\\"
        # 设置项目参数
        thread_element = dom_tree.getElementsByTagName("ThreadGroup")[0]
        one_control_element = dom_tree.getElementsByTagName("OnceOnlyController")[0]
        thread_element.setAttribute("testname",jmx_name+"--接口测试")
        one_control_element.setAttribute("testname",jmx_name+"--业务逻辑测试")
        # 设置用户参数
        argument_element = dom_tree.getElementsByTagName("Arguments")[0]
        old_child = argument_element.childNodes
        for sub_child in old_child:
            argument_element.removeChild(sub_child)
        argument_element.appendChild(para_node)

        # 请求部分
        flag_element = dom_tree.getElementsByTagName("TestSampler")[0]
        elment_test = dom_tree.getElementsByTagName("hashTree")[2]
        elment_test.insertBefore(http_node,flag_element)
        elment_test.removeChild(flag_element)

        dom_str = dom_tree.toprettyxml(indent='\t', encoding='UTF-8')
        with open(jmx_path+jmx_name + '.jmx','wb+') as f :
            f.write(dom_str)


jmx_generate = web_spider()
name,des = jmx_generate.get_API_content()
control_element,http_element,assert_element = jmx_generate.generate_http_node()

for proj_name in des.keys():
    # 获得每个接口的参数序列
    para_list = jmx_generate.get_para_list(des[proj_name])
    para_node = jmx_generate.get_para_jmx(para_list)
    http_node =  jmx_generate.get_http_jmx(des[proj_name],control_element,http_element,assert_element)
    jmx_name = name[proj_name]
    jmx_generate.generate_jmx(para_node, http_node,jmx_name)





