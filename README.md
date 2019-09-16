#  jenkins CI sdk

##  一：Example
```python
#!/usr/bin/env python  
#-*- coding:utf-8 _*-  
""" 
@contact: tangxiaoyong@bytedance.com
@python_ver: python-2.7
@file: demo.py 
@time: 2019/09/16
@software: pycharm
@Description:
"""
from jenkinsCI.jenkinsClient import JenkinsClient


if __name__=="__main__":

    ##实例化一个jenkins对象
    jenkins=JenkinsClient("http://server-host/jenkins/",username,password)

    view_name="test_demo"
    view_name1="test_demo1"
    ##创建view视图
    view_ret=jenkins.create_view(view_name=view_name)
    view_ret1 = jenkins.create_view(view_name=view_name1)
    print view_ret
    print view_name1

    ##删除view视图
    del_view=jenkins.delete_view(view_name1)
    print del_view

    ##创建jenkins job
    job_ret=jenkins.copy_job(old_job_name='xiaoyong-test',new_job_name='new_job_name',view_name="test_demo")
    print job_ret

    ##build job(执行job)
    exec_job=jenkins.invoke_job("new_job_name")
    print exec_job

    ##获取job console log
    contents=jenkins.get_job_console("new_job_name")
    print contents

    ##
    
```



## 二：API

> ###  please see the [API](https://github.com/xiaoyongtang/jenkinsCISDK/blob/master/jenkinsCIAPI.png)


***


## 三：more information
> ### for further information,please see the [code](https://github.com/xiaoyongtang/jenkinsCISDK/blob/master/jenkinsCI/jenkinsClient.py)

***
