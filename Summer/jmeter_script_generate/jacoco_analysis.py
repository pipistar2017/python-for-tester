# ecoding = utf-8
from bs4 import BeautifulSoup

class html_analysis():

    def __is_valid_href(self, href):
        if href.count("..") > 0 or href.count("index.source") > 0 or \
                        href.count('sessions.html') > 0 or href == "index.html" or href.count("html") == 0:
            return False
        else:
            return True

    # 获得类方法路径
    def __get_html_contents(self, path):
        path_list = []
        # 第一次输入的是一个单路径，需要处理下
        if isinstance(path, str):
            path_list.append(path)
        else:
            path_list = path

        result_path = []
        is_end = False
        for sub_path in path_list:
            with open(sub_path + "\\index.html") as dom_html:
                # dom_html = open(sub_path + "\\index.html")
                html_content = BeautifulSoup(dom_html, 'html5lib')
                dom_html.close()
                a_element = html_content.find_all('a')

                for a in a_element:
                    href = a['href']
                    if self.__is_valid_href(href):
                        if href.count('index') > 0:
                            result_path.append(sub_path + "\\" + href[:href.find('index') - 1])
                        else:
                            is_end = True
                            result_path.append(sub_path + "\\" + href)
        if is_end:
            return result_path
        else:
            return self.__get_html_contents(result_path)

    def __is_satisfied_coverage(self,real_level,level):
        if real_level.lower() == "n/a":
            return False
        else:
            coverage = int(real_level[:-1])
            if coverage > level:
                return False
            else:
                return True

    def __get_coverage_result(self, html_file,level):
        result_dic = {}
        result_coverage = []
        with  open(html_file) as dom_html:
            html_content = BeautifulSoup(dom_html, 'html5lib')
            body_content = html_content.find("tbody").find_all('tr')
            for sub_body in body_content:
                td_list = sub_body.find_all('td')
                # method_name  instruction_coverage branch_coverage
                if self.__is_satisfied_coverage(td_list[4].text,level):
                    result_coverage.append([td_list[0].text,td_list[2].text,td_list[4].text])

            class_div = html_content.find("div").find_all('a')
            class_path = class_div[2].text + "/" + class_div[3].text + "/" + html_content.find("h1").text
            if len(result_coverage) > 0:
                result_dic[class_path] = result_coverage
        return result_dic

    def get_coverage_result(self,path,level):
        result_list = []
        html_list = self.__get_html_contents(path)
        for sub_list in html_list:
            temp_dic = self.__get_coverage_result(sub_list,level)
            if len(temp_dic) > 0:
                for key in temp_dic.keys():
                    for des in temp_dic[key]:
                        method_name = key+des[0]
                        real_level = des[2]
                        if self.__is_satisfied_coverage(real_level,level):
                            result_list.append(method_name+"---分支覆盖率为："+real_level)
        return result_list

if __name__ == '__main__':
    test = html_analysis()
    result = test.get_coverage_result('C:\\Users\\hspcadmin\\Desktop\\ifs-dav_jacoco_HTML_Report',50)
    for res in result:
        print(res)