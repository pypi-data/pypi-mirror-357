# from . import global_values
from .BOMClass import BOM
# from . import config
from .KernelSourceClass import KernelSource
from .ConfigClass import Config
import sys
import logging

# logger = config.setup_logger('kernel-vulns')


def main():
    conf = Config()
    if not conf.get_cli_args():
        sys.exit(1)

    process(conf)
    # config.check_args(args)
    
    sys.exit(0)


def process_kernel_vulns(blackduck_url, blackduck_api_token, kernel_source_file,
                         project, version, logger=None, blackduck_trust_cert=False, folders=False,
                         kernel_comp_name='Linux Kernel'):
    conf = Config()
    conf.bd_url = blackduck_url
    conf.bd_api = blackduck_api_token
    conf.bd_project = project
    conf.bd_version = version
    if logger:
        conf.logger = logger
    else:
        conf.logger = logging
    conf.bd_trustcert = blackduck_trust_cert
    conf.folders = folders
    conf.kernel_source_file = kernel_source_file
    conf.kernel_comp_name = kernel_comp_name

    process(conf)

    return


def process(conf):
    kfiles = KernelSource(conf)
    conf.logger.debug(f"Read {kfiles.count()} source entries from kernel source file "
                      f"'{conf.kernel_source_file}'")

    bom = BOM(conf)
    if bom.check_kernel_comp(conf):
        conf.logger.warn("Linux Kernel not found in project - terminating")
        sys.exit(-1)

    bom.get_vulns(conf)
    conf.logger.info(f"Found {bom.count_vulns()} kernel vulnerabilities from project")

    # bom.print_vulns()
    conf.logger.info("Get detailed data for vulnerabilities")
    bom.process_data_async(conf)

    conf.logger.info("Checking for kernel source file references in vulnerabilities")
    bom.process_kernel_vulns(conf, kfiles)

    conf.logger.info(f"Identified {bom.count_in_kernel_vulns()} in-scope kernel vulns "
                     f"({bom.count_not_in_kernel_vulns()} not in-scope)")

    conf.logger.info(f"Ignored {bom.ignore_vulns_async(conf)} vulns")
    # bom.ignore_vulns()
    conf.logger.info("Done")


if __name__ == '__main__':
    main()
