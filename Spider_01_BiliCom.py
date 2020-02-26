import time
import requests
from multiprocessing.dummy import Pool as ThreadPool
import json
import pymysql
import fakerHeaders
import Spider_02_BiliUsrInfo



def divide(thread_i_di):
    """
    todo : 线程划分任务
    :param thread_i_di:
    :return:
    """
    for j in range(0, total//thread):
        #print("j:{}, i:{}. ".format(j, i+1))
        pageNumber = j*thread + (thread_i_di + 1)
        commitUrl = "https://api.bilibili.com/x/v2/reply?&pn=" + str(pageNumber) + "&type=1&oid=" + str(vidoId)
        run(commitUrl)
        print("sprider has run {}.".format(pageNumber))


def run(url):
    """
    todo : 评论爬虫入口
    :param url:
    :return:
    """
    try:
        #print(url)
        hideHeader = fakerHeaders.getFakerHeaders()
        head = {'User-Agent': hideHeader}
        resp = requests.get(url, headers = head,   timeout=10)
        time.sleep(0.5)  # 延迟，避免太快 ip 被封
        #print(resp.status_code)

        if ( resp.status_code == 200 ):
            parserHtml(resp.text)
            print("run finsh:",url)
            return True
        else:
            print("none, try again.")
            run(url)
            return url
    except:
        print("error, try again.Retry URL:",url)
        run(url)
        return url


# 解析html内容
def parserHtml(textHtml):
    '''
    todo ：利用json解析html text 文本内容
    parameter value ：html 内容
    return ：
    '''

    try:
        commentDetailData = json.loads(textHtml)
        #print(s)
    except:
        #pageGetWrong.append(pageNumber)
        print('error')

    commentlist = []

    try:
        # 切片遍历 得到信息
        for i in range(20):
            comment = commentDetailData['data']['replies'][i]
            blist = []

            # personal details
            userName = comment['member']['uname']
            userSign = comment['member']['sign']
            userSex = comment['member']['sex']
            userMid = comment['member']['mid']
            userLeverl = comment['member']['level_info']['current_level']


            # Python time strftime() 函数接收以时间元组，并返回以可读字符串表示的当地时间，格式由参数format决定。
            # Python time localtime() 函数类似gmtime()，作用是格式化时间戳为本地的时间
            commentCtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment['ctime']))
            commentContent = comment['content']['message']
            commentPlat = comment['content']['plat']  # palt － 机型－  1 未知 2 安卓 3 ios
            commentLikes = comment['like']
            commentRcounts = comment['rcount']
            #print(userName, userSign, userSex, userMid, userLeverl, commentCtime, commentContent, commentPlat, commentLikes, commentRcounts)

            insertIntoDataBase(userName, userSign, userSex, userMid, userLeverl, commentCtime, commentContent, commentPlat, commentLikes, commentRcounts)


            blist.append(userName)
            blist.append(userSign)
            blist.append(userSex)
            blist.append(userMid)
            blist.append(userLeverl)

            blist.append(commentCtime)
            blist.append(commentContent)
            blist.append(commentPlat)
            blist.append(commentLikes)
            blist.append(commentRcounts)
            #print(userName, userSign, userSex, userMid, userLeverl, commentCtime, commentContent, commentPlat, commentLikes, commentRcounts)

            commentlist.append(blist)

        #print("切割内容：" + str(commentlist[:1]))


    except:
        pass







def insertIntoDataBase(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10):
    """
    todo : 插入数据库， 并这个函数中调用用户信息爬虫
    :param s1:
    :param s2:
    :param s3:
    :param s4:  用户 mid
    :param s5:
    :param s6:
    :param s7:
    :param s8:
    :param s9:
    :param s10:
    :return:
    """
    #print("run in insert into DB.")


    # 打开数据库连接
    db = pymysql.connect(host = "localhost", port = 3306, user = "root", password = "123456", database = comDataBaseName, charset='utf8mb4')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 插入语句
    sql = "INSERT INTO "+ comTableName +"(uname, sign, sex, mid, current_level, ctime, message, plat, likehah, rcount) VALUES " \
          "('%s', '%s',  '%s',  %s,  %s, '%s', '%s',  %s,  '%s',  %s)" % (str(s1), str(s2), str(s3), int(s4), int(s5), str(s6), str(s7), int(s8), str(s9), int(s10) )
    #print(sql)
    try:
        # 执行sql语句
        #print("prefer execute sql.  ")
        #print(sql)
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        print("worng in insert")
        # 如果发生错误则回滚
        db.rollback()
        db.close()
    # 关闭数据库连接
    db.close()

    # 因为评论人可能不知评论一次，所以需要去重
    if(str(checkMid(s4)) != "存在" ):
        #print("bu cun zai ,zhengzaizhuaqv")

        try:
            print("正在抓取用户信息， s4 / mid", s4)
            Spider_02_BiliUsrInfo.getUsrInfoMainSpider(s4)
        except:
            print("用户信息爬虫有误，正在尝试再次获取，mid:", s4)
            Spider_02_BiliUsrInfo.getUsrInfoMainSpider(s4)





def checkMid(mid):
    """
    todo : 检查用户信息表中，用户信息重复情况
    :param mid:
    :return:
    """
    db = pymysql.connect(host = "localhost", port = 3306, user = "root", password = "123456", database = comDataBaseName, charset='utf8mb4')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL query语句
    sql = "select * from BiliUsrInfo where mid like '{}'".format(mid)

    #print(sql)
    try:
        # 执行sql语句

        cursor.execute(sql)
        desc = cursor.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in
                     cursor.fetchall()]  # 列表表达式把数据组装起来        # 提交到数据库执行


        if(str(data_dict) != "[]"):
            #print("存在",str(data_dict))
            return "存在"

        db.commit()
    except:
        print("worng in query mid. ")
        # 如果发生错误则回滚
        db.rollback()
        db.close()


if __name__ == '__main__':


    time0 = time.time()

    # 抓取页面数量
    total = 6921

    # 抓取视频id
    vidoId = 62026826  # 敬汉卿 维权视频 id，

    #vidoId = 37947862   # 测试用 视频 id

    # 评论爬虫 数据库名
    comDataBaseName = "GraduationProject"
    # 评论爬虫 表名
    comTableName = "BiliComment"


    # 线程
    thread = 6

    thread_i = [j
         for j in range(0, thread)
         ]

    pool = ThreadPool(thread)
    pool.map(divide, thread_i)

    pool.close()
    pool.join()

    time1 = time.time()
    print("总花费时间:{}s".format(time1-time0))
