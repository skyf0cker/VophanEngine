import math
import re
import time
import matplotlib.pyplot as plt
import jieba
import numpy as np
from bs4 import BeautifulSoup


class TextExtractor:
    """
    基于文本密度的正文提取方法
    """
    def __init__(self, html, path):
        self.stopwords_path = path
        self.html = html
        self.raw_density = []
        self.factor = 0.03
        self.smoothed_density = []
        self.lines_list = []
        self.text = self.Extract()
        self.article_flag = self._classify()

    def _clean_text(self):
        """
        清理原始数据
        :return:
        """
        reg_0 = r'<script.*?>[\s\S]*?</script>'
        reg_1 = r'<style.*?>[\s\S]*?</style>'
        reg_8 = r'<!--.*?>'
        reg_2 = r'<img.*?>'
        h = re.sub(reg_0, '', self.html)
        h = re.sub(reg_1, '', h)
        h = re.sub(reg_8, '', h)
        h = re.sub(reg_2, '', h)

        self.html = h

    def _get_words_num(self, html):
        reg = r'[^\x00-\xff]'
        char_list = re.findall(reg, html)
        return len(char_list)

    def _get_link_num(self, html):
        reg = r'(src|href)="(.*?)"'
        link_list = re.findall(reg, html)
        links = "".join([i[1] for i in link_list])
        return len(links)

    def _get_tag_num(self, html):
        reg = r'<.*?>'
        tag_list = re.findall(reg, html)
        return len(tag_list)

    def _get_sentence_num(self, html):
        reg = r'[。；！？\?]'
        sen_list = re.findall(reg, html)
        return len(sen_list)

    def _get_stopwords(self):
        with open(self.stopwords_path, encoding='utf-8') as stp:
            self.stp_list = [word.replace('\n', '') for word in stp.readlines()]

    def _get_stop_words_num(self, html):

        reg = r'[^\x00-\xff]'
        char_list = re.findall(reg, html)
        txt = "".join(char_list)
        words_list = jieba.cut(txt, cut_all=True)
        stop_word_list = list(set(self.stp_list) & set(words_list))
        return len(stop_word_list)

    def _get_denisity(self):
        """
        获得文本密度
        :return:
        """
        lines_list = self.html.split("\n")
        self.lines_list = lines_list
        all_sentences = self._get_sentence_num(self.html)
        all_stops = self._get_stop_words_num(self.html)
        density_list = []
        for line in lines_list:
            words = self._get_words_num(line)
            links = self._get_link_num(line)
            tags = self._get_tag_num(line)
            sentences = self._get_sentence_num(line)
            stopwords = self._get_stop_words_num(line)

            if words == 0:
                density = math.log(1/(tags+1))
            else:
                if links == 0:
                    links = 1
                check_point = words-links
                if check_point <= 0:
                    check_point = 1
                if links == 0:
                    links = 1
                if all_sentences == 0:
                    all_sentences = 1
                if all_stops == 0:
                    all_stops = 1
                density = math.log(check_point/links)\
                          *((sentences/all_sentences)+1)\
                          *((stopwords/all_stops)+1)\
                          *abs(math.log((words+1)/(tags+1)))

            density_list.append(density)
        self.raw_density = density_list


    def _gauss_smooth(self):
        """
        对文本密度进行高斯平滑
        :return:
        """
        smoothed_density = []
        for index, value in enumerate(self.raw_density):
            if index - 2 <= 0 or len(self.raw_density) - index <= 2:
                smoothed_density.append(value)
                continue
            else:
                density = 0
                for i in range(5):
                    j = i - 2
                    density += self._gauss_kernel(j)*self.raw_density[index+j]
                smoothed_density.append(density)
        self.smoothed_density = smoothed_density

        # plt.plot(self.smoothed_density)
        # plt.show()

    def _gauss_kernel(self, j):
        """
        高斯核的实现
        :param j:
        :return:
        """
        const_value = 0

        for i in range(5):
            m = i-2
            const_value += math.exp(-(m**2)/2)

        result = math.exp(-(j**2)/2)/const_value
        return result

    def _extract(self):
        """
        提取正文
        :return:
        """
        select_list = []
        index_list = []
        for index, value in enumerate(self.smoothed_density):
            if value > 0:
                index_list.append(index)
            else:
                select_list.append(index_list)
                index_list = []
                continue
        if len(select_list) == 0:
            return []
        # index_list = []
        # for i in select_list:
        #     index_list.extend(i)
        # return index_list
        max_distance = len(self.lines_list)/self.factor

        not_none_list = []
        for sele in select_list:
            if len(sele) != 0:
                not_none_list.append(sele)

        index_list = []

        for i in range(len(not_none_list)-1):
            distance = not_none_list[i+1][-1] - not_none_list[i][-1]
            if distance < max_distance:
                index_list.extend(not_none_list[i])
                index_list.extend(not_none_list[i+1])

        if len(index_list) == 0:
            index_list = select_list[np.argmax([len(i) for i in select_list])]
            return index_list
        else:
            min_index = min(index_list)
            max_index = max(index_list)
            return range(min_index, max_index)

        # return select_list[np.argmax([len(i) for i in select_list])]

    def _classify(self):
        """
        导航页与文章页的算法实现
        :return:
        """
        reg_p1 = "<a.*?>"
        reg_p2 = "<p.*?>"
        a_list = re.findall(reg_p1, self.html)
        return (math.log((len(a_list)+1)/(len(self.text)+1))) < 0

    def Extract(self):
        """
        开始提取内容
        :return:
        """
        self._get_stopwords()
        self._clean_text()
        self._get_denisity()
        self._gauss_smooth()
        indexs = self._extract()
        result = ""

        re_time = "\d{4}/.\d{2}/.\d{2}"
        re_title = "<title.*?>(.*?)</title>"
        time_finder = re.compile(re_time)
        title_finder = re.compile(re_title)
        try:
            self.time = time_finder.findall(self.html)[0]
            # self.time = re.findall(self.html, re_time)[0]
        except:
            self.time = ""

        try:
            self.title = title_finder.findall(self.html)[0]
            # self.title = re.findall(self.html, re_title)[0]
        except:
            self.title = ""

        for i in indexs:
            result += self.lines_list[i]

        soup = BeautifulSoup(result, "html.parser")
        return soup.text

if __name__ == "__main__":

    with open("./test.html", "r", encoding="utf-8") as r:
        html = r.read()
    t = TextExtractor(html, "./stopword.txt")
    print(t.text)
    print(t.article_flag)