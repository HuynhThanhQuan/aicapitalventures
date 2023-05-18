"""
"""
import setup_pyaicv
from aicv import tasks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='AI Capital Ventures config',
                        description='Commands to operate all activities of AI Capital Ventures ',
                        epilog='Please DM hthquan28@gmail.com to help')
    parser.add_argument('--task', help='Config file to setup AI Capital Ventures app',type=int)
    args = parser.parse_args()
    
    if args.task == 0:
        tasks.report_TCBS_customer_total_assets()
