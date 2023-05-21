"""
"""
import argparse

import setup_pyaicv
from aicv import tasks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='AI Capital Ventures config',
                        description='Commands to operate all activities of AI Capital Ventures ',
                        epilog='Please DM hthquan28@gmail.com to help')
    parser.add_argument('task', help='Config file to setup AI Capital Ventures app',type=int)
    parser.add_argument('--customer_name', help='Config file to setup AI Capital Ventures app',type=str)
    args = parser.parse_args()
    
    if args.task == 0:
        tasks.upload_TCBS_reviewed_data()
    elif args.task == 1:
        tasks.get_TCBS_summary_report()
    elif args.task == 2:
        tasks.get_TCBS_customer_report(args.customer_name)
