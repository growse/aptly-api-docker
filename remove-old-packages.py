#!/usr/bin/env python3

# From https://github.com/aptly-dev/aptly/issues/291#issuecomment-276404030

import argparse
import re
import sys
from time import sleep
from typing import List

from apt_pkg import version_compare, init_system
from subprocess import check_output, CalledProcessError
from functools import cmp_to_key
from tqdm import tqdm


class PurgeOldVersions:
    def __init__(self):
        self.args = self.parse_arguments()

        if self.args.dry_run:
            print("Run in dry mode, without actually deleting the packages.")
        if not self.args.repo:
            sys.exit("You must declare a repository with: --repo")

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            help="List packages to remove without removing " "them.",
            action="store_true",
        )
        parser.add_argument(
            "--repo", dest="repo", help="Which repository should be searched?", type=str, default="defaultrepo"
        )
        parser.add_argument(
            "--package-query",
            dest="package_query",
            help="Which packages should be removed?\n"
            "e.g.\n"
            "  - Single package: ros-indigo-rbdl.\n"
            "  - Query: 'Name (%% ros-indigo-*)' "
            "to match all ros-indigo packages. See \n"
            "https://www.aptly.info/doc/feature/query/",
            type=str,
            default="",
        )
        parser.add_argument(
            "-n",
            "--retain-how-many",
            dest="retain_how_many",
            help="How many package versions should be kept?",
            type=int,
            default=1,
        )
        return parser.parse_args()

    def get_packages(self) -> List[str]:
        init_system()

        packages = []

        try:
            output: bytes = check_output(
                ["aptly", "repo", "search", self.args.repo, self.args.package_query]
                if self.args.package_query
                else ["aptly", "repo", "search", self.args.repo]
            )

            packages = sorted(
                set(
                    map(
                        lambda p: re.sub(
                            "[_](\d{1,}[:])?\d{1,}[.]\d{1,}[.]\d{1,}[-](.*)", "", p
                        ),
                        [line for line in output.decode().split("\n") if len(line) > 0],
                    )
                )
            )

        except CalledProcessError as e:
            print(e)

        finally:
            return packages

    def purge(self) -> None:
        packages = self.get_packages()
        if not packages:
            sys.exit("No packages to remove.")
        else:
            print(f"{len(packages)} package names to look at: {','.join(packages)}")

        packages_to_remove: List[str] = []
        for package in packages:
            try:
                output = check_output(
                    ["aptly", "repo", "search", self.args.repo, package]
                )

                def sort_by_version_cmp(name1, name2):
                    version_and_build_1 = name1.split("_")[1]
                    version_and_build_2 = name2.split("_")[1]
                    return version_compare(version_and_build_1, version_and_build_2)

                packages_to_remove.extend(
                    sorted(
                        [line for line in output.decode().split("\n") if len(line) > 0],
                        key=cmp_to_key(sort_by_version_cmp),
                    )[: -self.args.retain_how_many]
                )

            except CalledProcessError as e:
                print(e)

        if len(packages_to_remove) > 0:
            print(f"Removing {len(packages_to_remove)} packages in total")
            with tqdm(total=len(packages_to_remove)) as pbar:
                for package in packages_to_remove:
                    pbar.set_description(package)
                    if not self.args.dry_run:
                        check_output(
                            ["aptly", "repo", "remove", self.args.repo, package]
                        )
                    else:
                        sleep(0.1)
                    pbar.update(1)
            check_output(["aptly", "db", "cleanup"])
        else:
            print("No packages to remove")


if __name__ == "__main__":
    purge_old_versions = PurgeOldVersions()
    purge_old_versions.purge()
