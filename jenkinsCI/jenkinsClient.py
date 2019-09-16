#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@contact: tangxiaoyong@bytedance.com
@python_ver: python-2.7
@file: jenkinsClient.py 
@time: 2019/09/16
@software: pycharm
@Description: jenkins url: http://tobci.byted.org/jenkins/view/xiaoyong_view_test/
"""
import json
import xmltodict
from jenkinsLib.jenkinsapi.jenkins import Jenkins


class JenkinsClient(Jenkins):
    '''
        Represents a jenkins environment.
    '''
    JOB_NAME_NOT_EXISTED = "this job is not existed [{}]"
    JOB_NAME_EXISTED = "this job is existed [{}]"
    VIEW_NAME_NOT_EXISTED = "this view is not existed [{}]"
    VIEW_NAME_EXISTED = "this view is existed [{}]"
    PROJECT_IS_DISABLE="this job is disabled [{}]"
    OK = 200

    LIST_VIEW = 'hudson.model.ListView'
    MY_VIEW = 'hudson.model.MyView'
    NESTED_VIEW = 'hudson.plugins.nested_view.NestedView'
    CATEGORIZED_VIEW = 'org.jenkinsci.plugins.categorizedview.CategorizedJobsView'
    DASHBOARD_VIEW = 'hudson.plugins.view.dashboard.Dashboard'
    PIPELINE_VIEW = ('au.com.centrumsystems.hudson.'
                     'plugin.buildpipeline.BuildPipelineView')

    def __init__(self, baseurl,username=None,password=None):
        '''
        :param baseurl: baseurl for jenkins instance including port, str
        :param username: username for jenkins auth, str
        :param password: password for jenkins auth, str
        :return: a Jenkins obj
        '''
        self.username=username
        self.password=password
        self.baseurl = baseurl
        self.jenkinsclient = Jenkins(baseurl=self.baseurl,username=self.username,password=self.password)

    def get_all_view_list(self):
        '''
        :return: Return a list of the names of all views
        '''
        return self.jenkinsclient.views.keys()

    def create_view(self, view_name, view_type=LIST_VIEW):
        '''
        :param view_name: name of new view, str .default:LIST_VIEW
        :param view_type: type of the view, one of the constants in Views, str
        :return: new View obj or None if view was not created
        '''
        if view_name not in self.get_all_view_list():
            return self.jenkinsclient.views.create(view_name=view_name, view_type=view_type)


    def get_view_url(self, view_name="all"):
        '''
        :param view_name: name of  view,str. default:all
        :return: url of view. default:base_url
        '''
        _base_url = self.jenkinsclient.baseurl
        if view_name == "all":
            return _base_url
        else:
            if view_name in self.get_all_view_list():
                _view_url = _base_url + "/view/{}/".format(view_name)
                return _view_url
            else:
                return _base_url

    def delete_view(self, view_name):
        '''
        :param view_name: name of  view
        :return: true/false/error msg
        '''
        if view_name in self.get_all_view_list():
            _base_url = self.jenkinsclient.baseurl
            _view_url = _base_url + "/view/{}/".format(view_name)
            _view_obj = self.jenkinsclient.get_view_by_url(str_view_url=_view_url)
            _view_obj.delete()
            return _view_obj.deleted
        else:
            return self.VIEW_NAME_NOT_EXISTED.format(view_name)

    def get_job_names(self, view_name="all"):
        '''
        view_name:name of view . default:all
        :return: Return a list of the names of all jobs
        '''
        job_names = list()
        if view_name == "all":
            _job_iterate = self.jenkinsclient.get_jobs()
            for ite in _job_iterate:
                job_names.append(ite[0])
            return job_names
        else:
            if view_name in self.get_all_view_list():
                _base_url = self.jenkinsclient.baseurl
                _view_url = _base_url + "/view/{}/".format(view_name)
                jobs_dic = self.jenkinsclient.get_view_by_url(_view_url).get_job_dict()
                for _job_name, _job_url in jobs_dic.items():
                    job_names.append(_job_name)
                return job_names
            else:
                return job_names

    def check_job_existed(self, job_name):
        '''
        :param job_name: job name
        :return: True/false
        '''
        if job_name in self.get_job_names():
            return True
        return False

    def copy_job(self, old_job_name, new_job_name, view_name="all"):
        '''
        :param old_job_name:Name of an existing job
        :param new_job_name:Name of new job
        :param view_name: view name of job . default:all
        :return: (job_name,view_name) or (error_msg,view_name)
        '''
        if old_job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(old_job_name), view_name

        if new_job_name in self.get_job_names():
            return self.JOB_NAME_EXISTED.format(new_job_name), view_name

        if view_name != "all" and (view_name not in self.get_all_view_list()):
            return self.VIEW_NAME_NOT_EXISTED.format(view_name), view_name

        _ret_new_job_name = self.jenkinsclient.copy_job(jobname=old_job_name, newjobname=new_job_name)
        if view_name != "all" and _ret_new_job_name.name == new_job_name:
            _view_url = self.get_view_url(view_name)
            self.jenkinsclient.get_view_by_url(_view_url).add_job(job_name=new_job_name)
        return _ret_new_job_name.name, view_name

    def add_job_to_view(self, job_name, view_name):
        '''
        :param job_name: Name of an existing job
        :param view_name: Name of an existing view
        :return: True/false/error msg
        '''
        if view_name == "all":
            return True

        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        if view_name != "all" and (view_name not in self.get_all_view_list()):
            return self.VIEW_NAME_NOT_EXISTED.format(view_name)

        if view_name != "all":
            _view_url = self.get_view_url(view_name)
            return self.jenkinsclient.get_view_by_url(_view_url).add_job(job_name=job_name)

    def get_job_xml_conf(self, job_name):
        '''
        :param job_name: Name of an existing job
        :return: the config.xml from the job / error msg
        '''

        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        _ret_xml_conf = self.jenkinsclient.get_job(job_name).get_config()
        return _ret_xml_conf

    def get_job_jsonStr_conf(self, job_name):
        '''
        :param job_name: Name of an existing job
        :return: json_str /error msg
        '''
        _xml_conf = self.get_job_xml_conf(job_name)

        if _xml_conf == self.JOB_NAME_NOT_EXISTED.format(job_name):
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        _dict_val = xmltodict.parse(xml_input=_xml_conf, encoding='utf-8')
        _ret_json_format_str = json.dumps(_dict_val, indent=4)
        return _ret_json_format_str

    def jsonConf_to_xmlConf(self, job_conf_json_str):
        '''
        :param job_conf_json_str: json configuration of new job.
        :return: xml format
        '''
        try:
            _json_dict = json.loads(job_conf_json_str)
        except Exception, e:
            return None
        _ret_xml_conf = xmltodict.unparse(input_dict=_json_dict)
        return _ret_xml_conf

    def update_job(self, jobname, xml_conf):
        '''

        create job or update configuration of an existing job

        :param jobname: name of new job, str
        :param xml_conf: configuration of new job, xml
        :return: new Job obj
        '''

        _ret_job_obj = self.jenkinsclient.create_job(jobname=jobname, xml=xml_conf)
        return _ret_job_obj

    def invoke_job(self, job_name):
        '''
        :param job_name: Name of an existing job
        :return:true/false/error msg
        '''
        _start_job_build_num=0
        if len(self.jenkinsclient.get_job(job_name).get_build_dict().keys())!=0:
            _start_job_build_num = self.jenkinsclient.get_job(job_name).get_last_buildnumber()

        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        if not self.job_is_enable(job_name):
            return self.PROJECT_IS_DISABLE.format(job_name)

        self.jenkinsclient.get_job(job_name).invoke(block=True)

        _end_job_build_num = self.jenkinsclient.get_job(job_name).get_last_buildnumber()

        if _end_job_build_num - _start_job_build_num >= 1:
            return True
        else:
            return False

    def stop_job_build(self, job_name, build_num=0):
        '''
        :param job_name: Name of an existing job
        :param build_num: build number of a job. default:last build number
        :return: true/false/error msg
        '''

        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        if build_num <= 0:
            build_num = self.jenkinsclient.get_job(job_name).get_last_buildnumber()

        _ret_val = self.jenkinsclient.get_job(job_name).get_build(build_num).stop()

        return _ret_val

    def job_is_running(self, job_name):
        '''
        :param job_name: Name of an existing job
        :return:true/false/error msg
        '''
        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        return self.jenkinsclient.get_job(job_name).is_running()

    def get_job_console(self, job_name, build_num=0):
        '''
        :param job_name: Name of an existing job
        :param build_num: build number of a job . default:last build number
        :return:Return the current state of the text console
        '''

        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        _ret_content = ""

        if build_num <= 0:
            build_num = self.jenkinsclient.get_job(job_name).get_last_buildnumber()

        _ret_content = self.jenkinsclient.get_job(job_name).get_build(build_num).get_console()

        return _ret_content

    def job_is_enable(self, job_name):
        '''
        :param job_name: Name of an existing job
        :return: true/false/error msg
        '''
        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        _ret_val = self.jenkinsclient.get_job(job_name).is_enabled()
        return _ret_val

    def enable_job(self, job_name):
        '''
        :param job_name:Name of an existing job
        :return:true/false/error msg
        '''
        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        if self.job_is_enable(job_name):
            return True

        _resp = self.jenkinsclient.get_job(job_name).enable()
        if _resp.status_code == self.OK:
            return True
        return False

    def disable_job(self, job_name):
        '''
        :param job_name: Name of an existing job
        :return: true/false/error msg
        '''

        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        if not self.job_is_enable(job_name):
            return True

        _resp = self.jenkinsclient.get_job(job_name).disable()
        if _resp.status_code == self.OK:
            return True
        return False

    def delete_job(self, job_name):
        '''
        :param job_name: name of a exist job, str
        :return: True/false/error msg
        '''

        if self.check_job_existed(job_name):
            self.jenkinsclient.delete_job(job_name)
            if self.check_job_existed(job_name):
                return False
            else:
                return True
        return True

    def delete_build(self, job_name, build_num=0):
        '''
        :param job_name: Name of an existing job
        :param build_num: build number of a job. default:last build number
        :raises NotFound:           When build is not found
        :return: true/false/error msg
        '''
        if job_name not in self.get_job_names():
            return self.JOB_NAME_NOT_EXISTED.format(job_name)

        if build_num <= 0:
            build_num = self.jenkinsclient.get_job(job_name).get_last_buildnumber()

        _build_nums_list = self.jenkinsclient.get_job(job_name).get_build_dict().keys()

        if build_num not in _build_nums_list:
            return True

        try:
            self.jenkinsclient.get_job(job_name).delete_build(build_num)
        except Exception, e:
            return False
        return True


