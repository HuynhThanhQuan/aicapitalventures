"""
"""


import setup_pyaicv


def run_TCBS_report():
    from aicv import tasks
    tasks.report_TCBS_customer_total_assets()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='AI Capital Ventures config',
                        description='Commands to operate all activities of AI Capital Ventures ',
                        epilog='Please DM hthquan28@gmail.com to help')
    parser.add_argument('--choose_task', help='Config file to setup AI Capital Ventures app',type=str)
    args = parser.parse_args()
 