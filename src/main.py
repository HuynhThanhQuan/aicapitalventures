import aicv


if __name__=='__main__':
    # print(os.environ.get('AICV'))
    # print(os.environ['AICV_KEY_GDRIVE_CRED'])
    # print(os.environ['AICV_KEY_GDRIVE_TOKEN'])
    # print(credential.get_read_only_credentials())
    # cred = credential.get_read_only_credentials()
    # print(cred, cred.token)
    # print(cred.scopes)
    # cred = credential.get_edit_credentials()
    # print(cred, cred.token)
    # print(cred.scopes)
    
    # print(gdrive.search_transaction_history_files())
    # print(gdrive.download_TCBS_transaction_history())
    # f = tcbs.list_TCBS_transaction_history()[0]
    # df = tcbs.get_latest_transaction_table()
    # print(df)
    # print(gdrive.search_verified_records())
    print(tcbs.export_verified_records())
    aicv.run()