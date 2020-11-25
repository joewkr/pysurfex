import unittest
import scheduler
import os
import time
import re


class EcflowTest(unittest.TestCase):

    @staticmethod
    def _create_exp(wd):
        os.makedirs(wd, exist_ok=True)
        argv = [
            "setup",
            "--wd", wd,
            "-rev", wd,
            "-conf", os.getcwd(),
            "-host", "unittest",
            "--domain_file", "test/settings/conf_proj_test.json"
        ]
        kwargs = scheduler.parse_surfex_script(argv)
        scheduler.surfex_script(**kwargs)

    def test_start_and_run(self):
        exp = "test_start_and_run"
        wd = "/tmp/host0/hm_wd/" + exp
        self._create_exp(wd)

        if not os.path.islink("/tmp/host1/job/" + exp):
            os.makedirs("/tmp/host1/job/", exist_ok=True)
            os.symlink("/tmp/host0/job/" + exp, "/tmp/host1/job/" + exp)


        # Dry submit
        argv = [
            "-exp", exp,
            "-lib", wd,
            "-ecf_name", exp + "/dry_submit",
            "-ecf_pass", "12345",
            "-ecf_tryno", "1"
        ]
        print(argv)
        kwargs = scheduler.parse_submit_cmd(argv, exp=True)
        kwargs.update({"dry_run": True})
        scheduler.submit_cmd_exp(**kwargs)

        argv = [
            "start",
            "--wd", wd,
            "-dtg", "2020111303",
            "-dtgend", "2020111306",
            "--suite", "unittest"
        ]
        kwargs = scheduler.parse_surfex_script(argv)
        # kwargs.update({"begin": False})
        scheduler.surfex_script(**kwargs)

        # Test if init run has synced
        test_file = wd + "/experiment_is_locked"
        test_file = "/tmp/host1/scratch/hm_home/" + exp + "/unittest_ok"
        found = False
        for t in range(0, 15):
            print(t)
            if os.path.exists(test_file):
                found = True
                break
            time.sleep(1)
        if not found:
            raise FileNotFoundError(test_file + " not found!")

        test_file = "/tmp/host1/scratch/hm_home/" + exp + "/SleepingBeauty"
        found = False
        for t in range(0, 15):
            print(t)
            if os.path.exists(test_file):
                found = True
                break
            time.sleep(1)
        if not found:
            raise FileNotFoundError(test_file + " not found!")

        ecf_name = None
        ecf_pass = None
        ecf_tryno = None
        ecf_rid = None
        submission_id = None

        '''
        job_file = "/tmp/host1/job/" + exp + "/SleepingBeauty.job1"
        for line in open(job_file):
            for match in re.finditer("^ecf_name = ", line):
                print(match)
                print(line)
                ecf_name = line.split()[2].replace('"', '')
            for match in re.finditer("^ecf_pass = ", line):
                ecf_pass = line.split()[2].replace('"', '')
            for match in re.finditer("^ecf_tryno = ", line):
                ecf_tryno = line.split()[2].replace('"', '')
            for match in re.finditer("^ecf_rid = ", line):
                ecf_rid = line.split()[2].replace('"', '')
            for match in re.finditer("^submission_id = ", line):
                submission_id = line.split()[2].replace('"', '')
        '''

        # Find sleeping beauty information from job file
        sfx_exp = scheduler.ExpFromFiles(exp, wd)
        sfx_exp.server.ecf_client.sync_local()
        defs = sfx_exp.server.ecf_client.get_defs()
        for item in defs.suites:
            for node in item:
                n = node.get_abs_node_path()
                print(n)
                if n == "/" + exp + "/SleepingBeauty":
                    print("There she is")
                    ecf_name = node.find_gen_variable("ECF_NAME").value()
                    ecf_tryno = node.find_gen_variable("ECF_TRYNO").value()
                    ecf_pass = node.find_gen_variable("ECF_PASS").value()
                    ecf_rid = node.find_gen_variable("ECF_RID").value()
                    submission_id = node.find_variable("SUBMISSION_ID").value()
                    print(ecf_name)
                    print(submission_id)

        argv = [
            "-exp", exp,
            "-lib", "/tmp/host1/scratch/hm_home/" + exp + "/lib",
            "-ecf_name", ecf_name,
            "-ecf_pass", ecf_pass,
            "-ecf_tryno", ecf_tryno,
            "-ecf_rid", ecf_rid,
            "-submission_id", submission_id
        ]
        print(argv)
        kwargs = scheduler.parse_status_cmd(argv, exp=True)
        scheduler.status_cmd_exp(**kwargs)

        kwargs = scheduler.parse_kill_cmd(argv, exp=True)
        scheduler.kill_cmd_exp(**kwargs)

        test_file = "/tmp/host1/scratch/hm_home/" + exp + "/SleepingBeauty2"
        found = False
        for t in range(0, 15):
            print(t)
            if os.path.exists(test_file):
                found = True
                break
            time.sleep(1)
        if not found:
            raise FileNotFoundError(test_file + " not found!")

    def test_create_surfex(self):
        exp = "test_create_surfex"
        wd = "/tmp/host0/hm_wd/" + exp
        self._create_exp(wd)

        if not os.path.islink("/tmp/host1/job/" + exp):
            os.makedirs("/tmp/host1/job/", exist_ok=True)
            os.symlink("/tmp/host0/job/" + exp, "/tmp/host1/job/" + exp)

        argv = [
            "start",
            "--wd", wd,
            "-dtg", "2020111303",
            "-dtgend", "2020112319",
        ]
        kwargs = scheduler.parse_surfex_script(argv)
        kwargs.update({"begin": False})
        scheduler.surfex_script(**kwargs)

    # TODO
    def test_parse_surfex_definition(self):
        pass
