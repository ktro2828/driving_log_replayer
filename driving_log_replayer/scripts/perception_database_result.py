#!/usr/bin/env python3

# Copyright (c) 2021 TIER IV.inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import glob
import os

from perception_eval.tool import PerceptionAnalyzer3D
import simplejson as json


class PerceptionLoadDatabaseResult:
    def __init__(self, result_root_directory, scenario_path):
        analyzer = PerceptionAnalyzer3D.from_scenario(
            result_root_directory,
            scenario_path,
        )
        regex = os.path.join(result_root_directory, "**", "scene_result.pkl")
        pickle_file_paths = glob.glob(regex, recursive=True)
        for filepath in pickle_file_paths:
            analyzer.add_from_pkl(filepath)
        score_df, error_df = analyzer.analyze()

        score_dict = score_df.to_dict()
        error_dict = error_df.groupby(level=0).apply(lambda df: df.xs(df.name).to_dict()).to_dict()
        database_metrics = {"Score": score_dict, "Error": error_dict}

        result_file_path = os.path.join(result_root_directory, "database_result.json")

        with open(result_file_path, "w") as f:
            json.dump(database_metrics, f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--result_root_directory",
        required=True,
        help="root directory of result",
    )
    parser.add_argument(
        "-s",
        "--scenario_path",
        required=True,
        help="path of the scenario to load evaluator settings",
    )
    args = parser.parse_args()
    database_result = PerceptionLoadDatabaseResult(
        os.path.expandvars(args.result_root_directory), os.path.expandvars(args.scenario_path)
    )
    database_result


if __name__ == "__main__":
    main()
