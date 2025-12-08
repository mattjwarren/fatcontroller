import os
#Currently chnges here need reflecting in unixsetup.sh
system_install_root='H:/Documents/dev/git_repos/fatcontroler/'
install_root='fatcontroler'
install_name='fatcontroler'
data_name='data'
log_file='logs.txt'

data_path=os.path.join(system_install_root,
                       install_root,
                       install_name,
                       data_name)

