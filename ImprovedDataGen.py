from random import seed
from xml.etree.ElementPath import prepare_self

import numpy.random
import pandas as pd
import numpy as np
import scipy.stats as ss
import random
import matplotlib.pyplot as plt
import time
from faker import Faker


STD_CFG  ={ "ability_df": 5,
    "prep_mean": 4.3,
    "prep_sigma": 0.7,
    "quiz_sd": 2.2,
    "quiz_mean": 6,
    "final_mean": 18.3,
    "final_sd": 2.7,
    "usage": False}

TEST_STD_CFG  ={"ability_df": 5,
    "prep_mean": 4.3,
    "prep_sigma": 0.7,
    "quiz_sd": 2.2,
    "quiz_mean": 6,
    "final_mean": 18.3,
    "final_sd": 2.7,
    "usage": True,
    "usage_mean": 3.7 ,
    "usage_sd": 1}


class Student:
    def __init__(self,id, config =STD_CFG ):
        rng = numpy.random.default_rng(abs(hash(id)))
        q1, q2 = ss.t.ppf([0.15, 0.95],config["ability_df"])

        q3, q4 = ss.t.ppf([0.20, 0.95], config["ability_df"])
        self._ability = rng.standard_t(config["ability_df"])
        if self._ability < q3 or self._ability > q4:
            self.usage = 0
        else:
            self.usage = 1
        if (not config["usage"]) or self.usage == 0:
            self.second_quiz = np.clip(np.round((np.clip(
                rng.normal(loc=config["quiz_mean"], scale=config["quiz_sd"]) + 0.2 * self._ability, 0,
                a_max=10).item())),0,10)
            if self._ability < q1 or self._ability > q2:
                self.prep_time = 0
            else:
                self.prep_time = (rng.lognormal(mean=config["prep_mean"], sigma=config[
                    "prep_sigma"]) - self.second_quiz * 0.15 - self._ability * 5)
            self.final_grade = np.clip(np.round(np.clip(rng.normal(loc=config["final_mean"], scale=config[
                "final_sd"]) * 0.67 + 0.95 * self.second_quiz + self.prep_time * 0.035, 0, 30).item()),0,30)
        else:


            self.usage = rng.lognormal(mean=config["usage_mean"], sigma=config[
                    "usage_sd"]) + self._ability *2

            self.second_quiz = np.clip(np.round((np.clip(
                rng.normal(loc=config["quiz_mean"], scale=config["quiz_sd"]) + 0.2 * self._ability, 0,
                a_max=10).item()) + np.log(self.usage)/4),0,10)
            if self._ability < q1 or self._ability > q2:
                self.prep_time = 0
            else:
                self.prep_time = self.usage + (rng.lognormal(mean=config["prep_mean"], sigma=config[
                    "prep_sigma"]) - self.second_quiz * 0.15 - self._ability * 5) * 0.067
            self.final_grade = np.clip(np.round(np.clip(rng.normal(loc=config["final_mean"], scale=config[
                "final_sd"]) * 0.67 + 0.95 * self.second_quiz + (self.prep_time- self.usage) * 0.15 + self.usage * 0.036, 0, 30).item()), 0 , 30)



    def get_ability(self):
        return self._ability

class Experiment:
    def __init__(self,seed, CFG = STD_CFG, TEST_CFG = TEST_STD_CFG ):
        self.seed =seed
        rng = np.random.default_rng(seed)
        Faker.seed(seed)
        n_test = 260 + rng.integers(-10, 10)
        n_control = 260 + np.random.default_rng(seed+99).integers(-10, 10)
        student_ids_test = []
        student_ids_control = []

        for i in range(0, n_test):
            faker = Faker(seed=seed)
            student_ids_test.append(faker.email())

        for i in range(0, n_control):
            faker = Faker(seed=seed + 1)
            student_ids_control.append(faker.email())

        control_data = pd.DataFrame({"id": []})
        control_data["id"] = student_ids_control
        students_obj_control = [Student(i, config = STD_CFG) for
                                i in student_ids_control]
        control_data["second_quiz"] = [st.second_quiz for st in students_obj_control]
        control_data["final_grade"] = [st.final_grade for st in students_obj_control]
        control_data["prep_time"] = [st.prep_time for st in students_obj_control]
        control_data["SECRET!!!!"] = [st.get_ability() for st in students_obj_control]
        control_data["usage"] = [st.usage for st in students_obj_control]
        self.n_control= n_control
        self.control_data = control_data


        test_data = pd.DataFrame({"id": []})
        test_data["id"] = student_ids_test
        students_obj_test = [Student(i, config=TEST_STD_CFG) for
                                i in student_ids_test]
        test_data["second_quiz"] = [st.second_quiz for st in students_obj_test]
        test_data["final_grade"] = [st.final_grade for st in students_obj_test]
        test_data["prep_time"] = [st.prep_time for st in students_obj_test]
        test_data["SECRET!!!!"] = [st.get_ability() for st in students_obj_test]
        test_data["usage"] = [st.usage for st in students_obj_test]
        self.n_test = n_test
        self.test_data = test_data
